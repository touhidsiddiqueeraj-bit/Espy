#!/usr/bin/env python3
"""Moved to firmware/build_base_firmware.py"""
import sys, subprocess
subprocess.run([sys.executable, str(__import__("pathlib").Path(__file__).parent.parent / "firmware" / "build_base_firmware.py")])
