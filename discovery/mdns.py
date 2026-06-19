"""UDP heartbeat discovery for Espy.

This module exposes two things:

  1. `mdns_discover(timeout)` — a one-shot synchronous listener that
     collects heartbeat packets for `timeout` seconds. Used by the
     DiscoveryEngine as a fallback / probe.

  2. `HeartbeatListener` — a persistent QThread that runs continuously
     and emits a Qt signal every time a heartbeat arrives. This is the
     primary discovery mechanism: ESP32 devices broadcast every 5s, so
     a persistent listener catches every broadcast, not just the ones
     that happen to land inside a 1.5s window.

Both used to share the same set of bugs:
  - 512-byte recv buffer truncated verbose JSON → silent drop
  - `except Exception: pass` swallowed bind/parse errors with no log
  - No SO_BROADCAST → broadcast packets filtered on some Windows hosts
  - No bind retry → one transient port-in-use failure killed discovery
  - No way to surface errors to the UI

All of those are fixed below.
"""
from __future__ import annotations
import json
import socket
import time
import logging
from typing import Optional

from PyQt6.QtCore import QThread, pyqtSignal

from constants import HEARTBEAT_PORT, OTA_PORT
from espy_logging import get_logger

_log = get_logger("discovery.mdns")

# Tuning constants — exported so tests / advanced users can override.
RECV_BUFFER = 4096            # was 512 — too small for verbose JSON
BIND_RETRY_DELAY = 1.5        # seconds between bind retries
BIND_MAX_RETRIES = 5          # give up after this many consecutive failures
LISTEN_TIMEOUT = 0.5          # socket select timeout — keeps stop() responsive


def _make_listening_socket() -> tuple[Optional[socket.socket], Optional[str]]:
    """Create a UDP socket bound to HEARTBEAT_PORT.

    Returns (sock, error_message). On success error_message is None.
    Sets SO_REUSEADDR + SO_BROADCAST, which the old code didn't do.
    """
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        # SO_BROADCAST is required for *sending* broadcasts on all platforms
        # and for *receiving* them on a handful of Windows configurations.
        try:
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        except OSError as e:
            # Not fatal — log and continue.
            _log.warning("SO_BROADCAST not settable: %s", e)
        sock.bind(("", HEARTBEAT_PORT))
        sock.settimeout(LISTEN_TIMEOUT)
        return sock, None
    except OSError as e:
        return None, f"{e.__class__.__name__}: {e}"


def _parse_heartbeat(data: bytes, addr: tuple) -> Optional[tuple[str, str, int]]:
    """Parse one heartbeat packet.

    Returns (name, ip, port) on success, or None on any error.
    Logs every failure with the raw bytes so it's diagnosable.
    """
    ip = addr[0]
    try:
        text = data.decode("utf-8")
        payload = json.loads(text)
    except (UnicodeDecodeError, json.JSONDecodeError) as e:
        _log.warning("Malformed heartbeat from %s (%s): %r",
                     ip, e, data[:200])
        return None

    if not isinstance(payload, dict):
        _log.warning("Heartbeat from %s is not a JSON object: %r", ip, payload)
        return None

    name = payload.get("device") or "Unknown"
    try:
        port = int(payload.get("ota_port", OTA_PORT))
    except (TypeError, ValueError):
        _log.warning("Heartbeat from %s has bad ota_port=%r; using default %d",
                     ip, payload.get("ota_port"), OTA_PORT)
        port = OTA_PORT

    _log.debug("Heartbeat from %s @ %s:%d payload=%s", name, ip, port, payload)
    return name, ip, port


def mdns_discover(timeout: float = 1.5) -> list[tuple[str, str, int]]:
    """One-shot synchronous heartbeat listener.

    Listens for `timeout` seconds, returns deduplicated (name, ip, port)
    tuples. Used as a probe/fallback by DiscoveryEngine. The persistent
    `HeartbeatListener` below is the primary discovery mechanism.
    """
    results: list[tuple[str, str, int]] = []
    sock, err = _make_listening_socket()
    if sock is None:
        _log.error("mdns_discover: cannot bind UDP port %d: %s",
                   HEARTBEAT_PORT, err)
        return results
    try:
        deadline = time.time() + timeout
        while time.time() < deadline:
            try:
                data, addr = sock.recvfrom(RECV_BUFFER)
            except socket.timeout:
                # No packet arrived within LISTEN_TIMEOUT — keep waiting
                # until the overall `timeout` deadline expires.
                continue
            except OSError as e:
                _log.warning("mdns_discover: recvfrom error: %s", e)
                break
            parsed = _parse_heartbeat(data, addr)
            if parsed is not None:
                results.append(parsed)
    finally:
        try:
            sock.close()
        except OSError:
            pass

    # Deduplicate by name (last one wins, so we keep the freshest IP).
    seen: dict[str, tuple[str, str, int]] = {}
    for name, ip, port in results:
        seen[name] = (name, ip, port)
    return list(seen.values())


class HeartbeatListener(QThread):
    """Persistent UDP heartbeat listener.

    Emits:
      - `heartbeat(name, ip, port)` for every valid heartbeat received
      - `status(level, message)` for bind/listen errors so the UI can
        surface them instead of dying silently

    This replaces the old 1.5s-burst-every-12s approach, which missed
    any device whose heartbeat didn't land inside the 1.5s window. ESP32
    devices broadcast every 5s, so a persistent listener catches every
    broadcast within ~5s of the device appearing on the network.
    """
    heartbeat = pyqtSignal(str, str, int)   # name, ip, port
    status     = pyqtSignal(str, str)       # level ("info"|"warn"|"error"), message

    def __init__(self) -> None:
        super().__init__()
        self._running = False
        self._sock: Optional[socket.socket] = None

    def run(self) -> None:
        self._running = True
        bind_attempts = 0

        while self._running:
            # ── (re)bind if needed ───────────────────────────────
            if self._sock is None:
                sock, err = _make_listening_socket()
                if sock is None:
                    bind_attempts += 1
                    _log.error("HeartbeatListener bind failed (%d/%d): %s",
                               bind_attempts, BIND_MAX_RETRIES, err)
                    if bind_attempts >= BIND_MAX_RETRIES:
                        hint = (
                            f"Listener giving up after {bind_attempts} attempts. "
                            f"Common causes: another Espy instance is running, "
                            f"Windows Firewall is blocking UDP port {HEARTBEAT_PORT}, "
                            f"or antivirus is hooking the socket."
                        )
                        _log.error(hint)
                        self.status.emit("error",
                            f"Cannot bind UDP port {HEARTBEAT_PORT}: {err}\n{hint}")
                        return
                    self.status.emit("warn",
                        f"Cannot bind UDP port {HEARTBEAT_PORT}: {err}. "
                        f"Retrying in {int(BIND_RETRY_DELAY)}s "
                        f"({bind_attempts}/{BIND_MAX_RETRIES})...")
                    self._sleep_responsive(BIND_RETRY_DELAY)
                    continue

                self._sock = sock
                bind_attempts = 0
                msg = f"Listening for heartbeats on UDP port {HEARTBEAT_PORT} (0.0.0.0)"
                _log.info(msg)
                self.status.emit("info", msg)

            # ── receive one packet ───────────────────────────────
            try:
                data, addr = self._sock.recvfrom(RECV_BUFFER)
            except socket.timeout:
                continue
            except OSError as e:
                # Socket was closed under us (stop()) or fatally errored.
                if self._running:
                    _log.warning("HeartbeatListener recvfrom error: %s", e)
                    self._safe_close()
                continue

            parsed = _parse_heartbeat(data, addr)
            if parsed is not None:
                name, ip, port = parsed
                self.heartbeat.emit(name, ip, port)

        self._safe_close()
        _log.info("HeartbeatListener stopped.")

    def _sleep_responsive(self, seconds: float) -> None:
        """Sleep in small chunks so stop() stays responsive."""
        slept = 0.0
        while self._running and slept < seconds:
            time.sleep(0.1)
            slept += 0.1

    def _safe_close(self) -> None:
        if self._sock is not None:
            try:
                self._sock.close()
            except OSError:
                pass
            self._sock = None

    def stop(self) -> None:
        self._running = False
        self._safe_close()
        # Don't wait forever if the thread is stuck in bind-retry sleep.
        self.wait(3000)
