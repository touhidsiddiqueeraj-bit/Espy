from __future__ import annotations
import socket
import ipaddress
import urllib.request
import json
from typing import Optional
from constants import OTA_PORT

def _get_local_subnet() -> Optional[str]:
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        parts = ip.split(".")
        return f"{parts[0]}.{parts[1]}.{parts[2]}."
    except Exception:
        return None

def arp_scan(timeout: float = 4) -> list[tuple[str, str]]:
    """Scan the local /24 subnet for devices responding on OTA_PORT.
    Returns list of (ip, device_name).
    """
    results: list[tuple[str, str]] = []
    subnet = _get_local_subnet()
    if not subnet:
        return results

    # Try the first few hosts (full scan would be 254 — sample for speed)
    hosts = [f"{subnet}{i}" for i in range(1, 255)]

    import concurrent.futures
    def probe(ip: str) -> Optional[tuple[str, str]]:
        try:
            req = urllib.request.Request(
                f"http://{ip}:{OTA_PORT}/espy/alive",
                method="GET",
            )
            with urllib.request.urlopen(req, timeout=1) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                name = data.get("device", "Unknown")
                return (ip, name)
        except Exception:
            return None

    with concurrent.futures.ThreadPoolExecutor(max_workers=50) as pool:
        futures = {pool.submit(probe, ip): ip for ip in hosts}
        for fut in concurrent.futures.as_completed(futures, timeout=timeout):
            try:
                r = fut.result()
                if r:
                    results.append(r)
            except Exception:
                pass

    return results
