from __future__ import annotations
import json
import socket
from typing import Optional
from constants import CACHE_FILE, OTA_PORT

def load_cache() -> dict:
    if CACHE_FILE.exists():
        try:
            return json.loads(CACHE_FILE.read_text())
        except Exception:
            pass
    return {}

def save_cache(data: dict):
    try:
        CACHE_FILE.write_text(json.dumps(data, indent=2))
    except Exception:
        pass

def check_cached_ip(ip: str, port: int = OTA_PORT) -> bool:
    """Quick ping to see if a cached IP is still alive."""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(2)
        result = sock.connect_ex((ip, port))
        sock.close()
        return result == 0
    except Exception:
        return False
