from __future__ import annotations
import subprocess
import sys
import os
import shutil
import time
import threading
from pathlib import Path
from typing import Optional

ANDROID_BOARDS = {
    "ESP32 Dev Module": {"flash_size": "4MB"},
    "ESP32-S3 DevKitC": {"flash_size": "16MB"},
    "ESP32-C3 DevKit": {"flash_size": "4MB"},
    "ESP32-S2 Saola": {"flash_size": "4MB"},
}


def find_esptool() -> Optional[list[str]]:
    if getattr(sys, "frozen", False):
        base = sys._MEIPASS
    else:
        base = str(Path(__file__).parent.parent.parent)
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


class UsbFlashThread(threading.Thread):
    def __init__(self, port: str, base_fw_path: str,
                 board: str = "",
                 on_progress: callable = None,
                 on_finished: callable = None,
                 on_failed: callable = None):
        super().__init__(daemon=True)
        self.port = port
        self.base_fw_path = base_fw_path
        self.board = board
        self.on_progress = on_progress
        self.on_finished = on_finished
        self.on_failed = on_failed

    def run(self):
        try:
            esptool = find_esptool()
            if not esptool:
                if self.on_failed:
                    self.on_failed("Could not find esptool.")
                return

            if self.on_progress:
                self.on_progress(5, "Preparing ESP32...")

            erase_args = [*esptool, "--port", self.port, "--baud", "921600"]
            info = ANDROID_BOARDS.get(self.board, {})
            fs = info.get("flash_size", "4MB")
            erase_args.extend(["--before", "default_reset", "--after", "hard_reset",
                               "--flash_size", fs, "erase_flash"])
            erase = subprocess.run(erase_args, capture_output=True, text=True, timeout=30)
            if erase.returncode != 0:
                if self.on_failed:
                    self.on_failed("Erase failed. Hold BOOT button and try again.")
                return

            if self.on_progress:
                self.on_progress(40, "Flashing firmware...")

            flash_cmd = [*esptool, "--port", self.port, "--baud", "921600",
                         "--before", "default_reset", "--after", "hard_reset",
                         "write_flash", "-fs", fs.lower(),
                         "0x0", self.base_fw_path]
            flash = subprocess.run(flash_cmd, capture_output=True, text=True, timeout=60)
            if flash.returncode != 0:
                if self.on_failed:
                    self.on_failed("Flash failed. Hold BOOT button and try again.")
                return

            if self.on_progress:
                self.on_progress(100, "Done!")
            if self.on_finished:
                self.on_finished()

        except subprocess.TimeoutExpired:
            if self.on_failed:
                self.on_failed("Timed out. Is the ESP32 plugged in?")
        except Exception as e:
            if self.on_failed:
                self.on_failed(str(e))
