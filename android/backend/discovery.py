from __future__ import annotations
import socket
import json
import threading
import time
from typing import Optional

from .models import Device

HEARTBEAT_PORT = 7777
OTA_PORT = 8080


def mdns_discover(timeout: float = 2.0) -> list[tuple[str, str, int]]:
    results: list[tuple[str, str, int]] = []
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.settimeout(timeout)
        sock.bind(("", HEARTBEAT_PORT))
        start = time.time()
        while time.time() - start < timeout:
            try:
                data, addr = sock.recvfrom(512)
                payload = json.loads(data.decode("utf-8"))
                name = payload.get("device", "Unknown")
                ip = addr[0]
                port = int(payload.get("ota_port", OTA_PORT))
                results.append((name, ip, port))
            except socket.timeout:
                break
            except Exception:
                continue
        sock.close()
    except Exception:
        pass
    seen: set[str] = set()
    unique: list[tuple[str, str, int]] = []
    for name, ip, port in results:
        if name not in seen:
            seen.add(name)
            unique.append((name, ip, port))
    return unique


def usb_probe() -> list[dict]:
    results: list[dict] = []
    try:
        import serial.tools.list_ports
        for p in serial.tools.list_ports.comports():
            if p.vid in (0x10C4, 0x1A86, 0x0403, 0x303A, 0x239A):
                results.append({"port": p.device, "description": p.description})
                continue
            desc = (p.description or "").lower()
            if any(k in desc for k in ("cp210", "ch340", "ch341", "ftdi", "esp32", "uart")):
                results.append({"port": p.device, "description": p.description})
                continue
        if not results:
            for p in serial.tools.list_ports.comports():
                if any(patt in p.device for patt in ("ttyUSB", "ttyACM", "COM")):
                    results.append({"port": p.device, "description": p.description})
    except ImportError:
        pass
    return results


class DiscoveryThread(threading.Thread):
    def __init__(self,
                 on_device_found: callable = None,
                 on_device_lost: callable = None,
                 on_usb_found: callable = None):
        super().__init__(daemon=True)
        self._running = False
        self._known: dict[str, Device] = {}
        self.on_device_found = on_device_found
        self.on_device_lost = on_device_lost
        self.on_usb_found = on_usb_found

    def stop(self):
        self._running = False

    def run(self):
        self._running = True
        while self._running:
            for name, dev in list(self._known.items()):
                if dev.is_stale:
                    del self._known[name]
                    if self.on_device_lost:
                        self.on_device_lost(name)

            fresh = mdns_discover(timeout=1.5)
            for name, ip, port in fresh:
                now = time.time()
                if name in self._known:
                    d = self._known[name]
                    d.ip = ip
                    d.port = port
                    d.last_seen = now
                else:
                    d = Device(name, ip, port)
                    self._known[name] = d
                    if self.on_device_found:
                        self.on_device_found(d)

            usb_devs = usb_probe()
            if self.on_usb_found:
                self.on_usb_found(usb_devs)

            for _ in range(6):
                if not self._running:
                    break
                time.sleep(0.5)
