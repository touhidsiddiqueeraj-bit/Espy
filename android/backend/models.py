from __future__ import annotations
import time
from typing import Optional
from dataclasses import dataclass, field


@dataclass
class FirmwareBackup:
    version: str
    timestamp: float
    checksum_sha256: str
    size_bytes: int
    partition: str = ""


class Device:
    def __init__(self, name: str, ip: str = "", port: int = 8080, is_usb: bool = False):
        self.name = name
        self.ip = ip
        self.port = port
        self.is_usb = is_usb
        self.last_seen = time.time()
        self.firmware_version = "unknown"
        self.last_known_ip = ip

    @property
    def is_stale(self) -> bool:
        return (time.time() - self.last_seen) > 20

    @property
    def label(self) -> str:
        if self.name and self.name != "Unknown":
            return self.name
        if self.ip:
            return f"Device at {self.ip}"
        return "Unknown Device"
