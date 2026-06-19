from __future__ import annotations
import subprocess
import sys
import os
import shutil
import time
import tempfile
from pathlib import Path
from typing import Optional

from PyQt6.QtCore import QThread, pyqtSignal


def _make_credential_blob(ssid: str, password: str, name: str) -> bytes:
    blob = b"EC"
    ssid_b = ssid.encode()
    blob += bytes([len(ssid_b)]) + ssid_b
    pass_b = password.encode()
    blob += bytes([len(pass_b)]) + pass_b
    name_b = name.encode()
    blob += bytes([len(name_b)]) + name_b
    while len(blob) % 4:
        blob += b'\xff'
    return blob


def _find_esptool() -> Optional[list[str]]:
    if getattr(sys, "frozen", False):
        base = sys._MEIPASS
    else:
        base = str(Path(__file__).parent.parent)
    candidates = [
        os.path.join(base, "tools", "esptool"),
        os.path.join(base, "tools", "esptool.exe"),
        os.path.join(base, "tools", "esptool.py"),
        shutil.which("esptool.py"),
        shutil.which("esptool"),
    ]
    try:
        import esptool
        if not getattr(sys, "frozen", False):
            return [sys.executable, "-m", "esptool"]
    except ImportError:
        pass
    for c in candidates:
        if c and os.path.isfile(c):
            return [c]
    return None


def _esptool_write(esptool_cmd: list[str], port: str, offset: str,
                   file_path: str, timeout: int = 30,
                   label: str = "") -> tuple[int, str, str]:
    cmd = [*esptool_cmd, "--port", port, "--baud", "115200",
           "write-flash", offset, file_path]
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
    return r.returncode, r.stdout, r.stderr


class UsbFlashWorker(QThread):
    progress = pyqtSignal(int, str)
    finished = pyqtSignal()
    failed = pyqtSignal(str)

    def __init__(self, port: str, base_fw_path: str,
                 device_name: str, wifi_ssid: str, wifi_password: str,
                 partition_bin_path: str | None = None,
                 board: str = ""):
        super().__init__()
        self.port = port
        self.base_fw_path = base_fw_path
        self.device_name = device_name
        self.wifi_ssid = wifi_ssid
        self.wifi_password = wifi_password
        self.partition_bin_path = partition_bin_path
        self.board = board

    def run(self):
        try:
            esptool = _find_esptool()
            if not esptool:
                self.failed.emit(
                    "Could not find esptool. Espy installation may be incomplete."
                )
                return

            self.progress.emit(5, "Preparing your ESP32...")

            # Erase
            self.progress.emit(15, "Erasing old firmware...")
            erase_args = [*esptool, "--port", self.port, "--baud", "115200",
                          "erase-flash"]
            erase = subprocess.run(
                erase_args, capture_output=True, text=True, timeout=60
            )
            if erase.returncode != 0:
                detail = (erase.stderr.strip() or erase.stdout.strip() or
                          "could not connect to ESP32")
                self.failed.emit(
                    f"Could not prepare the ESP32 ({detail}). "
                    "Try holding the BOOT button or a different USB cable."
                )
                return

            # Flash base firmware at 0x0 (combined bootloader + partition + app)
            self.progress.emit(40, "Installing Espy base firmware...")
            flash_cmd = [*esptool, "--port", self.port, "--baud", "115200"]
            if self.board:
                from constants import BOARDS
                info = BOARDS.get(self.board, {})
                flash_size = info.get("flash_size", "4MB")
                flash_cmd.extend(["--before", "default-reset", "--after", "hard-reset",
                                  "write-flash", "-fs", flash_size,
                                  "0x0", self.base_fw_path])
            else:
                flash_cmd.extend(["write-flash", "0x0", self.base_fw_path])
            flash = subprocess.run(
                flash_cmd, capture_output=True, text=True, timeout=120
            )
            if flash.returncode != 0:
                detail = (flash.stderr.strip() or flash.stdout.strip() or
                          "write failed")
                self.failed.emit(
                    f"Installation failed ({detail}). "
                    "Hold the BOOT button on your ESP32 and try again."
                )
                return

            # Flash partition table if a custom one is provided
            if self.partition_bin_path and os.path.isfile(self.partition_bin_path):
                self.progress.emit(60, "Writing custom partition table...")
                pt_cmd = [*esptool, "--port", self.port, "--baud", "115200",
                          "--before", "default-reset",
                          "write-flash", "0x8000", self.partition_bin_path]
                pt_result = subprocess.run(
                    pt_cmd, capture_output=True, text=True, timeout=30
                )
                if pt_result.returncode != 0:
                    self.progress.emit(60, "Partition table write skipped (continuing anyway)")

            # Brief pause so USB-serial reinitialises after the previous esptool reset
            time.sleep(1.5)

            # Write Wi-Fi credentials to easyesp_data partition
            if self.wifi_ssid:
                self.progress.emit(70, "Writing Wi-Fi credentials...")
                blob = _make_credential_blob(
                    self.wifi_ssid, self.wifi_password, self.device_name
                )
                creds_path = os.path.join(
                    tempfile.gettempdir(), "espy_creds.bin"
                )
                try:
                    with open(creds_path, "wb") as f:
                        f.write(blob)
                    cred_cmd = [*esptool, "--port", self.port, "--baud", "115200",
                                "--before", "default-reset",
                                "write-flash", "0x3C0040", creds_path]
                    cred_proc = subprocess.run(
                        cred_cmd, capture_output=True, text=True, timeout=30
                    )
                    if cred_proc.returncode != 0:
                        err_detail = (cred_proc.stderr.strip() or cred_proc.stdout.strip() or "unknown error")
                        self.progress.emit(
                            70,
                            f"Wi‑Fi write failed: {err_detail}"
                        )
                finally:
                    if os.path.exists(creds_path):
                        os.unlink(creds_path)

            self.progress.emit(80, "Preparing for first boot...")
            time.sleep(0.5)

            self.progress.emit(100, "Done! Unplug the USB cable.")
            self.finished.emit()

        except subprocess.TimeoutExpired:
            self.failed.emit(
                "Timed out trying to reach your ESP32. "
                "Hold the BOOT button while connecting, or check the USB cable."
            )
        except Exception as e:
            self.failed.emit(str(e))


class UsbAppFlashWorker(QThread):
    progress = pyqtSignal(int, str)
    finished = pyqtSignal()
    failed = pyqtSignal(str)

    def __init__(self, port: str, app_bin_path: str,
                 offset: str = "0x10000", board: str = "",
                 flash_size: str = "4MB"):
        super().__init__()
        self.port = port
        self.app_bin_path = app_bin_path
        self.offset = offset
        self.board = board
        self.flash_size = flash_size

    def run(self):
        try:
            esptool = _find_esptool()
            if not esptool:
                self.failed.emit("esptool not found.")
                return

            # Check if binary is a full flash image — if so, flash at 0x0
            flash_map = {"4MB": 4*1024*1024, "8MB": 8*1024*1024, "16MB": 16*1024*1024}
            flash_bytes = flash_map.get(self.flash_size, 4*1024*1024)
            file_size = os.path.getsize(self.app_bin_path)
            offset_int = int(self.offset, 16)
            if file_size + offset_int > flash_bytes:
                self.offset = "0x0"
                self.progress.emit(10, "Binary is a full flash image, flashing at 0x0...")
            else:
                self.progress.emit(10, f"Flashing at offset {self.offset}...")

            cmd = [*esptool, "--port", self.port, "--baud", "115200"]
            if self.board:
                cmd.extend(["--before", "default-reset", "--after", "hard-reset",
                           "write-flash", "-fs", self.flash_size,
                           self.offset, self.app_bin_path])
            else:
                cmd.extend(["write-flash", self.offset, self.app_bin_path])

            flash = subprocess.run(
                cmd, capture_output=True, text=True, timeout=120
            )
            if flash.returncode != 0:
                detail = (flash.stderr.strip() or flash.stdout.strip() or "write failed")
                cmd_str = " ".join(str(a) for a in cmd)
                self.failed.emit(
                    f"USB flash failed ({detail})\nCommand: {cmd_str}"
                )
                return

            self.progress.emit(100, "Done!")
            self.finished.emit()

        except subprocess.TimeoutExpired:
            self.failed.emit("Timed out flashing via USB.")
        except Exception as e:
            self.failed.emit(str(e))
