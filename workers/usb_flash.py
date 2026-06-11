from __future__ import annotations
import subprocess
import sys
import os
import shutil
import time
from pathlib import Path
from typing import Optional

from PyQt6.QtCore import QThread, pyqtSignal


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

    def _find_esptool(self) -> Optional[list[str]]:
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
            return [sys.executable, "-m", "esptool"]
        except ImportError:
            pass
        for c in candidates:
            if c and os.path.isfile(c):
                return [c]
        return None

    def run(self):
        try:
            esptool = self._find_esptool()
            if not esptool:
                self.failed.emit(
                    "Could not find esptool. EasyESP installation may be incomplete."
                )
                return

            self.progress.emit(5, "Preparing your ESP32...")

            # Erase (use flash_size if board is known)
            self.progress.emit(15, "Erasing old firmware...")
            erase_args = [*esptool, "--port", self.port, "--baud", "921600"]
            if self.board:
                from constants import BOARDS
                info = BOARDS.get(self.board, {})
                fs = info.get("flash_size", "4MB")
                erase_args.extend(["--before", "default_reset", "--after", "hard_reset",
                                   "--flash_size", fs, "erase_flash"])
            else:
                erase_args.append("erase_flash")
            erase = subprocess.run(
                erase_args, capture_output=True, text=True, timeout=30
            )
            if erase.returncode != 0:
                self.failed.emit(
                    "Could not prepare the ESP32. "
                    "Try a different USB cable or hold the BOOT button."
                )
                return

            # Flash base firmware at 0x0 (combined bootloader + partition + app)
            self.progress.emit(40, "Installing EasyESP base firmware...")
            flash_cmd = [*esptool, "--port", self.port, "--baud", "921600"]
            if self.board:
                from constants import BOARDS
                info = BOARDS.get(self.board, {})
                flash_size = info.get("flash_size", "4MB").lower()
                flash_cmd.extend(["--before", "default_reset", "--after", "hard_reset",
                                  "write_flash", "-fs", flash_size,
                                  "0x0", self.base_fw_path])
            else:
                flash_cmd.extend(["write_flash", "0x0", self.base_fw_path])
            flash = subprocess.run(
                flash_cmd, capture_output=True, text=True, timeout=60
            )
            if flash.returncode != 0:
                self.failed.emit(
                    "Installation failed. Hold the BOOT button on your ESP32 and try again."
                )
                return

            # Flash partition table if a custom one is provided
            if self.partition_bin_path and os.path.isfile(self.partition_bin_path):
                self.progress.emit(60, "Writing custom partition table...")
                pt_result = subprocess.run(
                    [*esptool, "--port", self.port, "--baud", "921600",
                     "write_flash", "0x8000", self.partition_bin_path],
                    capture_output=True, text=True, timeout=30
                )
                if pt_result.returncode != 0:
                    self.progress.emit(60, "Partition table write skipped (continuing anyway)")

            # Wi-Fi credentials are configured via the captive portal on first boot
            self.progress.emit(80, "Preparing for first boot...")
            time.sleep(0.5)

            self.progress.emit(100, "Done! Unplug the USB cable.")
            self.finished.emit()

        except subprocess.TimeoutExpired:
            self.failed.emit("Timed out. Is the ESP32 plugged in?")
        except Exception as e:
            self.failed.emit(str(e))
