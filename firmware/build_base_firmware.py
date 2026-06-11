#!/usr/bin/env python3
"""
Builds easyesp_base.ino using arduino-cli.
Output: firmware/easyesp_base.bin

Usage:
    python build_base_firmware.py

Requirements:
    - arduino-cli on PATH (or ARDUINO_CLI env var)
    - ESP32 core: arduino-cli core install esp32:esp32
"""

import subprocess
import shutil
import os
import sys
import tempfile
from pathlib import Path

SKETCH_PATH   = Path(__file__).parent.parent / "firmware" / "easyesp_base.ino"
PARTITION_CSV = Path(__file__).parent.parent / "firmware" / "easyesp_4mb.csv"
OUTPUT_BIN    = Path(__file__).parent.parent / "firmware" / "easyesp_base.bin"
FQBN          = "esp32:esp32:esp32"

def find_arduino_cli():
    env = os.environ.get("ARDUINO_CLI")
    if env and Path(env).is_file():
        return env
    found = shutil.which("arduino-cli") or shutil.which("arduino-cli.exe")
    if found:
        return found
    bundled = Path(__file__).parent.parent / "tools" / "arduino-cli"
    if bundled.is_file():
        return str(bundled)
    bundled_exe = Path(__file__).parent.parent / "tools" / "arduino-cli.exe"
    if bundled_exe.is_file():
        return str(bundled_exe)
    return None

def main():
    cli = find_arduino_cli()
    if not cli:
        print("ERROR: arduino-cli not found.")
        print("Install from https://arduino.github.io/arduino-cli/")
        sys.exit(1)

    # Ensure sketch directory exists with proper name
    sketch_dir = Path(tempfile.mkdtemp(prefix="easyesp_build_")) / "easyesp_base"
    sketch_dir.mkdir(parents=True)

    # Copy sketch and partition CSV
    shutil.copy2(SKETCH_PATH, sketch_dir / "easyesp_base.ino")
    shutil.copy2(PARTITION_CSV, sketch_dir / "easyesp_4mb.csv")

    # Ensure ESP32 core is installed
    result = subprocess.run([cli, "core", "list"], capture_output=True, text=True)
    if "esp32:esp32" not in result.stdout:
        print("Installing ESP32 core...")
        subprocess.run([cli, "core", "install", "esp32:esp32"], check=True)

    # Build
    outdir = Path(tempfile.mkdtemp(prefix="easyesp_bin_"))
    print(f"Compiling {SKETCH_PATH.name}...")

    result = subprocess.run(
        [cli, "compile",
         "--fqbn", FQBN,
         "--output-dir", str(outdir),
         str(sketch_dir)],
        capture_output=True, text=True,
    )

    if result.returncode != 0:
        print("COMPILATION FAILED:")
        print(result.stderr)
        print(result.stdout)
        sys.exit(1)

    # Find the .bin
    bins = [f for f in outdir.glob("*.bin")
            if "bootloader" not in f.name and "partitions" not in f.name]
    if not bins:
        print("ERROR: No .bin produced")
        sys.exit(1)

    bin_path = bins[0]
    size_kb = bin_path.stat().st_size / 1024

    # Copy to firmware/
    OUTPUT_BIN.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(bin_path, OUTPUT_BIN)

    print(f"\nBuilt successfully:")
    print(f"  Size:    {size_kb:.1f} KB")
    print(f"  Output:  {OUTPUT_BIN}")

    # Cleanup
    shutil.rmtree(sketch_dir.parent, ignore_errors=True)
    shutil.rmtree(outdir, ignore_errors=True)

if __name__ == "__main__":
    main()
