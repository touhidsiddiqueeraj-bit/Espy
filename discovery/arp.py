from __future__ import annotations
import socket
import ipaddress
import urllib.request
import json
from typing import Optional

from constants import OTA_PORT
from espy_logging import get_logger

_log = get_logger("discovery.arp")


def _get_local_subnet() -> Optional[str]:
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        parts = ip.split(".")
        return f"{parts[0]}.{parts[1]}.{parts[2]}."
    except OSError as e:
        _log.warning("Could not determine local subnet: %s", e)
        return None


def arp_scan(timeout: float = 4) -> list[tuple[str, str]]:
    """Scan the local /24 subnet for devices responding on OTA_PORT.

    Returns list of (ip, device_name). Errors are logged (not silently
    swallowed) so users can diagnose network/firewall issues.
    """
    results: list[tuple[str, str]] = []
    subnet = _get_local_subnet()
    if not subnet:
        _log.warning("ARP scan skipped — no local subnet detected.")
        return results

    hosts = [f"{subnet}{i}" for i in range(1, 255)]
    _log.debug("ARP scan starting on %s0/24 (%d hosts, timeout=%ds)",
               subnet, len(hosts), timeout)

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
        except Exception as e:
            # Per-host failures are expected (most hosts aren't ESP32s).
            # Log at debug level so we don't spam the log.
            _log.debug("Probe %s failed: %s", ip, e)
            return None

    try:
        with concurrent.futures.ThreadPoolExecutor(max_workers=50) as pool:
            futures = {pool.submit(probe, ip): ip for ip in hosts}
            for fut in concurrent.futures.as_completed(futures, timeout=timeout):
                try:
                    r = fut.result()
                    if r:
                        results.append(r)
                except concurrent.futures.TimeoutError:
                    pass
                except Exception as e:
                    _log.debug("ARP future error: %s", e)
    except concurrent.futures.TimeoutError:
        _log.warning("ARP scan timed out after %ds.", timeout)
    except Exception as e:
        _log.error("ARP scan failed: %s", e)

    _log.info("ARP scan found %d device(s).", len(results))
    return results
