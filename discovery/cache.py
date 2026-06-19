from __future__ import annotations
import json
import socket
from typing import Optional

from constants import CACHE_FILE, OTA_PORT
from espy_logging import get_logger

_log = get_logger("discovery.cache")


def load_cache() -> dict:
    if CACHE_FILE.exists():
        try:
            return json.loads(CACHE_FILE.read_text())
        except Exception as e:
            _log.warning("Could not parse discovery cache %s: %s", CACHE_FILE, e)
    return {}


def save_cache(data: dict):
    try:
        CACHE_FILE.write_text(json.dumps(data, indent=2))
    except Exception as e:
        _log.warning("Could not write discovery cache %s: %s", CACHE_FILE, e)


def check_cached_ip(ip: str, port: int = OTA_PORT) -> bool:
    """Quick TCP connect to see if a cached IP:port is still alive."""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(2)
        result = sock.connect_ex((ip, port))
        sock.close()
        return result == 0
    except OSError as e:
        _log.debug("check_cached_ip(%s:%d) failed: %s", ip, port, e)
        return False
