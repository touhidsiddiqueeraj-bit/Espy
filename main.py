#!/usr/bin/env python3
"""EasyESP — One-click wireless ESP32 firmware updater.
"""
import sys
import os

# Ensure the easyesp package directory is on path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import run

def main(): 
    run()

if __name__ == "__main__":
    main()
