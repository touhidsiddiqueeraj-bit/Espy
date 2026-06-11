from __future__ import annotations
import json
import time
import hashlib
import os
from pathlib import Path
from typing import Optional

from models import FirmwareBackup
from constants import BACKUP_DIR

MAX_BACKUPS = 5


def save_backup(device_name: str, firmware_data: bytes, version: str = "") -> FirmwareBackup:
    device_dir = BACKUP_DIR / _safe_name(device_name)
    device_dir.mkdir(parents=True, exist_ok=True)

    checksum = hashlib.sha256(firmware_data).hexdigest()
    timestamp = time.time()
    fw = FirmwareBackup(
        version=version or f"backup_{int(timestamp)}",
        timestamp=timestamp,
        checksum_sha256=checksum,
        size_bytes=len(firmware_data),
    )

    path = device_dir / f"{fw.version}.bin"
    path.write_bytes(firmware_data)

    # Prune old backups
    backups = sorted(device_dir.glob("*.bin"), key=os.path.getmtime)
    while len(backups) > MAX_BACKUPS:
        backups[0].unlink()
        backups = backups[1:]

    return fw


def list_backups(device_name: str) -> list[FirmwareBackup]:
    device_dir = BACKUP_DIR / _safe_name(device_name)
    if not device_dir.exists():
        return []
    backups: list[FirmwareBackup] = []
    for path in sorted(device_dir.glob("*.bin"), key=os.path.getmtime, reverse=True):
        data = path.read_bytes()
        backups.append(FirmwareBackup(
            version=path.stem,
            timestamp=os.path.getmtime(path),
            checksum_sha256=hashlib.sha256(data).hexdigest(),
            size_bytes=len(data),
        ))
    return backups


def restore_backup(device_name: str, version: str) -> Optional[bytes]:
    path = BACKUP_DIR / _safe_name(device_name) / f"{version}.bin"
    if path.exists():
        return path.read_bytes()
    return None


def _safe_name(name: str) -> str:
    return "".join(c if c.isalnum() or c in " _-" else "_" for c in name).strip()
