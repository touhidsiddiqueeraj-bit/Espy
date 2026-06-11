from __future__ import annotations
import time
import json
from typing import Optional, Any
from dataclasses import dataclass, field, asdict


@dataclass
class LibraryInfo:
    name: str
    version: str = ""
    available: bool = False
    needs_download: bool = False


@dataclass
class InoConfig:
    board: str = "ESP32 Dev Module"
    flash_size: str = "4MB"
    wifi_ssid: str = ""
    wifi_password: str = ""
    libraries: list[LibraryInfo] = field(default_factory=list)
    device_name: str = ""
    ota_password: str = ""
    deep_sleep: bool = False
    deep_sleep_interval: int = 0
    has_ota_conflict: bool = False
    warnings: list[str] = field(default_factory=list)
    auto_fixes: list[dict[str, Any]] = field(default_factory=list)
    raw_content: str = ""
    bin_size_bytes: int = 0
    partition_scheme: str = "default_ota"
    partition_csv_override: str = ""
    flash_size_override: str = ""


@dataclass
class FirmwareBackup:
    version: str
    timestamp: float
    checksum_sha256: str
    size_bytes: int
    partition: str = ""


class Device:
    def __init__(self, name: str, ip: str = "", port: int = 8080):
        self.name = name
        self.ip = ip
        self.port = port
        self.last_seen = time.time()
        self.firmware_version = "unknown"
        self.status: str = "online"
        self.last_known_ip: str = ip
        self.firmware_history: list[FirmwareBackup] = []
        self.version_history: list[str] = []

    @property
    def is_stale(self) -> bool:
        return (time.time() - self.last_seen) > 20

    @property
    def friendly_label(self) -> str:
        if self.name and self.name != "Unknown":
            return f"{self.name}"
        if self.ip:
            return f"Device at {self.ip}"
        return "Unknown Device"

    def to_cache(self) -> dict:
        return {
            "name": self.name,
            "last_known_ip": self.last_known_ip,
            "port": self.port,
            "firmware_version": self.firmware_version,
            "last_seen": self.last_seen,
            "version_history": self.version_history[-10:],
        }

    @classmethod
    def from_cache(cls, data: dict) -> Device:
        d = cls(data["name"], data.get("last_known_ip", ""), data.get("port", 8080))
        d.firmware_version = data.get("firmware_version", "unknown")
        d.last_seen = data.get("last_seen", 0)
        d.version_history = data.get("version_history", [])
        return d

    def __repr__(self) -> str:
        return f"<Device {self.name} @ {self.ip}>"
