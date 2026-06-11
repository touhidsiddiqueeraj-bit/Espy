from __future__ import annotations
import time
import json
import threading
from typing import Optional, Callable
from PyQt6.QtCore import QThread, pyqtSignal

from models import Device
from constants import CACHE_FILE, OTA_PORT
from discovery.mdns import mdns_discover
from discovery.cache import load_cache, save_cache, check_cached_ip
from discovery.arp import arp_scan
from discovery.usb import usb_probe


class DiscoveryEngine(QThread):
    found = pyqtSignal(str, str, int)
    lost = pyqtSignal(str)
    phase_changed = pyqtSignal(str)
    done = pyqtSignal()

    def __init__(self):
        super().__init__()
        self._running = False
        self._known: dict[str, Device] = {}
        self._cache: dict = {}
        self._scan_interval = 12

    def run(self):
        self._running = True
        self._cache = load_cache()

        # Restore cached devices
        for name, data in self._cache.items():
            dev = Device.from_cache(data)
            self._known[name] = dev
            self.found.emit(name, dev.last_known_ip, dev.port)

        while self._running:
            for device_name, device in list(self._known.items()):
                if device.is_stale:
                    # Try to re-find stale devices
                    pass

            # Phase 1: mDNS
            self.phase_changed.emit("Looking for devices on Wi-Fi...")
            mdns_results = mdns_discover(timeout=1.5)
            for name, ip, port in mdns_results:
                self._upsert_device(name, ip, port)

            if not self._had_recent_activity():
                # Phase 2: cached IP
                self.phase_changed.emit("Checking known devices...")
                for name, data in list(self._cache.items()):
                    ip = data.get("last_known_ip", "")
                    if ip and check_cached_ip(ip, data.get("port", OTA_PORT)):
                        self._upsert_device(name, ip, data.get("port", OTA_PORT))

            if not self._had_recent_activity():
                # Phase 3: ARP scan
                self.phase_changed.emit("Scanning network for devices...")
                try:
                    arp_results = arp_scan(timeout=4)
                    for ip, name in arp_results:
                        self._upsert_device(name, ip, OTA_PORT)
                except Exception:
                    pass

            # Prune stale
            stale = [n for n, d in self._known.items() if d.is_stale]
            for name in stale:
                del self._known[name]
                self.lost.emit(name)

            self._save_cache()

            # Wait before next scan cycle
            for _ in range(self._scan_interval * 2):
                if not self._running:
                    break
                time.sleep(0.5)

        self._save_cache()

    def stop(self):
        self._running = False
        self.wait()

    def _upsert_device(self, name: str, ip: str, port: int):
        now = time.time()
        if name in self._known:
            d = self._known[name]
            d.ip = ip
            d.port = port
            d.last_seen = now
        else:
            d = Device(name, ip, port)
            self._known[name] = d
            self.found.emit(name, ip, port)
        # Update cache
        if name not in self._cache:
            self._cache[name] = d.to_cache()
        else:
            self._cache[name]["last_known_ip"] = ip
            self._cache[name]["last_seen"] = now

    def _had_recent_activity(self) -> bool:
        now = time.time()
        for d in self._known.values():
            if now - d.last_seen < 8:
                return True
        return False

    def _save_cache(self):
        save_cache(self._cache)
