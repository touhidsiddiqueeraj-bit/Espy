from __future__ import annotations
import socket
import json
from typing import Optional
from constants import HEARTBEAT_PORT, OTA_PORT

def mdns_discover(timeout: float = 1.5) -> list[tuple[str, str, int]]:
    """UDP broadcast heartbeat discovery (cross-platform, reliable).
    Listens for JSON heartbeat packets on HEARTBEAT_PORT.
    Falls back gracefully if mDNS is unavailable.
    """
    results: list[tuple[str, str, int]] = []
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.settimeout(timeout)
        sock.bind(("", HEARTBEAT_PORT))
        start = __import__("time").time()
        while __import__("time").time() - start < timeout:
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
    # Deduplicate by name
    seen: set[str] = set()
    unique: list[tuple[str, str, int]] = []
    for name, ip, port in results:
        if name not in seen:
            seen.add(name)
            unique.append((name, ip, port))
    return unique
