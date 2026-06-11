from __future__ import annotations
import os
import sys
import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import Optional

from PyQt6.QtCore import QThread, pyqtSignal

from models import InoConfig
from constants import BOARDS
from parser import translate_error


class CompilerWorker(QThread):
    progress = pyqtSignal(str)
    finished = pyqtSignal(str)
    failed = pyqtSignal(str, str)

    def __init__(self, ino_path: str, cfg: InoConfig):
        super().__init__()
        self.ino_path = ino_path
        self.cfg = cfg

    def _find_arduino_cli(self) -> Optional[str]:
        if getattr(sys, "frozen", False):
            base = sys._MEIPASS
        else:
            base = str(Path(__file__).parent.parent)
        candidates = [
            os.path.join(base, "tools", "arduino-cli"),
            os.path.join(base, "tools", "arduino-cli.exe"),
            shutil.which("arduino-cli"),
            shutil.which("arduino-cli.exe"),
        ]
        for c in candidates:
            if c and os.path.isfile(c):
                return c
        return None

    def _install_missing_libs(self, cli: str) -> None:
        if not self.cfg.libraries:
            return
        import json
        installed: set[str] = set()
        try:
            r = subprocess.run(
                [cli, "lib", "list", "--format", "json"],
                capture_output=True, text=True
            )
            if r.returncode == 0 and r.stdout.strip():
                data = json.loads(r.stdout)
                if isinstance(data, list):
                    installed = {lib.get("library", {}).get("name", "") for lib in data}
                elif isinstance(data, dict):
                    libs = data.get("libraries", [])
                    installed = {lib.get("library", {}).get("name", "") for lib in libs}
        except Exception as e:
            self.progress.emit(f"  Could not check installed libraries — {e}")
        missing = [lib.name for lib in self.cfg.libraries if lib.name not in installed]
        if not missing:
            return
        self.progress.emit("Installing missing libraries...")
        for lib_name in missing:
            self.progress.emit(f"  Installing {lib_name}...")
            r = subprocess.run(
                [cli, "lib", "install", lib_name],
                capture_output=True, text=True
            )
            if r.returncode != 0:
                self.progress.emit(f"  Could not install '{lib_name}' — continuing anyway")

    def run(self):
        cli = self._find_arduino_cli()
        if not cli:
            self.failed.emit(
                "Could not find the build tools. EasyESP installation may be incomplete.",
                "arduino-cli not found in PATH or bundled tools."
            )
            return

        tmp = tempfile.mkdtemp(prefix="easyesp_")
        try:
            sketch_name = Path(self.ino_path).stem
            sketch_dir = os.path.join(tmp, sketch_name)
            os.makedirs(sketch_dir)
            dest_ino = os.path.join(sketch_dir, f"{sketch_name}.ino")
            shutil.copy2(self.ino_path, dest_ino)

            self._install_missing_libs(cli)

            self.progress.emit("Compiling your code...")
            board_cfg = BOARDS.get(self.cfg.board, list(BOARDS.values())[0])
            fqbn = board_cfg["fqbn"]

            # Apply flash size override if set
            fs = self.cfg.flash_size_override or self.cfg.flash_size
            fqbn += f":FlashSize={fs.replace('MB', 'M')}"

            outdir = os.path.join(tmp, "output")
            os.makedirs(outdir)

            # Write custom partition CSV if set
            if self.cfg.partition_csv_override:
                csv_path = os.path.join(sketch_dir, "partitions.csv")
                with open(csv_path, "w") as f:
                    f.write(self.cfg.partition_csv_override)
                fqbn += ",PartitionScheme=custom"

            result = subprocess.run(
                [cli, "compile",
                 "--fqbn", fqbn,
                 "--output-dir", outdir,
                 sketch_dir],
                capture_output=True, text=True
            )

            if result.returncode != 0:
                friendly = translate_error(result.stderr + result.stdout)
                self.failed.emit(friendly, result.stderr + result.stdout)
                return

            bins = list(Path(outdir).glob("*.bin"))
            if self.cfg.partition_csv_override or self.cfg.partition_scheme != "default_ota":
                # Keep partitions.bin when using custom scheme
                bins = [b for b in bins if "bootloader" not in b.name]
            else:
                bins = [b for b in bins if "bootloader" not in b.name and "partitions" not in b.name]
            if not bins:
                self.failed.emit(
                    "Compilation succeeded but no firmware file was produced.",
                    result.stdout,
                )
                return

            bin_path = str(bins[0])
            self.cfg.bin_size_bytes = os.path.getsize(bin_path)

            # Check if binary fits in selected partition scheme
            from constants import get_scheme_partitions
            parts = get_scheme_partitions(fs, self.cfg.partition_scheme)
            if not parts:
                parts = board_cfg.get("partitions", [])
            max_app = 0
            for p in parts:
                if "ota" in p["name"].lower() or p["name"] == "App":
                    sz = p["size"]
                    try:
                        if sz.endswith("MB"):
                            max_app = max(max_app, int(float(sz.replace("MB", "")) * 1024 * 1024))
                        elif sz.endswith("KB"):
                            max_app = max(max_app, int(sz.replace("KB", "")) * 1024)
                    except ValueError:
                        pass
            if max_app and self.cfg.bin_size_bytes > max_app:
                self.progress.emit(
                    f"⚠ Binary ({self.cfg.bin_size_bytes / 1024:.0f} KB) exceeds "
                    f"app partition ({max_app / 1024:.0f} KB) — may not fit!"
                )
            else:
                self.progress.emit("Done! Ready to upload.")
            self.finished.emit(bin_path)

        except Exception as e:
            self.failed.emit(str(e), "")
        finally:
            shutil.rmtree(tmp, ignore_errors=True)
