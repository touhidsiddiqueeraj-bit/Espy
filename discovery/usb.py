from __future__ import annotations
import sys
from typing import Optional, Callable
from constants import USB_PORT_PATTERNS

USB_VENDORS_WHITELIST = (
    0x10C4,  # Silicon Labs CP210x
    0x1A86,  # QinHeng CH340/CH341
    0x0403,  # FTDI
    0x303A,  # Espressif USB-JTAG-Serial
    0x239A,  # Adafruit
)

def usb_probe() -> list[dict]:
    """Find ESP32 devices connected via USB.
    Returns list of {port, description, device_name}.
    """
    results: list[dict] = []
    try:
        import serial.tools.list_ports
        for p in serial.tools.list_ports.comports():
            # Prefer VID/PID check when available (most reliable)
            if p.vid is not None and p.vid in USB_VENDORS_WHITELIST:
                results.append({
                    "port": p.device,
                    "description": p.description,
                    "device_name": "",
                })
                continue
            # Fallback: description keyword match
            desc = (p.description or "").lower()
            if any(k in desc for k in
                   ("cp210", "ch340", "ch341", "ftdi",
                    "esp32", "silicon", "uart")):
                results.append({
                    "port": p.device,
                    "description": p.description,
                    "device_name": "",
                })
                continue
        # Last fallback: port name pattern (only if nothing found yet)
        if not results:
            for p in serial.tools.list_ports.comports():
                port_name = p.device
                if any(pattern in port_name for pattern in USB_PORT_PATTERNS):
                    results.append({
                        "port": p.device,
                        "description": p.description,
                        "device_name": "",
                    })
    except ImportError:
        pass
    return results

def autodetect_port() -> Optional[str]:
    ports = usb_probe()
    return ports[0]["port"] if ports else None

def auto_detect_all() -> list[str]:
    return [p["port"] for p in usb_probe()]
