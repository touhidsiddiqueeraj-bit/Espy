from __future__ import annotations
import time
import logging
from typing import Optional

from PyQt6.QtCore import QThread, pyqtSignal

from models import Device
from constants import CACHE_FILE, OTA_PORT
from discovery.mdns import HeartbeatListener, mdns_discover
from discovery.cache import load_cache, save_cache, check_cached_ip
from discovery.arp import arp_scan
from discovery.usb import usb_probe
from espy_logging import get_logger

_log = get_logger("discovery.engine")


class DiscoveryEngine(QThread):
    """Coordinates device discovery.

    Primary mechanism: a persistent HeartbeatListener that catches every
    UDP broadcast from ESP32 devices (they broadcast every 5s).

    Secondary mechanisms (run on a slower cadence):
      - Cached-IP probe — quickly re-find devices we've seen before
      - ARP scan — find devices that aren't broadcasting yet but are
        running the OTA HTTP server

    All errors are logged AND emitted via the `status` signal so the UI
    can show them. Previously every `except Exception: pass` swallowed
    errors silently, leaving the user stuck on "No devices found".
    """
    found          = pyqtSignal(str, str, int)   # name, ip, port
    lost           = pyqtSignal(str)             # name
    phase_changed  = pyqtSignal(str)             # human-readable phase
    status         = pyqtSignal(str, str)        # level, message
    done           = pyqtSignal()

    def __init__(self) -> None:
        super().__init__()
        self._running = False
        self._known: dict[str, Device] = {}
        self._cache: dict = {}
        self._scan_interval = 12
        self._wake = False

        # Persistent heartbeat listener — primary discovery mechanism.
        self._heartbeat: Optional[HeartbeatListener] = None

    # ──────────────────────────────────────────────────────────
    #  Thread lifecycle
    # ──────────────────────────────────────────────────────────

    def run(self) -> None:
        self._running = True
        self._cache = load_cache()
        _log.info("DiscoveryEngine started. Cache: %d devices.",
                  len(self._cache))

        # Restore cached devices so the UI isn't empty on first launch.
        for name, data in self._cache.items():
            try:
                dev = Device.from_cache(data)
                self._known[name] = dev
                self.found.emit(name, dev.last_known_ip, dev.port)
            except Exception as e:
                _log.warning("Failed to restore cached device %r: %s", name, e)

        # Start the persistent heartbeat listener (primary mechanism).
        self._heartbeat = HeartbeatListener()
        self._heartbeat.heartbeat.connect(self._on_heartbeat_packet)
        self._heartbeat.status.connect(self._forward_status)
        self._heartbeat.start()

        # Secondary scan loop: cached-IP probe + ARP fallback.
        # These run on a slower cadence to catch devices that aren't
        # broadcasting heartbeats yet (e.g. just booted, or running
        # an older firmware without heartbeat support).
        while self._running:
            if not self._had_recent_activity():
                # Phase 2: cached IP probe — fast, targets known devices.
                self.phase_changed.emit("Checking known devices…")
                self._probe_cached_ips()

            if not self._had_recent_activity():
                # Phase 3: ARP scan — slow, scans the whole /24 subnet.
                self.phase_changed.emit("Scanning network for devices…")
                self._arp_scan_once()

            # Re-find stale devices — the old code had a `pass` stub here.
            self._refind_stale_devices()

            # Prune stale devices that we still couldn't reach.
            self._prune_stale()

            self._save_cache()

            # Sleep in 0.5s chunks so request_scan() can wake us up.
            for _ in range(self._scan_interval * 2):
                if not self._running:
                    break
                if self._wake:
                    self._wake = False
                    _log.debug("Scan woken up early by request_scan().")
                    break
                time.sleep(0.5)

        # Tear down the heartbeat listener cleanly.
        if self._heartbeat is not None:
            try:
                self._heartbeat.stop()
            except Exception as e:
                _log.warning("Error stopping HeartbeatListener: %s", e)
            self._heartbeat = None

        self._save_cache()
        self.done.emit()
        _log.info("DiscoveryEngine stopped.")

    def request_scan(self) -> None:
        """Wake the scan loop early (user clicked 'Rescan')."""
        _log.info("Rescan requested by user.")
        self._wake = True
        # Also restart the heartbeat listener in case it died on a bind error.
        if self._heartbeat is not None and not self._heartbeat.isRunning():
            _log.info("HeartbeatListener not running; restarting.")
            self._heartbeat.start()

    def stop(self) -> None:
        self._running = False
        self._wake = True  # wake the scan loop so it notices _running=False
        if self._heartbeat is not None:
            try:
                self._heartbeat.stop()
            except Exception as e:
                _log.warning("Error stopping HeartbeatListener during shutdown: %s", e)
        self.wait(5000)

    # ──────────────────────────────────────────────────────────
    #  Heartbeat listener callback
    # ──────────────────────────────────────────────────────────

    def _on_heartbeat_packet(self, name: str, ip: str, port: int) -> None:
        """Called by HeartbeatListener for every valid heartbeat."""
        self._upsert_device(name, ip, port)

    def _forward_status(self, level: str, message: str) -> None:
        """Forward heartbeat-listener status to the UI."""
        self.status.emit(level, message)

    # ──────────────────────────────────────────────────────────
    #  Discovery sub-phases
    # ──────────────────────────────────────────────────────────

    def _probe_cached_ips(self) -> None:
        """Quick TCP connect to each cached IP:port. Fast, no scanning."""
        for name, data in list(self._cache.items()):
            if not self._running:
                return
            ip = data.get("last_known_ip", "")
            port = data.get("port", OTA_PORT)
            if not ip:
                continue
            try:
                if check_cached_ip(ip, port):
                    self._upsert_device(name, ip, port)
            except Exception as e:
                _log.debug("Cached IP probe failed for %s @ %s:%d: %s",
                           name, ip, port, e)

    def _arp_scan_once(self) -> None:
        """Scan the local /24 subnet for the OTA HTTP server."""
        try:
            arp_results = arp_scan(timeout=4)
        except Exception as e:
            # The old code did `except Exception: pass` here, swallowing
            # every error. Log it instead so users can diagnose.
            _log.warning("ARP scan failed: %s", e)
            return
        for ip, name in arp_results:
            self._upsert_device(name, ip, OTA_PORT)

    def _refind_stale_devices(self) -> None:
        """Try to re-find devices that have gone stale.

        The old code had `# Try to re-find stale devices / pass` — a
        stub that did nothing. This implementation does a quick TCP
        connect to each stale device's last known IP:port; if it
        responds, we mark it seen again.
        """
        stale_names = [n for n, d in self._known.items() if d.is_stale]
        for name in stale_names:
            if not self._running:
                return
            dev = self._known[name]
            try:
                if check_cached_ip(dev.ip, dev.port):
                    _log.info("Re-found stale device %s @ %s:%d",
                              name, dev.ip, dev.port)
                    self._upsert_device(name, dev.ip, dev.port)
            except Exception as e:
                _log.debug("Re-find probe failed for %s: %s", name, e)

    def _prune_stale(self) -> None:
        """Drop devices we haven't heard from in DEVICE_STALE_TIMEOUT seconds."""
        stale = [n for n, d in self._known.items() if d.is_stale]
        for name in stale:
            _log.info("Device %s went stale (no heartbeat for %ds).",
                      name, int(time.time() - self._known[name].last_seen))
            del self._known[name]
            self.lost.emit(name)

    # ──────────────────────────────────────────────────────────
    #  Helpers
    # ──────────────────────────────────────────────────────────

    def _upsert_device(self, name: str, ip: str, port: int) -> None:
        now = time.time()
        if name in self._known:
            d = self._known[name]
            ip_changed = d.ip != ip
            port_changed = d.port != port
            d.ip = ip
            d.port = port
            d.last_seen = now
            d.last_known_ip = ip
            if ip_changed or port_changed:
                _log.info("Device %s changed address → %s:%d", name, ip, port)
        else:
            d = Device(name, ip, port)
            self._known[name] = d
            _log.info("New device discovered: %s @ %s:%d", name, ip, port)
            self.found.emit(name, ip, port)

        # Update cache so we can find this device quickly next launch.
        if name not in self._cache:
            self._cache[name] = d.to_cache()
        else:
            self._cache[name]["last_known_ip"] = ip
            self._cache[name]["port"] = port
            self._cache[name]["last_seen"] = now

    def _had_recent_activity(self) -> bool:
        """True if any device has been seen in the last 8 seconds."""
        now = time.time()
        for d in self._known.values():
            if now - d.last_seen < 8:
                return True
        return False

    def _save_cache(self) -> None:
        try:
            save_cache(self._cache)
        except Exception as e:
            _log.warning("Failed to save discovery cache: %s", e)
