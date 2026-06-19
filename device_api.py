"""Device management API client — talks to the ESP32 firmware endpoints.

Endpoints used:
  GET  /espy/health    — telemetry (RSSI, uptime, heap, partitions, …)
  POST /espy/rollback  — revert to the previous OTA partition

These endpoints are added to the base firmware in firmware/espy_base.ino.
Older firmware that doesn't have them will return 404; we handle that
gracefully so the UI degrades smoothly.
"""
from __future__ import annotations
import json
import urllib.request
from typing import Optional

from constants import OTA_PORT
from models import Device
from espy_logging import get_logger

_log = get_logger("device_api")

# Timeout for HTTP requests to the device. Devices on flaky Wi-Fi may
# take longer to respond, but we don't want to hang the UI forever.
HEALTH_TIMEOUT = 3.0
ROLLBACK_TIMEOUT = 5.0


class DeviceAPIError(Exception):
    """Raised when the device returns an error or is unreachable."""
    def __init__(self, message: str, status_code: int = 0, raw: str = ""):
        super().__init__(message)
        self.status_code = status_code
        self.raw = raw


def fetch_health(device: Device) -> dict:
    """GET /espy/health from the device.

    Returns the parsed JSON payload. Raises DeviceAPIError on any
    failure (network error, HTTP error, parse error).
    """
    url = f"http://{device.ip}:{device.port}/espy/health"
    try:
        req = urllib.request.Request(url, method="GET")
        with urllib.request.urlopen(req, timeout=HEALTH_TIMEOUT) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            return data
    except urllib.error.HTTPError as e:
        # 404 means the firmware is too old to have /espy/health
        if e.code == 404:
            raise DeviceAPIError(
                "Device firmware is too old to support /espy/health. "
                "Flash the latest base firmware to enable health telemetry.",
                status_code=404,
            )
        raise DeviceAPIError(f"HTTP {e.code}: {e.reason}", status_code=e.code)
    except urllib.error.URLError as e:
        raise DeviceAPIError(f"Network error: {e.reason}")
    except json.JSONDecodeError as e:
        raise DeviceAPIError(f"Bad JSON from device: {e}")
    except Exception as e:
        raise DeviceAPIError(f"Unexpected error: {e}")


def request_rollback(device: Device) -> dict:
    """POST /espy/rollback — revert to the previous OTA partition.

    Returns the parsed JSON response (usually empty since the device
    reboots immediately). Raises DeviceAPIError on failure.

    Note: a successful rollback causes the device to reboot, so the
    HTTP connection will typically close before the response is fully
    sent. We treat connection-closed as success.
    """
    url = f"http://{device.ip}:{device.port}/espy/rollback"
    try:
        req = urllib.request.Request(
            url, method="POST",
            data=b"",  # empty body
            headers={"Content-Type": "application/json"},
        )
        with urllib.request.urlopen(req, timeout=ROLLBACK_TIMEOUT) as resp:
            try:
                return json.loads(resp.read().decode("utf-8"))
            except json.JSONDecodeError:
                # Device probably rebooted before sending a body — that's OK.
                return {"status": "rebooting"}
    except urllib.error.HTTPError as e:
        if e.code == 404:
            raise DeviceAPIError(
                "Device firmware is too old to support /espy/rollback. "
                "Flash the latest base firmware to enable rollback.",
                status_code=404,
            )
        # Read the error body for diagnostics
        try:
            body = e.read().decode("utf-8")
        except Exception:
            body = ""
        raise DeviceAPIError(
            f"HTTP {e.code}: {e.reason}\n{body}",
            status_code=e.code, raw=body,
        )
    except urllib.error.URLError as e:
        # Connection reset is expected — the device reboots immediately.
        reason = str(e.reason)
        if "Connection refused" in reason or "Connection reset" in reason:
            _log.info("Device closed connection during rollback (expected — it's rebooting).")
            return {"status": "rebooting"}
        raise DeviceAPIError(f"Network error: {reason}")
    except Exception as e:
        raise DeviceAPIError(f"Unexpected error: {e}")


def fetch_alive(device: Device) -> bool:
    """Quick liveness check via /espy/alive. Returns True if device responds."""
    url = f"http://{device.ip}:{device.port}/espy/alive"
    try:
        req = urllib.request.Request(url, method="GET")
        with urllib.request.urlopen(req, timeout=2.0) as resp:
            return resp.status == 200
    except Exception:
        return False
