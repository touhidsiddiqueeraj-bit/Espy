#!/usr/bin/env python3
# Espy — Monolithic build (all source inlined)
# 22 modules combined into one file
# Run: python3 espy.py

from __future__ import annotations
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Optional
from typing import Optional, Any
from typing import Optional, Callable
import hashlib
import json
import math
import os
import random
import re
import shutil
import socket
import subprocess
import sys
import tempfile
import threading
import time
from PyQt6.QtCore import (
    Qt, QTimer, QPropertyAnimation, QVariantAnimation, QEasingCurve,
    pyqtProperty, QRect, QSize, QPointF,
    QParallelAnimationGroup, QSequentialAnimationGroup, QPauseAnimation,
    QAbstractAnimation,
)
from PyQt6.QtCore import QThread, pyqtSignal
from PyQt6.QtCore import Qt, QSize, QTimer, pyqtSignal
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtCore import Qt, pyqtSignal, QSize
from PyQt6.QtCore import Qt, pyqtSignal, QTimer
from PyQt6.QtCore import Qt, pyqtSignal, QTimer, QSize
from PyQt6.QtGui import (
    QPainter, QColor, QBrush, QPen, QFont, QPixmap, QLinearGradient,
)
from PyQt6.QtGui import QDragEnterEvent, QDropEvent, QPixmap
from PyQt6.QtGui import QFont
from PyQt6.QtGui import QPixmap
from PyQt6.QtGui import QPixmap, QIcon
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QComboBox, QFrame, QPlainTextEdit, QCheckBox,
)
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QLineEdit, QComboBox, QFrame, QFormLayout, QTextEdit,
)
from PyQt6.QtWidgets import (
    QFrame, QVBoxLayout, QLabel, QPushButton, QFileDialog,
    QHBoxLayout, QWidget, QStackedLayout,
)
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QComboBox, QStackedWidget,
    QListWidget, QListWidgetItem, QFrame, QSizePolicy,
    QMessageBox, QProgressBar,
)
from PyQt6.QtWidgets import (
    QWidget, QLabel, QProgressBar, QStackedWidget, QGraphicsOpacityEffect,
)
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QProgressBar, QApplication,
)
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFrame, QScrollArea, QGridLayout,
)
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QLineEdit, QComboBox, QTextEdit, QFrame, QSplitter,
)
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QStackedWidget, QFrame, QLineEdit,
)
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QStackedWidget, QLineEdit, QProgressBar, QFrame,
)
from PyQt6.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QLabel, QCheckBox


# ══ palette.py ═══════════════════════════════════════

WARM_PASTEL = {
    "bg":          "#FFF8F0",
    "card":        "#FFE8D6",
    "card_hover":  "#FFDDC4",
    "border":      "#E8D5C4",
    "accent":      "#FF7B6B",
    "accent_hover":"#E86555",
    "success":     "#7BCBA5",
    "warning":     "#FFD166",
    "error":       "#FF6B6B",
    "info":        "#C4A1FF",
    "text":        "#2D3436",
    "text_muted":  "#8E8E93",
    "text_faint":  "#C0B8B0",
    "text_on_accent":"#2D3436",
    "esp_skin":    "#FFD4B8",
    "esp_eye":     "#2D3436",
}

def stylesheet() -> str:
    c = WARM_PASTEL
    return f"""
    QMainWindow, QWidget {{
        background: {c['bg']};
        color: {c['text']};
        font-family: 'Ubuntu', 'Noto Sans', 'Segoe UI', system-ui, sans-serif;
        font-size: 17px;
    }}
    QFrame#card {{
        background: {c['card']};
        border: 1px solid {c['border']};
        border-radius: 18px;
        padding: 8px;
    }}
    QFrame#dropzone {{
        background: {c['card']};
        border: 3px dashed {c['border']};
        border-radius: 24px;
    }}
    QFrame#dropzone[dragover="true"] {{
        border-color: {c['accent']};
        background: #FFF0EA;
    }}
    QPushButton#primary {{
        background: {c['accent']};
        color: {c['text_on_accent']};
        border: none;
        border-radius: 16px;
        padding: 20px 44px;
        font-size: 19px;
        font-weight: 700;
        min-height: 60px;
        min-width: 200px;
    }}
    QPushButton#primary:hover {{
        background: {c['accent_hover']};
    }}
    QPushButton#primary:disabled {{
        background: {c['text_faint']};
        color: {c['text_muted']};
    }}
    QPushButton#secondary {{
        background: transparent;
        color: {c['text_muted']};
        border: 2px solid {c['border']};
        border-radius: 14px;
        padding: 14px 28px;
        font-size: 16px;
        min-height: 48px;
    }}
    QPushButton#secondary:hover {{
        border-color: {c['accent']};
        color: {c['accent']};
    }}
    QPushButton#success {{
        background: {c['success']};
        color: {c['text_on_accent']};
        border: none;
        border-radius: 16px;
        padding: 20px 44px;
        font-size: 19px;
        font-weight: 700;
    }}
    QPushButton#danger {{
        background: transparent;
        color: {c['error']};
        border: 2px solid {c['error']};
        border-radius: 14px;
        padding: 14px 28px;
        font-size: 16px;
    }}
    QPushButton#danger:hover {{
        background: #FFF0F0;
    }}
    QPushButton#ghost {{
        background: transparent;
        color: {c['text_muted']};
        border: none;
        font-size: 15px;
        padding: 10px 16px;
        min-height: 40px;
    }}
    QPushButton#ghost:hover {{
        color: {c['accent']};
    }}
    QComboBox {{
        background: white;
        border: 2px solid {c['border']};
        border-radius: 14px;
        padding: 12px 16px;
        color: {c['text']};
        font-size: 17px;
        min-height: 24px;
    }}
    QComboBox::drop-down {{
        border: none;
        width: 32px;
    }}
    QComboBox QAbstractItemView {{
        background: white;
        border: 1px solid {c['border']};
        border-radius: 10px;
        color: {c['text']};
        selection-background-color: {c['card']};
        selection-color: {c['accent']};
        padding: 6px;
        font-size: 16px;
    }}
    QLineEdit {{
        background: white;
        border: 2px solid {c['border']};
        border-radius: 14px;
        padding: 12px 16px;
        color: {c['text']};
        font-size: 17px;
        min-height: 24px;
    }}
    QLineEdit:focus {{
        border-color: {c['accent']};
        background: #FFF8F5;
    }}
    QProgressBar {{
        background: {c['border']};
        border: none;
        border-radius: 10px;
        height: 16px;
        text-align: center;
    }}
    QProgressBar::chunk {{
        background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
            stop:0 {c['accent']}, stop:1 {c['info']});
        border-radius: 10px;
    }}
    QScrollBar:vertical {{
        background: {c['bg']};
        width: 10px;
        border-radius: 5px;
    }}
    QScrollBar::handle:vertical {{
        background: {c['text_faint']};
        border-radius: 5px;
        min-height: 30px;
    }}
    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
        height: 0;
    }}
    QTextEdit {{
        background: white;
        border: 2px solid {c['border']};
        border-radius: 14px;
        padding: 12px;
        color: {c['text_muted']};
        font-family: 'Ubuntu Mono', 'Consolas', monospace;
        font-size: 15px;
    }}
    QListWidget {{
        background: transparent;
        border: none;
    }}
    QListWidget::item {{
        padding: 4px;
        margin: 2px;
    }}
    QLabel#step_dot {{
        font-size: 14px;
    }}
    QLabel#section_title {{
        font-size: 14px;
        font-weight: 700;
        color: {c['text_muted']};
        letter-spacing: 0.5px;
        padding: 10px 0 6px 0;
    }}
    QWidget#sidebar {{
        background: white;
        border-right: 1px solid {c['border']};
    }}
    """



# Global aliases (moved from import statements)
C = WARM_PASTEL

# ══ constants.py ═══════════════════════════════════════

APP_VERSION = "1.0.0"
APP_NAME = "Espy"

HEARTBEAT_PORT = 7777
OTA_PORT = 8080
HEARTBEAT_INTERVAL = 5
OTA_CHUNK_SIZE = 1024
OTA_TIMEOUT_TOTAL = 60
POST_FLASH_HEARTBEAT_WINDOW = 15

EASY_MODE_MIN_FONT = 18
EASY_MODE_TITLE_FONT = 28
EASY_MODE_BODY_FONT = 20

BOARDS = {
    "ESP32 Dev Module": {
        "fqbn": "esp32:esp32:esp32",
        "flash_size": "4MB",
        "max_sketch_size": 1966080,
        "partitions": [
            {"name": "Bootloader", "offset": "0x1000", "size": "28 KB"},
            {"name": "Partition Table", "offset": "0x8000", "size": "32 KB"},
            {"name": "NVS", "offset": "0x9000", "size": "20 KB"},
            {"name": "OTA Data", "offset": "0xE000", "size": "8 KB"},
            {"name": "App (OTA 0)", "offset": "0x10000", "size": "1.3 MB"},
            {"name": "App (OTA 1)", "offset": "0x150000", "size": "1.3 MB"},
            {"name": "SPIFFS", "offset": "0x290000", "size": "1.4 MB"},
        ],
        "chip": "ESP32",
        "usb_vid_pid": ["10C4:EA60", "1A86:7523"],
        "form_factor": "devkit",
    },
    "NodeMCU-32S": {
        "fqbn": "esp32:esp32:nodemcu-32s",
        "flash_size": "4MB",
        "max_sketch_size": 1966080,
        "partitions": [
            {"name": "Bootloader", "offset": "0x1000", "size": "28 KB"},
            {"name": "Partition Table", "offset": "0x8000", "size": "32 KB"},
            {"name": "NVS", "offset": "0x9000", "size": "20 KB"},
            {"name": "OTA Data", "offset": "0xE000", "size": "8 KB"},
            {"name": "App (OTA 0)", "offset": "0x10000", "size": "1.3 MB"},
            {"name": "App (OTA 1)", "offset": "0x150000", "size": "1.3 MB"},
            {"name": "SPIFFS", "offset": "0x290000", "size": "1.4 MB"},
        ],
        "chip": "ESP32",
        "usb_vid_pid": ["10C4:EA60", "1A86:7523"],
        "form_factor": "nodemcu",
    },
    "ESP32-S3 DevKitC": {
        "fqbn": "esp32:esp32:esp32s3",
        "flash_size": "16MB",
        "max_sketch_size": 8388608,
        "partitions": [
            {"name": "Bootloader", "offset": "0x0000", "size": "64 KB"},
            {"name": "Partition Table", "offset": "0x8000", "size": "32 KB"},
            {"name": "NVS", "offset": "0x9000", "size": "20 KB"},
            {"name": "OTA Data", "offset": "0xE000", "size": "8 KB"},
            {"name": "App (OTA 0)", "offset": "0x10000", "size": "6.5 MB"},
            {"name": "App (OTA 1)", "offset": "0x660000", "size": "6.5 MB"},
            {"name": "LittleFS", "offset": "0xCC0000", "size": "3.2 MB"},
        ],
        "chip": "ESP32-S3",
        "usb_vid_pid": ["303A:1001", "303A:0002"],
        "form_factor": "devkit",
    },
    "ESP32-C3 DevKit": {
        "fqbn": "esp32:esp32:esp32c3",
        "flash_size": "4MB",
        "max_sketch_size": 1966080,
        "partitions": [
            {"name": "Bootloader", "offset": "0x0000", "size": "28 KB"},
            {"name": "Partition Table", "offset": "0x8000", "size": "32 KB"},
            {"name": "NVS", "offset": "0x9000", "size": "20 KB"},
            {"name": "OTA Data", "offset": "0xE000", "size": "8 KB"},
            {"name": "App (OTA 0)", "offset": "0x10000", "size": "1.3 MB"},
            {"name": "App (OTA 1)", "offset": "0x150000", "size": "1.3 MB"},
            {"name": "SPIFFS", "offset": "0x290000", "size": "1.4 MB"},
        ],
        "chip": "ESP32-C3",
        "usb_vid_pid": ["303A:1001"],
        "form_factor": "devkit",
    },
    "ESP32-S2 Saola": {
        "fqbn": "esp32:esp32:esp32s2",
        "flash_size": "4MB",
        "max_sketch_size": 1966080,
        "partitions": [
            {"name": "Bootloader", "offset": "0x1000", "size": "28 KB"},
            {"name": "Partition Table", "offset": "0x8000", "size": "32 KB"},
            {"name": "NVS", "offset": "0x9000", "size": "20 KB"},
            {"name": "OTA Data", "offset": "0xE000", "size": "8 KB"},
            {"name": "App (OTA 0)", "offset": "0x10000", "size": "1.3 MB"},
            {"name": "App (OTA 1)", "offset": "0x150000", "size": "1.3 MB"},
            {"name": "SPIFFS", "offset": "0x290000", "size": "1.4 MB"},
        ],
        "chip": "ESP32-S2",
        "usb_vid_pid": ["303A:0002", "303A:0001"],
        "form_factor": "devkit",
    },
    "ESP32-C6 Dev Module": {
        "fqbn": "esp32:esp32:esp32c6",
        "flash_size": "4MB",
        "max_sketch_size": 1310720,
        "partitions": [
            {"name": "Bootloader", "offset": "0x0000", "size": "28 KB"},
            {"name": "Partition Table", "offset": "0x8000", "size": "32 KB"},
            {"name": "NVS", "offset": "0x9000", "size": "20 KB"},
            {"name": "OTA Data", "offset": "0xE000", "size": "8 KB"},
            {"name": "App (OTA 0)", "offset": "0x10000", "size": "1.3 MB"},
            {"name": "App (OTA 1)", "offset": "0x150000", "size": "1.3 MB"},
            {"name": "SPIFFS", "offset": "0x290000", "size": "1.4 MB"},
        ],
        "chip": "ESP32-C6",
        "usb_vid_pid": ["303A:1001"],
        "form_factor": "devkit",
    },
    "ESP32-H2 Dev Module": {
        "fqbn": "esp32:esp32:esp32h2",
        "flash_size": "4MB",
        "max_sketch_size": 1310720,
        "partitions": [
            {"name": "Bootloader", "offset": "0x0000", "size": "28 KB"},
            {"name": "Partition Table", "offset": "0x8000", "size": "32 KB"},
            {"name": "NVS", "offset": "0x9000", "size": "20 KB"},
            {"name": "OTA Data", "offset": "0xE000", "size": "8 KB"},
            {"name": "App (OTA 0)", "offset": "0x10000", "size": "1.3 MB"},
            {"name": "App (OTA 1)", "offset": "0x150000", "size": "1.3 MB"},
            {"name": "SPIFFS", "offset": "0x290000", "size": "1.4 MB"},
        ],
        "chip": "ESP32-H2",
        "usb_vid_pid": ["303A:1001"],
        "form_factor": "devkit",
    },
}

if sys.platform == "linux":
    APP_DIR = Path.home() / ".config" / "espy"
    USB_PORT_PATTERNS = ("ttyUSB", "ttyACM")
    SYSTEM_FONT = "'Ubuntu', 'Noto Sans', system-ui, sans-serif"
    MONO_FONT = "'Ubuntu Mono', 'Consolas', monospace"
elif sys.platform == "win32":
    APP_DIR = Path.home() / "AppData" / "Local" / "Espy"
    USB_PORT_PATTERNS = ("COM",)
    SYSTEM_FONT = "'Segoe UI', system-ui, sans-serif"
    MONO_FONT = "'Consolas', 'Courier New', monospace"
else:
    APP_DIR = Path.home() / ".config" / "espy"
    USB_PORT_PATTERNS = ("ttyUSB", "ttyACM")
    SYSTEM_FONT = "system-ui, sans-serif"
    MONO_FONT = "monospace"

APP_DIR.mkdir(parents=True, exist_ok=True)
BACKUP_DIR = APP_DIR / "backups"
BACKUP_DIR.mkdir(exist_ok=True)
CACHE_FILE = APP_DIR / "devices.json"

FIRST_RUN_FILE = APP_DIR / "onboarding_done"
MODE_PREF_FILE = APP_DIR / "mode_pref"

# Partition schemes for each flash size.
# Each entry: label -> (description, [partition_dicts])
PARTITION_SCHEMES = {
    "4MB": {
        "default_ota": (
            "Default (OTA)",
            "Two OTA slots + SPIFFS — standard for wireless updates",
            [
                {"name": "Bootloader", "offset": "0x1000", "size": "28 KB"},
                {"name": "Partition Table", "offset": "0x8000", "size": "32 KB"},
                {"name": "NVS", "offset": "0x9000", "size": "20 KB"},
                {"name": "OTA Data", "offset": "0xE000", "size": "8 KB"},
                {"name": "App (OTA 0)", "offset": "0x10000", "size": "1.3 MB"},
                {"name": "App (OTA 1)", "offset": "0x150000", "size": "1.3 MB"},
                {"name": "SPIFFS", "offset": "0x290000", "size": "1.4 MB"},
            ],
        ),
        "no_ota": (
            "No OTA",
            "Single large app + more space for data — best if you only flash via USB",
            [
                {"name": "Bootloader", "offset": "0x1000", "size": "28 KB"},
                {"name": "Partition Table", "offset": "0x8000", "size": "32 KB"},
                {"name": "NVS", "offset": "0x9000", "size": "20 KB"},
                {"name": "App", "offset": "0x10000", "size": "2.6 MB"},
                {"name": "SPIFFS", "offset": "0x2A0000", "size": "1.3 MB"},
            ],
        ),
        "large_data": (
            "Large Data",
            "OTA-capable but with a bigger SPIFFS/LittleFS partition",
            [
                {"name": "Bootloader", "offset": "0x1000", "size": "28 KB"},
                {"name": "Partition Table", "offset": "0x8000", "size": "32 KB"},
                {"name": "NVS", "offset": "0x9000", "size": "20 KB"},
                {"name": "OTA Data", "offset": "0xE000", "size": "8 KB"},
                {"name": "App (OTA 0)", "offset": "0x10000", "size": "0.9 MB"},
                {"name": "App (OTA 1)", "offset": "0x100000", "size": "0.9 MB"},
                {"name": "SPIFFS", "offset": "0x1F0000", "size": "1.9 MB"},
            ],
        ),
        "minimal": (
            "Minimal",
            "No OTA, no filesystem — maximum space for a single app",
            [
                {"name": "Bootloader", "offset": "0x1000", "size": "28 KB"},
                {"name": "Partition Table", "offset": "0x8000", "size": "32 KB"},
                {"name": "NVS", "offset": "0x9000", "size": "20 KB"},
                {"name": "App", "offset": "0x10000", "size": "3.9 MB"},
            ],
        ),
    },
    "8MB": {
        "default_ota": (
            "Default (OTA)",
            "Two OTA slots + SPIFFS for 8MB flash",
            [
                {"name": "Bootloader", "offset": "0x1000", "size": "28 KB"},
                {"name": "Partition Table", "offset": "0x8000", "size": "32 KB"},
                {"name": "NVS", "offset": "0x9000", "size": "20 KB"},
                {"name": "OTA Data", "offset": "0xE000", "size": "8 KB"},
                {"name": "App (OTA 0)", "offset": "0x10000", "size": "2.9 MB"},
                {"name": "App (OTA 1)", "offset": "0x2F0000", "size": "2.9 MB"},
                {"name": "SPIFFS", "offset": "0x5D0000", "size": "1.9 MB"},
            ],
        ),
        "no_ota": (
            "No OTA",
            "Single large app + 4 MB data partition",
            [
                {"name": "Bootloader", "offset": "0x1000", "size": "28 KB"},
                {"name": "Partition Table", "offset": "0x8000", "size": "32 KB"},
                {"name": "NVS", "offset": "0x9000", "size": "20 KB"},
                {"name": "App", "offset": "0x10000", "size": "3.9 MB"},
                {"name": "SPIFFS", "offset": "0x400000", "size": "3.9 MB"},
            ],
        ),
        "large_data": (
            "Large Data",
            "OTA + 3.8 MB data partition",
            [
                {"name": "Bootloader", "offset": "0x1000", "size": "28 KB"},
                {"name": "Partition Table", "offset": "0x8000", "size": "32 KB"},
                {"name": "NVS", "offset": "0x9000", "size": "20 KB"},
                {"name": "OTA Data", "offset": "0xE000", "size": "8 KB"},
                {"name": "App (OTA 0)", "offset": "0x10000", "size": "1.9 MB"},
                {"name": "App (OTA 1)", "offset": "0x1F0000", "size": "1.9 MB"},
                {"name": "SPIFFS", "offset": "0x3D0000", "size": "3.8 MB"},
            ],
        ),
    },
    "16MB": {
        "default_ota": (
            "Default (OTA)",
            "Two OTA slots + LittleFS for 16MB flash",
            [
                {"name": "Bootloader", "offset": "0x0000", "size": "64 KB"},
                {"name": "Partition Table", "offset": "0x8000", "size": "32 KB"},
                {"name": "NVS", "offset": "0x9000", "size": "20 KB"},
                {"name": "OTA Data", "offset": "0xE000", "size": "8 KB"},
                {"name": "App (OTA 0)", "offset": "0x10000", "size": "6.5 MB"},
                {"name": "App (OTA 1)", "offset": "0x660000", "size": "6.5 MB"},
                {"name": "LittleFS", "offset": "0xCC0000", "size": "3.2 MB"},
            ],
        ),
        "no_ota": (
            "No OTA",
            "Single massive app + 8 MB data",
            [
                {"name": "Bootloader", "offset": "0x0000", "size": "64 KB"},
                {"name": "Partition Table", "offset": "0x8000", "size": "32 KB"},
                {"name": "NVS", "offset": "0x9000", "size": "20 KB"},
                {"name": "App", "offset": "0x10000", "size": "7.9 MB"},
                {"name": "LittleFS", "offset": "0x800000", "size": "7.9 MB"},
            ],
        ),
        "large_data": (
            "Large Data",
            "OTA + 6 MB LittleFS partition",
            [
                {"name": "Bootloader", "offset": "0x0000", "size": "64 KB"},
                {"name": "Partition Table", "offset": "0x8000", "size": "32 KB"},
                {"name": "NVS", "offset": "0x9000", "size": "20 KB"},
                {"name": "OTA Data", "offset": "0xE000", "size": "8 KB"},
                {"name": "App (OTA 0)", "offset": "0x10000", "size": "4.9 MB"},
                {"name": "App (OTA 1)", "offset": "0x4F8000", "size": "4.9 MB"},
                {"name": "LittleFS", "offset": "0x9DF000", "size": "6.1 MB"},
            ],
        ),
    },
}


def get_default_scheme(flash_size: str) -> str:
    """Return the partition scheme key for the default for a given flash size."""
    return "default_ota"


def get_scheme_partitions(flash_size: str, scheme_key: str) -> list[dict]:
    """Resolve partition list for a flash_size + scheme_key. Falls back to default."""
    sizes = PARTITION_SCHEMES.get(flash_size)
    if not sizes:
        return []
    scheme = sizes.get(scheme_key)
    if not scheme:
        scheme_key = get_default_scheme(flash_size)
        scheme = sizes.get(scheme_key)
    return scheme[2] if scheme else []


TOP_LIBRARIES = [
    "DHT sensor library",
    "Adafruit Unified Sensor",
    "PubSubClient",
    "ArduinoJson",
    "Adafruit SSD1306",
    "Adafruit GFX Library",
    "WiFi",
    "WebServer",
    "ESPmDNS",
    "Update",
    "Preferences",
    "LittleFS",
    "SD",
    "SPI",
    "Wire",
    "Adafruit NeoPixel",
    "FastLED",
    "Servo",
    "OneWire",
    "DallasTemperature",
]


# ══ models.py ═══════════════════════════════════════

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


# ══ discovery/usb.py ═══════════════════════════════════════

USB_VENDORS_WHITELIST = (
    0x10C4,  # Silicon Labs CP210x
    0x1A86,  # QinHeng CH340/CH341
    0x0403,  # FTDI
    0x303A,  # Espressif USB-JTAG-Serial
    0x239A,  # Adafruit
)

def usb_probe() -> list[dict]:
    """Find ESP32 devices connected via USB.
    Returns list of {port, description, device_name}.
    """
    results: list[dict] = []
    try:
        import serial.tools.list_ports
        for p in serial.tools.list_ports.comports():
            # Prefer VID/PID check when available (most reliable)
            if p.vid is not None and p.vid in USB_VENDORS_WHITELIST:
                results.append({
                    "port": p.device,
                    "description": p.description,
                    "device_name": "",
                })
                continue
            # Fallback: description keyword match
            desc = (p.description or "").lower()
            if any(k in desc for k in
                   ("cp210", "ch340", "ch341", "ftdi",
                    "esp32", "silicon", "uart")):
                results.append({
                    "port": p.device,
                    "description": p.description,
                    "device_name": "",
                })
                continue
        # Last fallback: port name pattern (only if nothing found yet)
        if not results:
            for p in serial.tools.list_ports.comports():
                port_name = p.device
                if any(pattern in port_name for pattern in USB_PORT_PATTERNS):
                    results.append({
                        "port": p.device,
                        "description": p.description,
                        "device_name": "",
                    })
    except ImportError:
        pass
    return results

def autodetect_port() -> Optional[str]:
    ports = usb_probe()
    return ports[0]["port"] if ports else None

def auto_detect_all() -> list[str]:
    return [p["port"] for p in usb_probe()]


# ══ ui/illustrations.py ═══════════════════════════════════════

def _c(name: str, fallback: str = "#DDD") -> str:
    return C.get(name, fallback)

def espy_glasses(size: int = 140) -> str:
    return f"""<svg width="{size}" height="{size}" viewBox="0 0 140 160">
  <path d="M70 10 Q70 -5 85 -10" stroke="{_c('accent')}" stroke-width="2.5" fill="none" stroke-linecap="round"/>
  <circle cx="86" cy="-10" r="5" fill="{_c('accent')}"/>
  <rect x="15" y="35" width="110" height="70" rx="28" fill="{_c('esp_skin')}" stroke="{_c('border')}" stroke-width="2"/>
  <circle cx="48" cy="65" r="16" fill="none" stroke="{_c('accent')}" stroke-width="2.5"/>
  <circle cx="92" cy="65" r="16" fill="none" stroke="{_c('accent')}" stroke-width="2.5"/>
  <line x1="64" y1="65" x2="76" y2="65" stroke="{_c('accent')}" stroke-width="2.5"/>
  <circle cx="48" cy="65" r="5" fill="{_c('esp_eye')}"/>
  <circle cx="92" cy="65" r="5" fill="{_c('esp_eye')}"/>
  <circle cx="50" cy="63" r="2" fill="white"/>
  <circle cx="94" cy="63" r="2" fill="white"/>
  <ellipse cx="32" cy="78" rx="8" ry="5" fill="#FFB5B5" opacity="0.6"/>
  <ellipse cx="108" cy="78" rx="8" ry="5" fill="#FFB5B5" opacity="0.6"/>
  <path d="M55 83 Q70 95 85 83" stroke="{_c('accent')}" stroke-width="2.5" fill="none" stroke-linecap="round"/>
  <rect x="30" y="105" width="12" height="10" rx="3" fill="{_c('border')}"/>
  <rect x="50" y="105" width="12" height="10" rx="3" fill="{_c('border')}"/>
  <rect x="70" y="105" width="12" height="10" rx="3" fill="{_c('border')}"/>
  <rect x="90" y="105" width="12" height="10" rx="3" fill="{_c('border')}"/>
</svg>"""

def espy_happy(size: int = 140) -> str:
    return f"""<svg width="{size}" height="{size}" viewBox="0 0 140 160">
  <path d="M70 10 Q70 -5 88 -10" stroke="{_c('accent')}" stroke-width="2.5" fill="none" stroke-linecap="round"/>
  <circle cx="89" cy="-10" r="5" fill="{_c('accent')}"/>
  <rect x="15" y="35" width="110" height="70" rx="28" fill="{_c('esp_skin')}" stroke="{_c('border')}" stroke-width="2"/>
  <circle cx="48" cy="65" r="16" fill="none" stroke="{_c('accent')}" stroke-width="2.5"/>
  <circle cx="92" cy="65" r="16" fill="none" stroke="{_c('accent')}" stroke-width="2.5"/>
  <line x1="64" y1="65" x2="76" y2="65" stroke="{_c('accent')}" stroke-width="2.5"/>
  <circle cx="48" cy="65" r="5" fill="{_c('esp_eye')}"/>
  <circle cx="92" cy="65" r="5" fill="{_c('esp_eye')}"/>
  <circle cx="50" cy="63" r="2" fill="white"/>
  <circle cx="94" cy="63" r="2" fill="white"/>
  <ellipse cx="32" cy="78" rx="8" ry="5" fill="#FFB5B5" opacity="0.6"/>
  <ellipse cx="108" cy="78" rx="8" ry="5" fill="#FFB5B5" opacity="0.6"/>
  <path d="M50 83 Q70 102 90 83" stroke="{_c('accent')}" stroke-width="2.5" fill="none" stroke-linecap="round"/>
  <rect x="30" y="105" width="12" height="10" rx="3" fill="{_c('border')}"/>
  <rect x="50" y="105" width="12" height="10" rx="3" fill="{_c('border')}"/>
  <rect x="70" y="105" width="12" height="10" rx="3" fill="{_c('border')}"/>
  <rect x="90" y="105" width="12" height="10" rx="3" fill="{_c('border')}"/>
</svg>"""

def espy_wink(size: int = 140) -> str:
    return f"""<svg width="{size}" height="{size}" viewBox="0 0 140 160">
  <path d="M70 10 Q70 -5 90 -8" stroke="{_c('accent')}" stroke-width="2.5" fill="none" stroke-linecap="round"/>
  <circle cx="91" cy="-8" r="5" fill="{_c('accent')}"/>
  <rect x="15" y="35" width="110" height="70" rx="28" fill="{_c('esp_skin')}" stroke="{_c('border')}" stroke-width="2"/>
  <circle cx="48" cy="65" r="16" fill="none" stroke="{_c('accent')}" stroke-width="2.5"/>
  <circle cx="92" cy="65" r="16" fill="none" stroke="{_c('accent')}" stroke-width="2.5"/>
  <line x1="64" y1="65" x2="76" y2="65" stroke="{_c('accent')}" stroke-width="2.5"/>
  <circle cx="48" cy="65" r="5" fill="{_c('esp_eye')}"/>
  <circle cx="50" cy="63" r="2" fill="white"/>
  <line x1="87" y1="65" x2="97" y2="65" stroke="{_c('esp_eye')}" stroke-width="2.5" stroke-linecap="round"/>
  <ellipse cx="32" cy="78" rx="8" ry="5" fill="#FFB5B5" opacity="0.6"/>
  <ellipse cx="108" cy="78" rx="8" ry="5" fill="#FFB5B5" opacity="0.6"/>
  <path d="M55 83 Q70 95 85 83" stroke="{_c('accent')}" stroke-width="2.5" fill="none" stroke-linecap="round"/>
  <rect x="30" y="105" width="12" height="10" rx="3" fill="{_c('border')}"/>
  <rect x="50" y="105" width="12" height="10" rx="3" fill="{_c('border')}"/>
  <rect x="70" y="105" width="12" height="10" rx="3" fill="{_c('border')}"/>
  <rect x="90" y="105" width="12" height="10" rx="3" fill="{_c('border')}"/>
</svg>"""

def espy_surprise(size: int = 140) -> str:
    return f"""<svg width="{size}" height="{size}" viewBox="0 0 140 160">
  <path d="M70 10 Q70 -5 86 -12" stroke="{_c('accent')}" stroke-width="2.5" fill="none" stroke-linecap="round"/>
  <circle cx="87" cy="-12" r="5" fill="{_c('accent')}"/>
  <rect x="15" y="35" width="110" height="70" rx="28" fill="{_c('esp_skin')}" stroke="{_c('border')}" stroke-width="2"/>
  <circle cx="48" cy="65" r="16" fill="none" stroke="{_c('accent')}" stroke-width="2.5"/>
  <circle cx="92" cy="65" r="16" fill="none" stroke="{_c('accent')}" stroke-width="2.5"/>
  <line x1="64" y1="65" x2="76" y2="65" stroke="{_c('accent')}" stroke-width="2.5"/>
  <circle cx="48" cy="65" r="7" fill="{_c('esp_eye')}"/>
  <circle cx="92" cy="65" r="7" fill="{_c('esp_eye')}"/>
  <circle cx="50" cy="63" r="2.5" fill="white"/>
  <circle cx="94" cy="63" r="2.5" fill="white"/>
  <ellipse cx="32" cy="78" rx="8" ry="5" fill="#FFB5B5" opacity="0.6"/>
  <ellipse cx="108" cy="78" rx="8" ry="5" fill="#FFB5B5" opacity="0.6"/>
  <ellipse cx="70" cy="90" rx="8" ry="6" fill="none" stroke="{_c('accent')}" stroke-width="2"/>
  <rect x="30" y="105" width="12" height="10" rx="3" fill="{_c('border')}"/>
  <rect x="50" y="105" width="12" height="10" rx="3" fill="{_c('border')}"/>
  <rect x="70" y="105" width="12" height="10" rx="3" fill="{_c('border')}"/>
  <rect x="90" y="105" width="12" height="10" rx="3" fill="{_c('border')}"/>
</svg>"""

def espy_sad(size: int = 140) -> str:
    return f"""<svg width="{size}" height="{size}" viewBox="0 0 140 160">
  <path d="M70 10 Q70 0 80 5" stroke="{_c('accent')}" stroke-width="2.5" fill="none" stroke-linecap="round"/>
  <circle cx="81" cy="5" r="5" fill="{_c('accent')}" opacity="0.6"/>
  <rect x="15" y="35" width="110" height="70" rx="28" fill="{_c('esp_skin')}" stroke="{_c('border')}" stroke-width="2"/>
  <circle cx="48" cy="65" r="16" fill="none" stroke="{_c('accent')}" stroke-width="2" opacity="0.7"/>
  <circle cx="92" cy="65" r="16" fill="none" stroke="{_c('accent')}" stroke-width="2" opacity="0.7"/>
  <line x1="64" y1="65" x2="76" y2="65" stroke="{_c('accent')}" stroke-width="2" opacity="0.7"/>
  <ellipse cx="48" cy="68" rx="5" ry="4" fill="{_c('esp_eye')}" opacity="0.6"/>
  <ellipse cx="92" cy="68" rx="5" ry="4" fill="{_c('esp_eye')}" opacity="0.6"/>
  <ellipse cx="32" cy="78" rx="8" ry="5" fill="#FFB5B5" opacity="0.3"/>
  <ellipse cx="108" cy="78" rx="8" ry="5" fill="#FFB5B5" opacity="0.3"/>
  <path d="M55 92 Q70 82 85 92" stroke="{_c('accent')}" stroke-width="2.5" fill="none" stroke-linecap="round" opacity="0.7"/>
  <rect x="30" y="105" width="12" height="10" rx="3" fill="{_c('border')}"/>
  <rect x="50" y="105" width="12" height="10" rx="3" fill="{_c('border')}"/>
  <rect x="70" y="105" width="12" height="10" rx="3" fill="{_c('border')}"/>
  <rect x="90" y="105" width="12" height="10" rx="3" fill="{_c('border')}"/>
</svg>"""

def espy_searching(size: int = 140) -> str:
    return f"""<svg width="{size}" height="{size}" viewBox="0 0 140 160">
  <path d="M70 10 Q60 -2 50 -5" stroke="{_c('accent')}" stroke-width="2.5" fill="none" stroke-linecap="round"/>
  <circle cx="49" cy="-6" r="5" fill="{_c('accent')}"/>
  <rect x="15" y="35" width="110" height="70" rx="28" fill="{_c('esp_skin')}" stroke="{_c('border')}" stroke-width="2"/>
  <circle cx="48" cy="65" r="16" fill="none" stroke="{_c('accent')}" stroke-width="2.5"/>
  <circle cx="92" cy="65" r="16" fill="none" stroke="{_c('accent')}" stroke-width="2.5"/>
  <line x1="64" y1="65" x2="76" y2="65" stroke="{_c('accent')}" stroke-width="2.5"/>
  <circle cx="44" cy="65" r="5" fill="{_c('esp_eye')}"/>
  <circle cx="46" cy="63" r="2" fill="white"/>
  <circle cx="88" cy="65" r="5" fill="{_c('esp_eye')}"/>
  <circle cx="90" cy="63" r="2" fill="white"/>
  <line x1="80" y1="58" x2="98" y2="58" stroke="{_c('accent')}" stroke-width="1.5" stroke-linecap="round" opacity="0.4"/>
  <line x1="80" y1="65" x2="98" y2="65" stroke="{_c('accent')}" stroke-width="1.5" stroke-linecap="round" opacity="0.7"/>
  <line x1="80" y1="72" x2="98" y2="72" stroke="{_c('accent')}" stroke-width="1.5" stroke-linecap="round" opacity="0.4"/>
  <ellipse cx="32" cy="78" rx="8" ry="5" fill="#FFB5B5" opacity="0.5"/>
  <ellipse cx="108" cy="78" rx="8" ry="5" fill="#FFB5B5" opacity="0.5"/>
  <path d="M55 83 Q70 95 85 83" stroke="{_c('accent')}" stroke-width="2.5" fill="none" stroke-linecap="round"/>
  <rect x="30" y="105" width="12" height="10" rx="3" fill="{_c('border')}"/>
  <rect x="50" y="105" width="12" height="10" rx="3" fill="{_c('border')}"/>
  <rect x="70" y="105" width="12" height="10" rx="3" fill="{_c('border')}"/>
  <rect x="90" y="105" width="12" height="10" rx="3" fill="{_c('border')}"/>
</svg>"""

def espy_focused(size: int = 140) -> str:
    return f"""<svg width="{size}" height="{size}" viewBox="0 0 140 160">
  <path d="M70 10 Q72 -5 88 -8" stroke="{_c('accent')}" stroke-width="2.5" fill="none" stroke-linecap="round"/>
  <circle cx="89" cy="-8" r="5" fill="{_c('accent')}"/>
  <rect x="15" y="35" width="110" height="70" rx="28" fill="{_c('esp_skin')}" stroke="{_c('border')}" stroke-width="2"/>
  <circle cx="48" cy="65" r="16" fill="none" stroke="{_c('accent')}" stroke-width="2.5"/>
  <circle cx="92" cy="65" r="16" fill="none" stroke="{_c('accent')}" stroke-width="2.5"/>
  <line x1="64" y1="65" x2="76" y2="65" stroke="{_c('accent')}" stroke-width="2.5"/>
  <line x1="36" y1="50" x2="48" y2="53" stroke="{_c('accent')}" stroke-width="2.5" stroke-linecap="round"/>
  <line x1="92" y1="53" x2="104" y2="50" stroke="{_c('accent')}" stroke-width="2.5" stroke-linecap="round"/>
  <ellipse cx="48" cy="65" rx="5" ry="3.5" fill="{_c('esp_eye')}"/>
  <ellipse cx="92" cy="65" rx="5" ry="3.5" fill="{_c('esp_eye')}"/>
  <circle cx="50" cy="64" r="1.5" fill="white"/>
  <circle cx="94" cy="64" r="1.5" fill="white"/>
  <ellipse cx="32" cy="78" rx="8" ry="5" fill="#FFB5B5" opacity="0.5"/>
  <ellipse cx="108" cy="78" rx="8" ry="5" fill="#FFB5B5" opacity="0.5"/>
  <line x1="58" y1="85" x2="82" y2="85" stroke="{_c('accent')}" stroke-width="2.5" stroke-linecap="round"/>
  <rect x="30" y="105" width="12" height="10" rx="3" fill="{_c('border')}"/>
  <rect x="50" y="105" width="12" height="10" rx="3" fill="{_c('border')}"/>
  <rect x="70" y="105" width="12" height="10" rx="3" fill="{_c('border')}"/>
  <rect x="90" y="105" width="12" height="10" rx="3" fill="{_c('border')}"/>
</svg>"""

def espy_sweat(size: int = 140) -> str:
    return f"""<svg width="{size}" height="{size}" viewBox="0 0 140 160">
  <path d="M70 10 Q70 -5 86 -12" stroke="{_c('accent')}" stroke-width="2.5" fill="none" stroke-linecap="round"/>
  <circle cx="87" cy="-12" r="5" fill="{_c('accent')}"/>
  <rect x="15" y="35" width="110" height="70" rx="28" fill="{_c('esp_skin')}" stroke="{_c('border')}" stroke-width="2"/>
  <circle cx="48" cy="65" r="16" fill="none" stroke="{_c('accent')}" stroke-width="2.5"/>
  <circle cx="92" cy="65" r="16" fill="none" stroke="{_c('accent')}" stroke-width="2.5"/>
  <line x1="64" y1="65" x2="76" y2="65" stroke="{_c('accent')}" stroke-width="2.5"/>
  <circle cx="48" cy="65" r="5" fill="{_c('esp_eye')}"/>
  <circle cx="50" cy="63" r="2" fill="white"/>
  <line x1="87" y1="65" x2="97" y2="65" stroke="{_c('esp_eye')}" stroke-width="2.5" stroke-linecap="round"/>
  <path d="M108 42 Q112 48 108 52 Q104 48 108 42Z" fill="{_c('info')}" opacity="0.7"/>
  <ellipse cx="32" cy="78" rx="8" ry="5" fill="#FFB5B5" opacity="0.5"/>
  <ellipse cx="108" cy="78" rx="8" ry="5" fill="#FFB5B5" opacity="0.5"/>
  <path d="M55 83 Q70 95 85 83" stroke="{_c('accent')}" stroke-width="2.5" fill="none" stroke-linecap="round"/>
  <rect x="30" y="105" width="12" height="10" rx="3" fill="{_c('border')}"/>
  <rect x="50" y="105" width="12" height="10" rx="3" fill="{_c('border')}"/>
  <rect x="70" y="105" width="12" height="10" rx="3" fill="{_c('border')}"/>
  <rect x="90" y="105" width="12" height="10" rx="3" fill="{_c('border')}"/>
</svg>"""

def espy_excited(size: int = 140) -> str:
    return f"""<svg width="{size}" height="{size}" viewBox="0 0 140 160">
  <path d="M70 10 Q72 -8 92 -12" stroke="{_c('accent')}" stroke-width="2.5" fill="none" stroke-linecap="round"/>
  <circle cx="93" cy="-12" r="5" fill="{_c('accent')}"/>
  <rect x="15" y="35" width="110" height="70" rx="28" fill="{_c('esp_skin')}" stroke="{_c('border')}" stroke-width="2"/>
  <circle cx="48" cy="65" r="16" fill="none" stroke="{_c('accent')}" stroke-width="2.5"/>
  <circle cx="92" cy="65" r="16" fill="none" stroke="{_c('accent')}" stroke-width="2.5"/>
  <line x1="64" y1="65" x2="76" y2="65" stroke="{_c('accent')}" stroke-width="2.5"/>
  <text x="48" y="69" font-size="14" fill="{_c('warning')}" text-anchor="middle">★</text>
  <text x="92" y="69" font-size="14" fill="{_c('warning')}" text-anchor="middle">★</text>
  <ellipse cx="32" cy="78" rx="8" ry="5" fill="#FFB5B5" opacity="0.8"/>
  <ellipse cx="108" cy="78" rx="8" ry="5" fill="#FFB5B5" opacity="0.8"/>
  <path d="M50 83 Q70 108 90 83" stroke="{_c('accent')}" stroke-width="2.5" fill="none" stroke-linecap="round"/>
  <ellipse cx="70" cy="90" rx="8" ry="5" fill="{_c('accent')}" opacity="0.15"/>
  <text x="20" y="42" font-size="12" fill="{_c('warning')}" opacity="0.6">✦</text>
  <text x="112" y="50" font-size="10" fill="{_c('warning')}" opacity="0.6">✦</text>
  <text x="16" y="50" font-size="8" fill="{_c('warning')}" opacity="0.4">✦</text>
  <rect x="30" y="105" width="12" height="10" rx="3" fill="{_c('border')}"/>
  <rect x="50" y="105" width="12" height="10" rx="3" fill="{_c('border')}"/>
  <rect x="70" y="105" width="12" height="10" rx="3" fill="{_c('border')}"/>
  <rect x="90" y="105" width="12" height="10" rx="3" fill="{_c('border')}"/>
</svg>"""

def espy_peek(size: int = 80) -> str:
    s2 = size
    return f"""<svg width="{s2}" height="{s2}" viewBox="0 0 80 100">
  <path d="M40 5 Q40 -2 50 -4" stroke="{_c('accent')}" stroke-width="2" fill="none" stroke-linecap="round"/>
  <circle cx="51" cy="-4" r="3" fill="{_c('accent')}"/>
  <rect x="5" y="20" width="70" height="44" rx="18" fill="{_c('esp_skin')}" stroke="{_c('border')}" stroke-width="1.5"/>
  <circle cx="28" cy="42" r="10" fill="none" stroke="{_c('accent')}" stroke-width="2"/>
  <circle cx="52" cy="42" r="10" fill="none" stroke="{_c('accent')}" stroke-width="2"/>
  <line x1="38" y1="42" x2="42" y2="42" stroke="{_c('accent')}" stroke-width="2"/>
  <circle cx="28" cy="42" r="3.5" fill="{_c('esp_eye')}"/>
  <circle cx="52" cy="42" r="3.5" fill="{_c('esp_eye')}"/>
  <circle cx="29" cy="41" r="1.5" fill="white"/>
  <circle cx="53" cy="41" r="1.5" fill="white"/>
  <ellipse cx="16" cy="52" rx="6" ry="3" fill="#FFB5B5" opacity="0.5"/>
  <ellipse cx="64" cy="52" rx="6" ry="3" fill="#FFB5B5" opacity="0.5"/>
  <path d="M35 55 Q40 62 45 55" stroke="{_c('accent')}" stroke-width="2" fill="none" stroke-linecap="round"/>
</svg>"""

def espy_listening(size: int = 140) -> str:
    return f"""<svg width="{size}" height="{size}" viewBox="0 0 140 160">
  <path d="M70 10 Q70 -5 85 -10" stroke="{_c('accent')}" stroke-width="2.5" fill="none" stroke-linecap="round"/>
  <circle cx="86" cy="-10" r="5" fill="{_c('accent')}"/>
  <rect x="15" y="35" width="110" height="70" rx="28" fill="{_c('esp_skin')}" stroke="{_c('border')}" stroke-width="2"/>
  <circle cx="48" cy="65" r="16" fill="none" stroke="{_c('accent')}" stroke-width="2.5"/>
  <circle cx="92" cy="65" r="16" fill="none" stroke="{_c('accent')}" stroke-width="2.5"/>
  <line x1="64" y1="65" x2="76" y2="65" stroke="{_c('accent')}" stroke-width="2.5"/>
  <circle cx="48" cy="65" r="5" fill="{_c('esp_eye')}"/>
  <circle cx="92" cy="65" r="5" fill="{_c('esp_eye')}"/>
  <circle cx="50" cy="63" r="2" fill="white"/>
  <circle cx="94" cy="63" r="2" fill="white"/>
  <ellipse cx="32" cy="78" rx="8" ry="5" fill="#FFB5B5" opacity="0.5"/>
  <ellipse cx="108" cy="78" rx="8" ry="5" fill="#FFB5B5" opacity="0.5"/>
  <path d="M55 83 Q70 95 85 83" stroke="{_c('accent')}" stroke-width="2.5" fill="none" stroke-linecap="round"/>
  <rect x="30" y="105" width="12" height="10" rx="3" fill="{_c('border')}"/>
  <rect x="50" y="105" width="12" height="10" rx="3" fill="{_c('border')}"/>
  <rect x="70" y="105" width="12" height="10" rx="3" fill="{_c('border')}"/>
  <rect x="90" y="105" width="12" height="10" rx="3" fill="{_c('border')}"/>
  <path d="M115 55 Q125 50 128 42" stroke="{_c('accent')}" stroke-width="2" fill="none" stroke-linecap="round" opacity="0.5"/>
  <path d="M120 65 Q132 60 135 50" stroke="{_c('accent')}" stroke-width="2" fill="none" stroke-linecap="round" opacity="0.3"/>
</svg>"""

def usb_illustration(size: int = 160) -> str:
    return f"""<svg width="{size}" height="{size}" viewBox="0 0 160 160">
  <rect x="60" y="20" width="40" height="20" rx="4" fill="#888" stroke="#666" stroke-width="1.5"/>
  <rect x="55" y="40" width="50" height="30" rx="6" fill="#AAA" stroke="#888" stroke-width="1.5"/>
  <rect x="65" y="70" width="30" height="40" rx="4" fill="{_c('esp_skin')}" stroke="{_c('border')}" stroke-width="1.5"/>
  <rect x="55" y="110" width="50" height="30" rx="8" fill="white" stroke="{_c('accent')}" stroke-width="2"/>
  <line x1="70" y1="118" x2="70" y2="132" stroke="{_c('accent')}" stroke-width="2"/>
  <line x1="80" y1="118" x2="80" y2="132" stroke="{_c('accent')}" stroke-width="2"/>
  <line x1="90" y1="118" x2="90" y2="132" stroke="{_c('accent')}" stroke-width="2"/>
  <text x="40" y="155" font-size="11" fill="{_c('text_muted')}" text-anchor="middle">USB</text>
</svg>"""

def plug_illustration(size: int = 240) -> str:
    """Composite SVG: laptop port on left, ESP32 board on right, USB cable between.
    Shows the physical connection at realistic proportions."""
    s = size
    vw, vh = 300, 180
    # Colors
    laptop_body = "#4A4A4A"
    laptop_screen = "#2D2D2D"
    usb_plug = "#888"
    usb_cable = "#555"
    pcb_blue = "#1E3A5F"
    pcb_gold = "#FFD700"
    glow = _c('accent')
    return f"""<svg width="{s}" height="{int(s * vh / vw)}" viewBox="0 0 {vw} {vh}">
  <defs>
    <linearGradient id="cable_grad" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0%" stop-color="{usb_cable}"/>
      <stop offset="100%" stop-color="{usb_cable}"/>
    </linearGradient>
    <filter id="glow">
      <feGaussianBlur stdDeviation="2" result="blur"/>
      <feMerge><feMergeNode in="blur"/><feMergeNode in="SourceGraphic"/></feMerge>
    </filter>
  </defs>

  <!-- Laptop body (left) -->
  <rect x="10" y="50" width="70" height="45" rx="6" fill="{laptop_body}" stroke="#333" stroke-width="1.5"/>
  <rect x="15" y="55" width="60" height="25" rx="3" fill="{laptop_screen}"/>
  <rect x="35" y="82" width="20" height="4" rx="2" fill="{laptop_body}" stroke="#555" stroke-width="0.5"/>
  <!-- USB port on laptop -->
  <rect x="78" y="68" width="8" height="10" rx="1.5" fill="{usb_plug}" stroke="#666" stroke-width="0.8"/>

  <!-- USB cable -->
  <path d="M86 73 Q105 73 110 68 Q120 60 140 68 Q155 73 170 73" stroke="{usb_cable}" stroke-width="3" fill="none" stroke-linecap="round"/>
  <!-- USB connector (plug end) -->
  <rect x="168" y="66" width="14" height="16" rx="2.5" fill="{usb_plug}" stroke="#666" stroke-width="1"/>
  <rect x="170" y="69" width="10" height="10" rx="1" fill="#444"/>

  <!-- ESP32 Dev Board (right) -->
  <rect x="195" y="35" width="95" height="68" rx="4" fill="{pcb_blue}" stroke="#0D2137" stroke-width="1.5"/>
  <!-- Pin headers -->
  <rect x="195" y="35" width="18" height="68" rx="2" fill="#0D2137" opacity="0.25"/>
  <rect x="272" y="35" width="18" height="68" rx="2" fill="#0D2137" opacity="0.25"/>
  <!-- Chip package -->
  <rect x="218" y="50" width="60" height="38" rx="3" fill="#2A5A8A" stroke="#1E3A5F" stroke-width="1"/>
  <rect x="225" y="55" width="46" height="28" rx="4" fill="#C0C0C0" stroke="#888" stroke-width="1"/>
  <text x="248" y="73" font-size="7" fill="#333" text-anchor="middle" font-family="monospace">ESP32</text>
  <!-- USB port on board -->
  <rect x="248" y="90" width="14" height="8" rx="2" fill="#666" stroke="#555" stroke-width="0.8"/>
  <!-- LED -->
  <circle cx="230" cy="48" r="2" fill="{pcb_gold}"/>
  <circle cx="266" cy="48" r="2" fill="{pcb_gold}"/>

  <!-- Connection glow dot -->
  <circle cx="175" cy="74" r="4" fill="{glow}" opacity="0.6" filter="url(#glow)">
    <animate attributeName="opacity" values="0.3;0.8;0.3" dur="2s" repeatCount="indefinite"/>
  </circle>

  <text x="50" y="130" font-size="9" fill="{_c('text_muted')}" text-anchor="middle">Your Computer</text>
  <text x="242" y="130" font-size="9" fill="{_c('text_muted')}" text-anchor="middle">ESP32 Board</text>
</svg>"""

def wifi_illustration(size: int = 100) -> str:
    return f"""<svg width="{size}" height="{size}" viewBox="0 0 100 100">
  <path d="M12 45 Q50 15 88 45" stroke="{_c('accent')}" stroke-width="4" fill="none" stroke-linecap="round"/>
  <path d="M25 58 Q50 35 75 58" stroke="{_c('accent')}" stroke-width="4" fill="none" stroke-linecap="round"/>
  <path d="M38 71 Q50 55 62 71" stroke="{_c('accent')}" stroke-width="4" fill="none" stroke-linecap="round"/>
  <circle cx="50" cy="85" r="6" fill="{_c('accent')}"/>
</svg>"""

def chip_icon(size: int = 24) -> str:
    return f"""<svg width="{size}" height="{size}" viewBox="0 0 24 24">
  <rect x="3" y="3" width="18" height="18" rx="3" fill="none" stroke="{_c('text_muted')}" stroke-width="2"/>
  <rect x="7" y="7" width="10" height="10" rx="2" fill="none" stroke="{_c('text_muted')}" stroke-width="1.5"/>
  <circle cx="12" cy="12" r="2" fill="{_c('accent')}" opacity="0.6"/>
  <line x1="12" y1="3" x2="12" y2="7" stroke="{_c('text_muted')}" stroke-width="1.5"/>
  <line x1="12" y1="17" x2="12" y2="21" stroke="{_c('text_muted')}" stroke-width="1.5"/>
</svg>"""

def book_icon(size: int = 24) -> str:
    return f"""<svg width="{size}" height="{size}" viewBox="0 0 24 24">
  <rect x="4" y="2" width="16" height="20" rx="2" fill="none" stroke="{_c('text_muted')}" stroke-width="2"/>
  <line x1="12" y1="2" x2="12" y2="22" stroke="{_c('text_muted')}" stroke-width="2"/>
  <line x1="4" y1="8" x2="12" y2="8" stroke="{_c('text_muted')}" stroke-width="1.5"/>
  <line x1="4" y1="12" x2="12" y2="12" stroke="{_c('text_muted')}" stroke-width="1.5"/>
  <line x1="4" y1="16" x2="10" y2="16" stroke="{_c('text_muted')}" stroke-width="1.5"/>
</svg>"""

def drop_zone_illustration(size: int = 180) -> str:
    return f"""<svg width="{size}" height="{size}" viewBox="0 0 180 180">
  <rect x="15" y="30" width="150" height="120" rx="20" fill="none" stroke="{_c('border')}" stroke-width="3" stroke-dasharray="8 6"/>
  <path d="M90 55 L90 100 M70 80 L90 100 L110 80" stroke="{_c('accent')}" stroke-width="4" fill="none" stroke-linecap="round" stroke-linejoin="round"/>
  <rect x="55" y="105" width="70" height="8" rx="4" fill="{_c('border')}"/>
  <text x="90" y="140" font-size="13" fill="{_c('text_muted')}" text-anchor="middle">.ino</text>
</svg>"""

def onboarding_flow_svg(width: int = 360, height: int = 380) -> str:
    """Single SVG showing the 4-step Espy lifecycle.
    Vertical timeline with icons and short plain-English labels."""
    c = _c('accent')
    s = _c('success')
    m = _c('text_muted')
    t = _c('text')
    sk = _c('esp_skin')
    return f"""<svg width="{width}" height="{height}" viewBox="0 0 {width} {height}" xmlns="http://www.w3.org/2000/svg">
  <style>
    .step-num {{ font: bold 14px sans-serif; fill: white; }}
    .step-title {{ font: bold 16px sans-serif; fill: {t}; }}
    .step-desc {{ font: 13px sans-serif; fill: {m}; }}
    .connective {{ font: 11px sans-serif; fill: {m}; }}
  </style>

  <!-- Step 1: Plug USB -->
  <rect x="40" y="10" width="28" height="28" rx="14" fill="{c}"/>
  <text x="54" y="30" text-anchor="middle" class="step-num">1</text>
  <text x="80" y="28" class="step-title">Plug in via USB</text>
  <text x="80" y="46" class="step-desc">Connect your ESP32 to this computer once.</text>
  <!-- USB icon -->
  <rect x="60" y="58" width="28" height="12" rx="2" fill="#AAA" stroke="#888" stroke-width="1"/>
  <rect x="70" y="70" width="8" height="10" rx="1.5" fill="#888"/>
  <rect x="80" y="58" width="16" height="12" rx="2" fill="{sk}" stroke="{m}" stroke-width="0.8"/>

  <!-- Arrow down -->
  <line x1="54" y1="82" x2="54" y2="105" stroke="{c}" stroke-width="2" stroke-dasharray="4 3"/>
  <polygon points="54,105 50,97 58,97" fill="{c}"/>

  <!-- Step 2: Connect Wi-Fi -->
  <rect x="40" y="110" width="28" height="28" rx="14" fill="{c}"/>
  <text x="54" y="130" text-anchor="middle" class="step-num">2</text>
  <text x="80" y="128" class="step-title">Connect to Wi-Fi</text>
  <text x="80" y="146" class="step-desc">Your ESP32 joins your home network.</text>
  <!-- Wi-Fi icon -->
  <path d="M55 160 Q70 148 85 160" stroke="{c}" stroke-width="2" fill="none" stroke-linecap="round"/>
  <path d="M60 167 Q70 158 80 167" stroke="{c}" stroke-width="2" fill="none" stroke-linecap="round"/>
  <circle cx="70" cy="176" r="3" fill="{c}"/>

  <!-- Arrow down -->
  <line x1="54" y1="182" x2="54" y2="205" stroke="{c}" stroke-width="2" stroke-dasharray="4 3"/>
  <polygon points="54,205 50,197 58,197" fill="{c}"/>

  <!-- Step 3: Drop .ino -->
  <rect x="40" y="210" width="28" height="28" rx="14" fill="{c}"/>
  <text x="54" y="230" text-anchor="middle" class="step-num">3</text>
  <text x="80" y="228" class="step-title">Drop your code</text>
  <text x="80" y="246" class="step-desc">Drag any .ino file onto Espy.</text>
  <!-- Drop icon -->
  <rect x="58" y="258" width="24" height="20" rx="4" fill="none" stroke="{c}" stroke-width="1.5" stroke-dasharray="3 2"/>
  <path d="M70 260 L70 272 M64 267 L70 272 L76 267" stroke="{c}" stroke-width="2" fill="none" stroke-linecap="round"/>
  <text x="70" y="280" font-size="7" fill="{m}" text-anchor="middle">.ino</text>

  <!-- Arrow down -->
  <line x1="54" y1="285" x2="54" y2="308" stroke="{c}" stroke-width="2" stroke-dasharray="4 3"/>
  <polygon points="54,308 50,300 58,300" fill="{c}"/>

  <!-- Step 4: Done! -->
  <rect x="40" y="315" width="28" height="28" rx="14" fill="{s}"/>
  <path d="M48 329 L53 334 L62 323" stroke="white" stroke-width="2.5" fill="none" stroke-linecap="round" stroke-linejoin="round"/>
  <text x="80" y="333" class="step-title" fill="{s}">Done! No cables needed</text>
  <text x="80" y="351" class="step-desc">Future updates happen over Wi-Fi automatically.</text>
  <!-- Star -->
  <text x="62" y="368" font-size="14" fill="{c}" text-anchor="middle">✦</text>
  <text x="160" y="370" font-size="11" fill="{c}" text-anchor="middle">✦</text>
</svg>"""

def step_illustrations(size: int = 180) -> list[str]:
    s = size
    return [
        f"""<svg width="{s}" height="{s}" viewBox="0 0 180 140">
  <rect x="50" y="20" width="80" height="40" rx="8" fill="white" stroke="{_c('accent')}" stroke-width="2"/>
  <rect x="60" y="60" width="60" height="30" rx="6" fill="{_c('esp_skin')}" stroke="{_c('border')}" stroke-width="1.5"/>
  <line x1="90" y1="90" x2="90" y2="115" stroke="{_c('border')}" stroke-width="2"/>
  <rect x="60" y="110" width="60" height="18" rx="5" fill="white" stroke="{_c('accent')}" stroke-width="1.5"/>
  <text x="90" y="130" font-size="12" fill="{_c('text_muted')}" text-anchor="middle">USB cable</text>
  <circle cx="170" cy="25" r="12" fill="{_c('success')}" opacity="0.2"/>
  <text x="170" y="29" font-size="14" fill="{_c('success')}" text-anchor="middle" font-weight="bold">1</text>
</svg>""",
        f"""<svg width="{s}" height="{s}" viewBox="0 0 180 140">
  <path d="M20 55 Q50 20 80 55" stroke="{_c('accent')}" stroke-width="3" fill="none" stroke-linecap="round"/>
  <path d="M45 65 Q65 40 85 65" stroke="{_c('accent')}" stroke-width="3" fill="none" stroke-linecap="round"/>
  <circle cx="65" cy="80" r="5" fill="{_c('accent')}"/>
  <rect x="110" y="50" width="40" height="50" rx="10" fill="{_c('esp_skin')}" stroke="{_c('border')}" stroke-width="1.5"/>
  <circle cx="118" cy="62" r="2" fill="{_c('esp_eye')}"/>
  <circle cx="132" cy="62" r="2" fill="{_c('esp_eye')}"/>
  <circle cx="170" cy="25" r="12" fill="{_c('success')}" opacity="0.2"/>
  <text x="170" y="29" font-size="14" fill="{_c('success')}" text-anchor="middle" font-weight="bold">2</text>
</svg>""",
        f"""<svg width="{s}" height="{s}" viewBox="0 0 180 140">
  <rect x="25" y="30" width="130" height="80" rx="16" fill="none" stroke="{_c('accent')}" stroke-width="2.5" stroke-dasharray="6 5"/>
  <path d="M90 50 L90 80 M75 65 L90 80 L105 65" stroke="{_c('accent')}" stroke-width="3.5" fill="none" stroke-linecap="round" stroke-linejoin="round"/>
  <rect x="55" y="85" width="70" height="6" rx="3" fill="{_c('border')}"/>
  <text x="90" y="112" font-size="12" fill="{_c('text_muted')}" text-anchor="middle">.ino file</text>
  <circle cx="170" cy="25" r="12" fill="{_c('success')}" opacity="0.2"/>
  <text x="170" y="29" font-size="14" fill="{_c('success')}" text-anchor="middle" font-weight="bold">3</text>
</svg>""",
    ]

def espy_svg_tag(size: int = 24) -> str:
    return f"""<svg width="{size}" height="{size}" viewBox="0 0 24 24">
  <circle cx="12" cy="10" r="6" fill="{_c('esp_skin')}" stroke="{_c('accent')}" stroke-width="1.5"/>
  <circle cx="10" cy="9" r="1.5" fill="{_c('esp_eye')}"/>
  <circle cx="14" cy="9" r="1.5" fill="{_c('esp_eye')}"/>
  <path d="M8 12 Q12 15 16 12" stroke="{_c('accent')}" stroke-width="1.2" fill="none" stroke-linecap="round"/>
  <rect x="8" y="16" width="8" height="4" rx="2" fill="{_c('border')}"/>
</svg>"""

def espy_icon_24(size: int = 24) -> str:
    return f"""<svg width="{size}" height="{size}" viewBox="0 0 24 24">
  <circle cx="12" cy="8" r="5" fill="{_c('esp_skin')}" stroke="{_c('accent')}" stroke-width="1.2"/>
  <circle cx="10.5" cy="7.5" r="1.2" fill="{_c('esp_eye')}"/>
  <circle cx="13.5" cy="7.5" r="1.2" fill="{_c('esp_eye')}"/>
  <path d="M9 10.5 Q12 12.5 15 10.5" stroke="{_c('accent')}" stroke-width="1" fill="none" stroke-linecap="round"/>
  <rect x="9" y="13" width="6" height="3" rx="1.5" fill="{_c('border')}"/>
</svg>"""

def board_esp32_devkit(size: int = 180) -> str:
    return f"""<svg width="{size}" height="{int(size * 0.72)}" viewBox="0 0 220 158">
  <!-- PCB: classic blue, 53mm × 28mm style -->
  <rect x="10" y="18" width="200" height="122" rx="4" fill="#1E3A5F" stroke="#0D2137" stroke-width="1.5"/>
  <!-- Left pin header (15 pins) -->
  <rect x="10" y="22" width="18" height="114" rx="2" fill="#0D2137" opacity="0.35"/>
  <g fill="#C0A030" opacity="0.6">
    <rect x="14" y="26" width="10" height="4" rx="1.5"/>
    <rect x="14" y="33" width="10" height="4" rx="1.5"/>
    <rect x="14" y="40" width="10" height="4" rx="1.5"/>
    <rect x="14" y="47" width="10" height="4" rx="1.5"/>
    <rect x="14" y="54" width="10" height="4" rx="1.5"/>
    <rect x="14" y="61" width="10" height="4" rx="1.5"/>
    <rect x="14" y="68" width="10" height="4" rx="1.5"/>
    <rect x="14" y="75" width="10" height="4" rx="1.5"/>
    <rect x="14" y="82" width="10" height="4" rx="1.5"/>
    <rect x="14" y="89" width="10" height="4" rx="1.5"/>
    <rect x="14" y="96" width="10" height="4" rx="1.5"/>
    <rect x="14" y="103" width="10" height="4" rx="1.5"/>
    <rect x="14" y="110" width="10" height="4" rx="1.5"/>
    <rect x="14" y="117" width="10" height="4" rx="1.5"/>
    <rect x="14" y="124" width="10" height="4" rx="1.5"/>
  </g>
  <!-- Right pin header (15 pins) -->
  <rect x="192" y="22" width="18" height="114" rx="2" fill="#0D2137" opacity="0.35"/>
  <g fill="#C0A030" opacity="0.6">
    <rect x="196" y="26" width="10" height="4" rx="1.5"/><rect x="196" y="33" width="10" height="4" rx="1.5"/>
    <rect x="196" y="40" width="10" height="4" rx="1.5"/><rect x="196" y="47" width="10" height="4" rx="1.5"/>
    <rect x="196" y="54" width="10" height="4" rx="1.5"/><rect x="196" y="61" width="10" height="4" rx="1.5"/>
    <rect x="196" y="68" width="10" height="4" rx="1.5"/><rect x="196" y="75" width="10" height="4" rx="1.5"/>
    <rect x="196" y="82" width="10" height="4" rx="1.5"/><rect x="196" y="89" width="10" height="4" rx="1.5"/>
    <rect x="196" y="96" width="10" height="4" rx="1.5"/><rect x="196" y="103" width="10" height="4" rx="1.5"/>
    <rect x="196" y="110" width="10" height="4" rx="1.5"/><rect x="196" y="117" width="10" height="4" rx="1.5"/>
    <rect x="196" y="124" width="10" height="4" rx="1.5"/>
  </g>
  <!-- ESP32 module / chip area -->
  <rect x="42" y="48" width="136" height="62" rx="3" fill="#2A5A8A" stroke="#1E3A5F" stroke-width="1"/>
  <!-- Metal shield can -->
  <rect x="55" y="52" width="110" height="54" rx="4" fill="#C0C0C0" stroke="#999" stroke-width="1"/>
  <!-- Chip label -->
  <text x="110" y="85" font-size="8" fill="#333" text-anchor="middle" font-family="monospace">ESP32-WROOM-32</text>
  <!-- Gold LED indicators -->
  <circle cx="48" cy="44" r="2.5" fill="#FFD700" stroke="#CC9900" stroke-width="0.5"/>
  <circle cx="168" cy="44" r="2.5" fill="#FF4444" opacity="0.8"/>
  <!-- USB micro-B port -->
  <rect x="95" y="130" width="30" height="12" rx="2" fill="#666" stroke="#555" stroke-width="1"/>
  <rect x="100" y="130" width="20" height="12" rx="1.5" fill="#444"/>
  <!-- EN / RST button -->
  <circle cx="175" cy="132" r="4" fill="#888" stroke="#666" stroke-width="0.8"/>
  <circle cx="50" cy="132" r="4" fill="#888" stroke="#666" stroke-width="0.8"/>
  <!-- Antenna area -->
  <rect x="155" y="18" width="40" height="8" rx="1" fill="#0D2137" opacity="0.15"/>
  <path d="M175 18 L175 10" stroke="#FFD700" stroke-width="0.5" opacity="0.4"/>
  <text x="110" y="151" font-size="10" fill="{_c('text_muted')}" text-anchor="middle" font-family="sans-serif">ESP32 Dev Module</text>
</svg>"""


def board_nodemcu(size: int = 180) -> str:
    return f"""<svg width="{size}" height="{int(size * 0.8)}" viewBox="0 0 200 160">
  <!-- PCB: green, breadboard-friendly -->
  <rect x="15" y="15" width="170" height="130" rx="10" fill="#0D5C2E" stroke="#083D1E" stroke-width="1.5"/>
  <!-- Left pin header -->
  <rect x="15" y="15" width="22" height="130" rx="3" fill="#083D1E" opacity="0.3"/>
  <g fill="#C0A030" opacity="0.55">
    <rect x="19" y="19" width="14" height="4" rx="1.5"/><rect x="19" y="27" width="14" height="4" rx="1.5"/>
    <rect x="19" y="35" width="14" height="4" rx="1.5"/><rect x="19" y="43" width="14" height="4" rx="1.5"/>
    <rect x="19" y="51" width="14" height="4" rx="1.5"/><rect x="19" y="59" width="14" height="4" rx="1.5"/>
    <rect x="19" y="67" width="14" height="4" rx="1.5"/><rect x="19" y="75" width="14" height="4" rx="1.5"/>
    <rect x="19" y="83" width="14" height="4" rx="1.5"/><rect x="19" y="91" width="14" height="4" rx="1.5"/>
    <rect x="19" y="99" width="14" height="4" rx="1.5"/><rect x="19" y="107" width="14" height="4" rx="1.5"/>
    <rect x="19" y="115" width="14" height="4" rx="1.5"/><rect x="19" y="123" width="14" height="4" rx="1.5"/>
    <rect x="19" y="131" width="14" height="4" rx="1.5"/>
  </g>
  <!-- Right pin header -->
  <rect x="163" y="15" width="22" height="130" rx="3" fill="#083D1E" opacity="0.3"/>
  <g fill="#C0A030" opacity="0.55">
    <rect x="167" y="19" width="14" height="4" rx="1.5"/><rect x="167" y="27" width="14" height="4" rx="1.5"/>
    <rect x="167" y="35" width="14" height="4" rx="1.5"/><rect x="167" y="43" width="14" height="4" rx="1.5"/>
    <rect x="167" y="51" width="14" height="4" rx="1.5"/><rect x="167" y="59" width="14" height="4" rx="1.5"/>
    <rect x="167" y="67" width="14" height="4" rx="1.5"/><rect x="167" y="75" width="14" height="4" rx="1.5"/>
    <rect x="167" y="83" width="14" height="4" rx="1.5"/><rect x="167" y="91" width="14" height="4" rx="1.5"/>
    <rect x="167" y="99" width="14" height="4" rx="1.5"/><rect x="167" y="107" width="14" height="4" rx="1.5"/>
    <rect x="167" y="115" width="14" height="4" rx="1.5"/><rect x="167" y="123" width="14" height="4" rx="1.5"/>
    <rect x="167" y="131" width="14" height="4" rx="1.5"/>
  </g>
  <!-- Module area -->
  <rect x="55" y="55" width="90" height="50" rx="3" fill="#1A8C4A" stroke="#0D5C2E" stroke-width="1"/>
  <rect x="65" y="58" width="70" height="44" rx="3" fill="#D0D0D0" stroke="#999" stroke-width="1"/>
  <text x="100" y="85" font-size="8" fill="#333" text-anchor="middle" font-family="monospace">ESP32</text>
  <!-- USB micro-B port on top edge -->
  <rect x="78" y="8" width="44" height="12" rx="2" fill="#666" stroke="#555" stroke-width="1"/>
  <rect x="86" y="8" width="28" height="12" rx="1.5" fill="#444"/>
  <!-- LED -->
  <circle cx="65" cy="48" r="2" fill="#FFD700"/>
  <circle cx="135" cy="48" r="2" fill="#FF4444" opacity="0.7"/>
  <!-- RST button -->
  <circle cx="145" cy="115" r="5" fill="#888" stroke="#666" stroke-width="0.8"/>
  <text x="100" y="153" font-size="10" fill="{_c('text_muted')}" text-anchor="middle" font-family="sans-serif">NodeMCU-32S</text>
</svg>"""


def board_esp32s3(size: int = 180) -> str:
    return f"""<svg width="{size}" height="{int(size * 0.72)}" viewBox="0 0 210 150">
  <!-- PCB: purple/dark red, compact -->
  <rect x="10" y="12" width="190" height="110" rx="5" fill="#3A1B4A" stroke="#241030" stroke-width="1.5"/>
  <!-- Pin headers top/bottom -->
  <rect x="10" y="12" width="190" height="14" rx="5" fill="#241030" opacity="0.25"/>
  <rect x="10" y="108" width="190" height="14" rx="5" fill="#241030" opacity="0.25"/>
  <g fill="#C0A030" opacity="0.5">
    <rect x="16" y="14" width="8" height="10" rx="1"/><rect x="28" y="14" width="8" height="10" rx="1"/>
    <rect x="40" y="14" width="8" height="10" rx="1"/><rect x="52" y="14" width="8" height="10" rx="1"/>
    <rect x="64" y="14" width="8" height="10" rx="1"/><rect x="76" y="14" width="8" height="10" rx="1"/>
    <rect x="88" y="14" width="8" height="10" rx="1"/><rect x="100" y="14" width="8" height="10" rx="1"/>
    <rect x="112" y="14" width="8" height="10" rx="1"/><rect x="124" y="14" width="8" height="10" rx="1"/>
    <rect x="136" y="14" width="8" height="10" rx="1"/><rect x="148" y="14" width="8" height="10" rx="1"/>
    <rect x="160" y="14" width="8" height="10" rx="1"/><rect x="172" y="14" width="8" height="10" rx="1"/>
  </g>
  <g fill="#C0A030" opacity="0.5">
    <rect x="16" y="110" width="8" height="10" rx="1"/><rect x="28" y="110" width="8" height="10" rx="1"/>
    <rect x="40" y="110" width="8" height="10" rx="1"/><rect x="52" y="110" width="8" height="10" rx="1"/>
    <rect x="64" y="110" width="8" height="10" rx="1"/><rect x="76" y="110" width="8" height="10" rx="1"/>
    <rect x="88" y="110" width="8" height="10" rx="1"/><rect x="100" y="110" width="8" height="10" rx="1"/>
    <rect x="112" y="110" width="8" height="10" rx="1"/><rect x="124" y="110" width="8" height="10" rx="1"/>
    <rect x="136" y="110" width="8" height="10" rx="1"/><rect x="148" y="110" width="8" height="10" rx="1"/>
    <rect x="160" y="110" width="8" height="10" rx="1"/><rect x="172" y="110" width="8" height="10" rx="1"/>
  </g>
  <!-- Chip area -->
  <rect x="40" y="40" width="130" height="50" rx="3" fill="#5C2D7A" stroke="#3A1B4A" stroke-width="1"/>
  <rect x="50" y="43" width="110" height="44" rx="4" fill="#D0D0D0" stroke="#999" stroke-width="1"/>
  <text x="105" y="70" font-size="8" fill="#333" text-anchor="middle" font-family="monospace">ESP32-S3</text>
  <!-- USB-C port -->
  <rect x="170" y="55" width="22" height="16" rx="4" fill="#666" stroke="#555" stroke-width="1"/>
  <rect x="174" y="59" width="14" height="8" rx="2" fill="#444"/>
  <!-- RGB LED -->
  <circle cx="45" cy="32" r="2.5" fill="#FFD700"/>
  <!-- Boot/Reset buttons -->
  <rect x="132" y="98" width="14" height="8" rx="2" fill="#888" stroke="#666" stroke-width="0.6"/>
  <rect x="150" y="98" width="14" height="8" rx="2" fill="#888" stroke="#666" stroke-width="0.6"/>
  <text x="105" y="137" font-size="10" fill="{_c('text_muted')}" text-anchor="middle" font-family="sans-serif">ESP32-S3 DevKitC</text>
</svg>"""


def board_esp32c3(size: int = 180) -> str:
    return f"""<svg width="{size}" height="{int(size * 0.65)}" viewBox="0 0 200 130">
  <!-- PCB: dark green, compact RISC-V -->
  <rect x="15" y="12" width="170" height="95" rx="6" fill="#1A4A3A" stroke="#0D3025" stroke-width="1.5"/>
  <!-- Left pin header -->
  <rect x="15" y="12" width="18" height="95" rx="3" fill="#0D3025" opacity="0.3"/>
  <g fill="#C0A030" opacity="0.5">
    <rect x="18" y="16" width="12" height="4" rx="1.5"/><rect x="18" y="24" width="12" height="4" rx="1.5"/>
    <rect x="18" y="32" width="12" height="4" rx="1.5"/><rect x="18" y="40" width="12" height="4" rx="1.5"/>
    <rect x="18" y="48" width="12" height="4" rx="1.5"/><rect x="18" y="56" width="12" height="4" rx="1.5"/>
    <rect x="18" y="64" width="12" height="4" rx="1.5"/><rect x="18" y="72" width="12" height="4" rx="1.5"/>
    <rect x="18" y="80" width="12" height="4" rx="1.5"/><rect x="18" y="88" width="12" height="4" rx="1.5"/>
  </g>
  <!-- Right pin header -->
  <rect x="167" y="12" width="18" height="95" rx="3" fill="#0D3025" opacity="0.3"/>
  <g fill="#C0A030" opacity="0.5">
    <rect x="170" y="16" width="12" height="4" rx="1.5"/><rect x="170" y="24" width="12" height="4" rx="1.5"/>
    <rect x="170" y="32" width="12" height="4" rx="1.5"/><rect x="170" y="40" width="12" height="4" rx="1.5"/>
    <rect x="170" y="48" width="12" height="4" rx="1.5"/><rect x="170" y="56" width="12" height="4" rx="1.5"/>
    <rect x="170" y="64" width="12" height="4" rx="1.5"/><rect x="170" y="72" width="12" height="4" rx="1.5"/>
    <rect x="170" y="80" width="12" height="4" rx="1.5"/><rect x="170" y="88" width="12" height="4" rx="1.5"/>
  </g>
  <!-- Chip -->
  <rect x="50" y="30" width="100" height="50" rx="3" fill="#2D6B55" stroke="#1A4A3A" stroke-width="1"/>
  <rect x="58" y="34" width="84" height="42" rx="3" fill="#D0D0D0" stroke="#999" stroke-width="1"/>
  <text x="100" y="60" font-size="8" fill="#333" text-anchor="middle" font-family="monospace">ESP32-C3</text>
  <!-- USB-C port -->
  <rect x="82" y="98" width="36" height="14" rx="4" fill="#666" stroke="#555" stroke-width="1"/>
  <rect x="88" y="100" width="24" height="10" rx="2" fill="#444"/>
  <!-- LED -->
  <circle cx="55" cy="26" r="2" fill="#FFD700"/>
  <circle cx="145" cy="26" r="2" fill="#FF4444" opacity="0.7"/>
  <text x="100" y="123" font-size="10" fill="{_c('text_muted')}" text-anchor="middle" font-family="sans-serif">ESP32-C3 DevKit</text>
</svg>"""


def board_esp32s2(size: int = 180) -> str:
    return f"""<svg width="{size}" height="{int(size * 0.7)}" viewBox="0 0 210 146">
  <!-- PCB: red/brown -->
  <rect x="8" y="15" width="194" height="106" rx="4" fill="#4A1A1A" stroke="#300D0D" stroke-width="1.5"/>
  <!-- Top/bottom pin headers -->
  <rect x="8" y="15" width="194" height="14" rx="4" fill="#300D0D" opacity="0.25"/>
  <rect x="8" y="107" width="194" height="14" rx="4" fill="#300D0D" opacity="0.25"/>
  <g fill="#C0A030" opacity="0.5">
    <rect x="14" y="17" width="8" height="10" rx="1"/><rect x="26" y="17" width="8" height="10" rx="1"/>
    <rect x="38" y="17" width="8" height="10" rx="1"/><rect x="50" y="17" width="8" height="10" rx="1"/>
    <rect x="62" y="17" width="8" height="10" rx="1"/><rect x="74" y="17" width="8" height="10" rx="1"/>
    <rect x="86" y="17" width="8" height="10" rx="1"/><rect x="98" y="17" width="8" height="10" rx="1"/>
    <rect x="110" y="17" width="8" height="10" rx="1"/><rect x="122" y="17" width="8" height="10" rx="1"/>
    <rect x="134" y="17" width="8" height="10" rx="1"/><rect x="146" y="17" width="8" height="10" rx="1"/>
    <rect x="158" y="17" width="8" height="10" rx="1"/><rect x="170" y="17" width="8" height="10" rx="1"/>
    <rect x="182" y="17" width="8" height="10" rx="1"/>
  </g>
  <g fill="#C0A030" opacity="0.5">
    <rect x="14" y="109" width="8" height="10" rx="1"/><rect x="26" y="109" width="8" height="10" rx="1"/>
    <rect x="38" y="109" width="8" height="10" rx="1"/><rect x="50" y="109" width="8" height="10" rx="1"/>
    <rect x="62" y="109" width="8" height="10" rx="1"/><rect x="74" y="109" width="8" height="10" rx="1"/>
    <rect x="86" y="109" width="8" height="10" rx="1"/><rect x="98" y="109" width="8" height="10" rx="1"/>
    <rect x="110" y="109" width="8" height="10" rx="1"/><rect x="122" y="109" width="8" height="10" rx="1"/>
    <rect x="134" y="109" width="8" height="10" rx="1"/><rect x="146" y="109" width="8" height="10" rx="1"/>
    <rect x="158" y="109" width="8" height="10" rx="1"/><rect x="170" y="109" width="8" height="10" rx="1"/>
    <rect x="182" y="109" width="8" height="10" rx="1"/>
  </g>
  <!-- Chip -->
  <rect x="42" y="38" width="126" height="56" rx="3" fill="#6B2D2D" stroke="#4A1A1A" stroke-width="1"/>
  <rect x="52" y="42" width="106" height="48" rx="4" fill="#D0D0D0" stroke="#999" stroke-width="1"/>
  <text x="105" y="70" font-size="8" fill="#333" text-anchor="middle" font-family="monospace">ESP32-S2</text>
  <!-- USB micro-B -->
  <rect x="82" y="116" width="40" height="12" rx="2" fill="#666" stroke="#555" stroke-width="1"/>
  <rect x="88" y="116" width="28" height="12" rx="1.5" fill="#444"/>
  <!-- LED -->
  <circle cx="50" cy="34" r="2" fill="#FFD700"/>
  <circle cx="155" cy="34" r="2" fill="#FF4444" opacity="0.7"/>
  <!-- RST button -->
  <circle cx="165" cy="98" r="5" fill="#888" stroke="#666" stroke-width="0.8"/>
  <text x="105" y="141" font-size="10" fill="{_c('text_muted')}" text-anchor="middle" font-family="sans-serif">ESP32-S2 Saola</text>
</svg>"""



def board_esp32s3(size: int = 180) -> str:
    return f"""<svg width="{size}" height="{int(size * 0.75)}" viewBox="0 0 200 150">
  <rect x="10" y="10" width="180" height="100" rx="6" fill="#3A1B4A" stroke="#241030" stroke-width="2"/>
  <rect x="10" y="10" width="25" height="100" rx="6" fill="#241030" opacity="0.2"/>
  <rect x="165" y="10" width="25" height="100" rx="6" fill="#241030" opacity="0.2"/>
  <rect x="45" y="30" width="110" height="60" rx="4" fill="#5C2D7A" stroke="#3A1B4A" stroke-width="1.5"/>
  <rect x="60" y="35" width="80" height="50" rx="5" fill="#D0D0D0" stroke="#999" stroke-width="1.5"/>
  <text x="100" y="65" font-size="10" fill="#333" text-anchor="middle" font-family="monospace">S3</text>
  <circle cx="78" cy="27" r="2.5" fill="#FFD700"/>
  <circle cx="122" cy="27" r="2.5" fill="#FFD700"/>
  <rect x="18" y="25" width="12" height="70" rx="3" fill="#888" opacity="0.3"/>
  <rect x="170" y="25" width="12" height="70" rx="3" fill="#888" opacity="0.3"/>
  <rect x="85" y="100" width="32" height="12" rx="3" fill="#666" stroke="#555" stroke-width="1"/>
  <rect x="88" y="100" width="26" height="12" rx="2" fill="#444"/>
  <rect x="155" y="95" width="20" height="18" rx="3" fill="#888" stroke="#666" stroke-width="1"/>
  <rect x="158" y="98" width="14" height="12" rx="2" fill="#666"/>
  <rect x="25" y="95" width="20" height="18" rx="3" fill="#888" stroke="#666" stroke-width="1"/>
  <text x="100" y="128" font-size="10" fill="{_c('text_muted')}" text-anchor="middle" font-family="sans-serif">ESP32-S3 DevKitC</text>
</svg>"""


def board_esp32c3(size: int = 180) -> str:
    return f"""<svg width="{size}" height="{int(size * 0.7)}" viewBox="0 0 200 140">
  <rect x="15" y="15" width="170" height="90" rx="8" fill="#1A4A3A" stroke="#0D3025" stroke-width="2"/>
  <rect x="15" y="15" width="20" height="90" rx="8" fill="#0D3025" opacity="0.2"/>
  <rect x="165" y="15" width="20" height="90" rx="8" fill="#0D3025" opacity="0.2"/>
  <rect x="50" y="30" width="100" height="50" rx="4" fill="#2D6B55" stroke="#1A4A3A" stroke-width="1.5"/>
  <rect x="65" y="35" width="70" height="40" rx="5" fill="#D0D0D0" stroke="#999" stroke-width="1.5"/>
  <text x="100" y="60" font-size="9" fill="#333" text-anchor="middle" font-family="monospace">C3</text>
  <circle cx="80" cy="28" r="2" fill="#FFD700"/>
  <circle cx="120" cy="28" r="2" fill="#FFD700"/>
  <rect x="22" y="30" width="12" height="60" rx="2" fill="#888" opacity="0.3"/>
  <rect x="166" y="30" width="12" height="60" rx="2" fill="#888" opacity="0.3"/>
  <rect x="85" y="95" width="30" height="10" rx="3" fill="#666" stroke="#555" stroke-width="1"/>
  <text x="100" y="118" font-size="10" fill="{_c('text_muted')}" text-anchor="middle" font-family="sans-serif">ESP32-C3</text>
</svg>"""


def board_esp32s2(size: int = 180) -> str:
    return f"""<svg width="{size}" height="{int(size * 0.72)}" viewBox="0 0 200 145">
  <rect x="10" y="15" width="180" height="95" rx="4" fill="#4A1A1A" stroke="#300D0D" stroke-width="2"/>
  <rect x="10" y="15" width="22" height="95" rx="4" fill="#300D0D" opacity="0.2"/>
  <rect x="168" y="15" width="22" height="95" rx="4" fill="#300D0D" opacity="0.2"/>
  <rect x="42" y="35" width="116" height="55" rx="4" fill="#6B2D2D" stroke="#4A1A1A" stroke-width="1.5"/>
  <rect x="57" y="40" width="86" height="45" rx="5" fill="#D0D0D0" stroke="#999" stroke-width="1.5"/>
  <text x="100" y="67" font-size="10" fill="#333" text-anchor="middle" font-family="monospace">S2</text>
  <circle cx="76" cy="33" r="2.5" fill="#FFD700"/>
  <circle cx="124" cy="33" r="2.5" fill="#FFD700"/>
  <rect x="16" y="30" width="12" height="65" rx="2" fill="#888" opacity="0.3"/>
  <rect x="172" y="30" width="12" height="65" rx="2" fill="#888" opacity="0.3"/>
  <rect x="85" y="100" width="30" height="12" rx="3" fill="#666" stroke="#555" stroke-width="1"/>
  <rect x="90" y="100" width="20" height="12" rx="2" fill="#444"/>
  <rect x="40" y="12" width="12" height="8" rx="2" fill="#888"/>
  <rect x="148" y="12" width="12" height="8" rx="2" fill="#888"/>
  <text x="100" y="122" font-size="10" fill="{_c('text_muted')}" text-anchor="middle" font-family="sans-serif">ESP32-S2 Saola</text>
</svg>"""


def board_esp32c6(size: int = 180) -> str:
    return f"""<svg width="{size}" height="{int(size * 0.7)}" viewBox="0 0 200 140">
  <!-- PCB: deep navy, RISC-V C6 -->
  <rect x="15" y="12" width="170" height="95" rx="6" fill="#1A1A4A" stroke="#0D0D30" stroke-width="1.5"/>
  <!-- Left pin header -->
  <rect x="15" y="12" width="18" height="95" rx="3" fill="#0D0D30" opacity="0.3"/>
  <g fill="#C0A030" opacity="0.5">
    <rect x="18" y="16" width="12" height="4" rx="1.5"/><rect x="18" y="24" width="12" height="4" rx="1.5"/>
    <rect x="18" y="32" width="12" height="4" rx="1.5"/><rect x="18" y="40" width="12" height="4" rx="1.5"/>
    <rect x="18" y="48" width="12" height="4" rx="1.5"/><rect x="18" y="56" width="12" height="4" rx="1.5"/>
    <rect x="18" y="64" width="12" height="4" rx="1.5"/><rect x="18" y="72" width="12" height="4" rx="1.5"/>
    <rect x="18" y="80" width="12" height="4" rx="1.5"/><rect x="18" y="88" width="12" height="4" rx="1.5"/>
  </g>
  <!-- Right pin header -->
  <rect x="167" y="12" width="18" height="95" rx="3" fill="#0D0D30" opacity="0.3"/>
  <g fill="#C0A030" opacity="0.5">
    <rect x="170" y="16" width="12" height="4" rx="1.5"/><rect x="170" y="24" width="12" height="4" rx="1.5"/>
    <rect x="170" y="32" width="12" height="4" rx="1.5"/><rect x="170" y="40" width="12" height="4" rx="1.5"/>
    <rect x="170" y="48" width="12" height="4" rx="1.5"/><rect x="170" y="56" width="12" height="4" rx="1.5"/>
    <rect x="170" y="64" width="12" height="4" rx="1.5"/><rect x="170" y="72" width="12" height="4" rx="1.5"/>
    <rect x="170" y="80" width="12" height="4" rx="1.5"/><rect x="170" y="88" width="12" height="4" rx="1.5"/>
  </g>
  <!-- Chip -->
  <rect x="50" y="30" width="100" height="50" rx="3" fill="#2D2D6B" stroke="#1A1A4A" stroke-width="1"/>
  <rect x="58" y="34" width="84" height="42" rx="3" fill="#D0D0D0" stroke="#999" stroke-width="1"/>
  <text x="100" y="60" font-size="8" fill="#333" text-anchor="middle" font-family="monospace">ESP32-C6</text>
  <!-- USB-C port (bottom edge) -->
  <rect x="82" y="98" width="36" height="14" rx="4" fill="#666" stroke="#555" stroke-width="1"/>
  <rect x="88" y="100" width="24" height="10" rx="2" fill="#444"/>
  <!-- LED -->
  <circle cx="55" cy="26" r="2" fill="#FFD700"/>
  <circle cx="145" cy="26" r="2" fill="#FF4444" opacity="0.7"/>
  <text x="100" y="125" font-size="10" fill="{_c('text_muted')}" text-anchor="middle" font-family="sans-serif">ESP32-C6</text>
</svg>"""


def board_esp32h2(size: int = 180) -> str:
    return f"""<svg width="{size}" height="{int(size * 0.65)}" viewBox="0 0 200 130">
  <!-- PCB: dark forest green, Zigbee/Thread H2 -->
  <rect x="18" y="12" width="164" height="86" rx="6" fill="#2A4A2A" stroke="#1A301A" stroke-width="1.5"/>
  <!-- Left pin header (compact) -->
  <rect x="18" y="12" width="16" height="86" rx="3" fill="#1A301A" opacity="0.3"/>
  <g fill="#C0A030" opacity="0.5">
    <rect x="21" y="16" width="10" height="4" rx="1.5"/><rect x="21" y="24" width="10" height="4" rx="1.5"/>
    <rect x="21" y="32" width="10" height="4" rx="1.5"/><rect x="21" y="40" width="10" height="4" rx="1.5"/>
    <rect x="21" y="48" width="10" height="4" rx="1.5"/><rect x="21" y="56" width="10" height="4" rx="1.5"/>
    <rect x="21" y="64" width="10" height="4" rx="1.5"/><rect x="21" y="72" width="10" height="4" rx="1.5"/>
    <rect x="21" y="80" width="10" height="4" rx="1.5"/>
  </g>
  <!-- Right pin header -->
  <rect x="166" y="12" width="16" height="86" rx="3" fill="#1A301A" opacity="0.3"/>
  <g fill="#C0A030" opacity="0.5">
    <rect x="169" y="16" width="10" height="4" rx="1.5"/><rect x="169" y="24" width="10" height="4" rx="1.5"/>
    <rect x="169" y="32" width="10" height="4" rx="1.5"/><rect x="169" y="40" width="10" height="4" rx="1.5"/>
    <rect x="169" y="48" width="10" height="4" rx="1.5"/><rect x="169" y="56" width="10" height="4" rx="1.5"/>
    <rect x="169" y="64" width="10" height="4" rx="1.5"/><rect x="169" y="72" width="10" height="4" rx="1.5"/>
    <rect x="169" y="80" width="10" height="4" rx="1.5"/>
  </g>
  <!-- Chip -->
  <rect x="55" y="28" width="90" height="48" rx="3" fill="#3D6B3D" stroke="#2A4A2A" stroke-width="1"/>
  <rect x="63" y="32" width="74" height="40" rx="3" fill="#D0D0D0" stroke="#999" stroke-width="1"/>
  <text x="100" y="57" font-size="8" fill="#333" text-anchor="middle" font-family="monospace">ESP32-H2</text>
  <!-- USB-C port -->
  <rect x="80" y="90" width="40" height="12" rx="4" fill="#666" stroke="#555" stroke-width="1"/>
  <rect x="86" y="92" width="28" height="8" rx="2" fill="#444"/>
  <!-- LED -->
  <circle cx="60" cy="24" r="2" fill="#FFD700"/>
  <circle cx="140" cy="24" r="2" fill="#FF4444" opacity="0.7"/>
  <!-- Antenna area -->
  <rect x="148" y="80" width="24" height="6" rx="1" fill="#1A301A" opacity="0.15"/>
  <text x="100" y="118" font-size="10" fill="{_c('text_muted')}" text-anchor="middle" font-family="sans-serif">ESP32-H2</text>
</svg>"""


BOARD_ILLUSTRATIONS = {
    "ESP32 Dev Module": board_esp32_devkit,
    "NodeMCU-32S": board_nodemcu,
    "ESP32-S3 DevKitC": board_esp32s3,
    "ESP32-C3 DevKit": board_esp32c3,
    "ESP32-S2 Saola": board_esp32s2,
    "ESP32-C6 Dev Module": board_esp32c6,
    "ESP32-H2 Dev Module": board_esp32h2,
}

ESPY_MOODS = {
    "idle": espy_glasses,
    "happy": espy_happy,
    "wink": espy_wink,
    "surprise": espy_surprise,
    "sad": espy_sad,
    "searching": espy_searching,
    "focused": espy_focused,
    "sweat": espy_sweat,
    "excited": espy_excited,
    "peek": espy_peek,
    "listening": espy_listening,
}


# ══ ui/animations.py ═══════════════════════════════════════

# ── Fade transition stack ─────────────────────────────────

class FadeStack(QStackedWidget):
    """QStackedWidget with a crossfade between pages."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self._animating = False

    def fade_to(self, index: int, duration: int = 250):
        if self._animating or index == self.currentIndex():
            self.setCurrentIndex(index)
            return
        self._animating = True
        current = self.currentWidget()
        if current:
            eff = QGraphicsOpacityEffect(current)
            current.setGraphicsEffect(eff)
            anim = QPropertyAnimation(eff, b"opacity")
            anim.setDuration(duration // 2)
            anim.setStartValue(1.0)
            anim.setEndValue(0.0)
            anim.finished.connect(lambda: self._finish_fade(index, duration // 2))
            anim.start()
        else:
            self.setCurrentIndex(index)
            self._animating = False

    def _finish_fade(self, index: int, next_duration: int):
        self.setCurrentIndex(index)
        w = self.currentWidget()
        if w:
            eff = QGraphicsOpacityEffect(w)
            w.setGraphicsEffect(eff)
            eff.setOpacity(0.0)
            anim = QPropertyAnimation(eff, b"opacity")
            anim.setDuration(next_duration)
            anim.setStartValue(0.0)
            anim.setEndValue(1.0)
            anim.finished.connect(self._clear_gfx)
            anim.start()
        self._animating = False

    def _clear_gfx(self):
        w = self.currentWidget()
        if w:
            w.setGraphicsEffect(None)


# ── Bouncy mascot (QVariantAnimation, no pyqtProperty) ─────

class BouncyMascot(QLabel):
    """Mascot with mood-based bounce styles."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._current_mood = "idle"
        self._current_size = 140
        self._offset = 0
        self._bounce = QVariantAnimation(self)
        self._bounce.setLoopCount(-1)
        self._bounce.setEasingCurve(QEasingCurve.Type.InOutSine)
        self._bounce.valueChanged.connect(self._on_bounce)
        self._bounce_style = "idle"

    def set_mood(self, mood: str, size: int = 140):
        fn = ESPY_MOODS.get(mood, ESPY_MOODS["idle"])
        pm = QPixmap()
        pm.loadFromData(fn(size).encode())
        self.setPixmap(pm)
        self._current_mood = mood
        self._current_size = size

    def set_bounce_style(self, style: str = "idle"):
        self._bounce_style = style
        pulses = {
            "idle":    (1200,  -6),
            "happy":   (800,  -10),
            "sad":     (1800, -4),
            "excited": (600,  -14),
            "searching": (1000, -8),
        }
        dur, height = pulses.get(style, (1200, -6))
        self._bounce.setDuration(dur)
        self._bounce.setStartValue(0)
        self._bounce.setKeyValueAt(0.5, height)
        self._bounce.setEndValue(0)

    def start_bounce(self):
        if self._bounce.state() != QAbstractAnimation.State.Running:
            self._bounce.start()

    def stop_bounce(self):
        self._bounce.stop()
        self._offset = 0
        self.update()

    def _on_bounce(self, value):
        self._offset = int(value)
        self.update()

    def paintEvent(self, e):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)
        pm = self.pixmap()
        if pm and not pm.isNull():
            r = self.rect()
            x = (r.width() - pm.width()) // 2
            y = (r.height() - pm.height()) // 2 + self._offset
            p.drawPixmap(x, y, pm)
        p.end()


# ── Loading dots ──────────────────────────────────────────

class LoadingDots(QLabel):
    """Three dots that pulse in sequence."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self._phase = 0
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._tick)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setStyleSheet(f"font-size: 32px; color: {C['accent']}; font-weight: 700;")
        self._timer.start(350)

    def _tick(self):
        phases = ["● ○ ○", "○ ● ○", "○ ○ ●"]
        self._phase = (self._phase + 1) % 3
        self.setText(phases[self._phase])

    def start(self):
        self._timer.start(350)

    def stop(self):
        self._timer.stop()
        self.setText("")


# ── Pulse widget (drop zone glow) ─────────────────────────

class PulseWidget(QWidget):
    """Widget that pulses its background opacity."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self._pulse_opacity = 0.3
        self._pulse = QPropertyAnimation(self, b"pulse_opacity")
        self._pulse.setDuration(2000)
        self._pulse.setLoopCount(-1)
        self._pulse.setEasingCurve(QEasingCurve.Type.InOutSine)

    def start_pulse(self):
        self._pulse.setStartValue(0.15)
        self._pulse.setEndValue(0.5)
        self._pulse.start()

    def stop_pulse(self):
        self._pulse.stop()

    def _get_pulse(self) -> float:
        return self._pulse_opacity

    def _set_pulse(self, v: float):
        self._pulse_opacity = v
        self.update()

    pulse_opacity = pyqtProperty(float, _get_pulse, _set_pulse)

    def paintEvent(self, e):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        color = QColor(C['accent'])
        color.setAlphaF(self._pulse_opacity * 0.12)
        p.setBrush(QBrush(color))
        p.setPen(Qt.PenStyle.NoPen)
        p.drawRoundedRect(self.rect().adjusted(2, 2, -2, -2), 24, 24)
        p.end()


# ── Confetti ──────────────────────────────────────────────

class ConfettiWidget(QWidget):
    """Falling confetti particles with sparkle shapes."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self._timer = QTimer(self)
        self._timer.timeout.connect(self.update)
        self._particles: list[dict] = []
        self._running = False

    def start(self, count: int = 60):
        import random
        rng = random.Random()
        self._particles = []
        colors = [C['accent'], C['success'], C['warning'], C['info'], C['accent_hover']]
        shapes = ["rect", "star", "circle"]
        for _ in range(count):
            self._particles.append({
                "x": rng.uniform(0, 1),
                "y": rng.uniform(-0.3, 0),
                "speed": rng.uniform(0.002, 0.01),
                "size": rng.randint(4, 12),
                "color": rng.choice(colors),
                "opacity": rng.uniform(0.4, 0.9),
                "drift": rng.uniform(-0.002, 0.002),
                "shape": rng.choice(shapes),
                "rotation": rng.uniform(0, 360),
                "rot_speed": rng.uniform(-3, 3),
            })
        self._running = True
        self._timer.start(30)

    def stop(self):
        self._running = False
        self._timer.stop()
        self._particles = []
        self.update()

    def paintEvent(self, e):
        if not self._running or not self._particles:
            return
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        w = self.width()
        h = self.height()
        for pt in self._particles:
            pt["y"] += pt["speed"]
            pt["x"] += pt["drift"]
            pt["rotation"] += pt["rot_speed"]
            if pt["y"] > 1.15:
                pt["y"] = -0.08
                pt["x"] = random.random()
            px = int(pt["x"] * w)
            py = int(pt["y"] * h)
            color = QColor(pt["color"])
            color.setAlphaF(pt["opacity"])
            p.setBrush(QBrush(color))
            p.setPen(Qt.PenStyle.NoPen)
            s = pt["size"]
            if pt["shape"] == "star":
                cx, cy = px, py
                r_outer = s // 2
                poly = []
                for i in range(5):
                    angle = math.radians(pt["rotation"] + i * 72 - 90)
                    poly.append((cx + r_outer * math.cos(angle), cy + r_outer * math.sin(angle)))
                    angle2 = math.radians(pt["rotation"] + (i + 0.5) * 72 - 90)
                    poly.append((cx + r_outer * 0.4 * math.cos(angle2), cy + r_outer * 0.4 * math.sin(angle2)))
                if poly:
                    pts = [QPointF(x, y) for x, y in poly]
                    p.drawPolygon(pts)
            elif pt["shape"] == "circle":
                p.drawEllipse(px - s // 4, py - s // 4, s // 2, s // 2)
            else:
                p.drawRoundedRect(px, py, s, s // 2, 2, 2)
        p.end()


# ── Animated checkmark ────────────────────────────────────

class AnimatedCheckmark(QWidget):
    """Draws a circular checkmark then breathes."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self._progress = 0.0
        self._breathing = False
        self._breath_progress = 0.0
        self._anim = QPropertyAnimation(self, b"draw_progress")
        self._anim.setDuration(600)
        self._anim.setEasingCurve(QEasingCurve.Type.OutBack)
        self._breath_anim = QPropertyAnimation(self, b"breath_value")
        self._breath_anim.setDuration(1500)
        self._breath_anim.setLoopCount(-1)
        self._breath_anim.setEasingCurve(QEasingCurve.Type.InOutSine)
        self.setFixedSize(120, 120)

    def start_animate(self):
        self._progress = 0.0
        self._breathing = False
        self._anim.setStartValue(0.0)
        self._anim.setEndValue(1.0)
        self._anim.start()
        self._anim.finished.connect(self._start_breathing)

    def _start_breathing(self):
        self._breathing = True
        self._breath_anim.setStartValue(0.9)
        self._breath_anim.setEndValue(1.1)
        self._breath_anim.start()

    def _get_progress(self) -> float:
        return self._progress

    def _set_progress(self, v: float):
        self._progress = v
        self.update()

    def _get_breath(self) -> float:
        return self._breath_progress

    def _set_breath(self, v: float):
        self._breath_progress = v
        self.update()

    draw_progress = pyqtProperty(float, _get_progress, _set_progress)
    breath_value = pyqtProperty(float, _get_breath, _set_breath)

    def paintEvent(self, e):
        if self._progress <= 0:
            return
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        w = self.width()
        h = self.height()
        cx, cy = w // 2, h // 2
        base_r = min(cx, cy) - 8
        scale = self._breath_progress if self._breathing else 1.0
        r = int(base_r * scale)

        p.setBrush(QBrush(QColor(C['success'])))
        p.setPen(Qt.PenStyle.NoPen)
        p.drawEllipse(cx - r, cy - r, r * 2, r * 2)

        p.setPen(QPen(QColor("white"), 6, Qt.PenStyle.SolidLine,
                      Qt.PenCapStyle.RoundCap, Qt.PenJoinStyle.RoundJoin))
        path = [
            (cx - r * 0.4, cy),
            (cx - r * 0.1, cy + r * 0.35),
            (cx + r * 0.45, cy - r * 0.3),
        ]
        if self._progress < 0.5:
            frac = self._progress * 2
            p1 = path[0]
            p2 = (
                path[0][0] + (path[1][0] - path[0][0]) * frac,
                path[0][1] + (path[1][1] - path[0][1]) * frac,
            )
            p.drawLine(int(p1[0]), int(p1[1]), int(p2[0]), int(p2[1]))
        else:
            frac = (self._progress - 0.5) * 2
            p.drawLine(int(path[0][0]), int(path[0][1]),
                       int(path[1][0]), int(path[1][1]))
            p2 = (
                path[1][0] + (path[2][0] - path[1][0]) * frac,
                path[1][1] + (path[2][1] - path[1][1]) * frac,
            )
            p.drawLine(int(path[1][0]), int(path[1][1]),
                       int(p2[0]), int(p2[1]))
        p.end()


# ── Mascot progress bar ───────────────────────────────────

class MascotProgressBar(QWidget):
    """Progress bar with a mascot that pushes the filled portion."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self._value = 0
        self._anim = QPropertyAnimation(self, b"bar_value")
        self._anim.setDuration(400)
        self._anim.setEasingCurve(QEasingCurve.Type.OutCubic)
        self.setFixedHeight(48)
        self.setMinimumWidth(300)
        self._pixmap_cache: dict[tuple[str, int], QPixmap] = {}

    def _get_value(self) -> int:
        return self._value

    def _set_value(self, v: int):
        self._value = max(0, min(100, v))
        self.update()

    bar_value = pyqtProperty(int, _get_value, _set_value)

    def set_value(self, v: int, animate: bool = True):
        if animate:
            self._anim.setStartValue(self._value)
            self._anim.setEndValue(v)
            self._anim.start()
        else:
            self._value = v
            self.update()

    def paintEvent(self, e):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)

        w = self.width()
        h = self.height()
        bar_h = 16
        bar_y = (h - bar_h) // 2
        margin = 4
        track_w = w - margin * 2
        m = 4
        fill_w = max(m, int(track_w * self._value / 100))
        r = bar_h // 2

        # Track
        p.setBrush(QBrush(QColor(C['border'])))
        p.setPen(Qt.PenStyle.NoPen)
        p.drawRoundedRect(margin, bar_y, track_w, bar_h, r, r)

        # Fill
        grad = QLinearGradient(margin, 0, margin + fill_w, 0)
        grad.setColorAt(0, QColor(C['accent']))
        grad.setColorAt(1, QColor(C['info']))
        p.setBrush(QBrush(grad))
        p.drawRoundedRect(margin, bar_y, fill_w, bar_h, r, r)

        if self._value > 0:
            # Block
            block_x = margin + fill_w - 6
            block_y = bar_y - 8
            block_w = 14
            block_h = bar_h + 16
            bc = QColor(C['accent_hover'])
            bc.setAlphaF(0.4)
            p.setBrush(QBrush(bc))
            p.drawRoundedRect(block_x, block_y, block_w, block_h, 4, 4)

            # Mascot pushing position
            mascot_size = 36
            mx = block_x - mascot_size // 2
            my = block_y - mascot_size + 4
            try:
                mood = "sweat" if 30 < self._value < 80 else ("focused" if self._value < 100 else "excited")
                if self._value >= 100:
                    mood = "happy"
                key = (mood, mascot_size)
                pm = self._pixmap_cache.get(key)
                if pm is None:
                    fn = ESPY_MOODS.get(mood, ESPY_MOODS["idle"])
                    pm = QPixmap()
                    pm.loadFromData(fn(mascot_size).encode())
                    if not pm.isNull():
                        self._pixmap_cache[key] = pm
                if pm is not None and not pm.isNull():
                    p.drawPixmap(int(mx), int(my), pm)
            except Exception:
                pass

        # Percentage text
        p.setPen(QPen(QColor(C['text_muted'])))
        font = QFont("system-ui", 13, QFont.Weight.Bold)
        p.setFont(font)
        p.drawText(self.rect(), Qt.AlignmentFlag.AlignCenter, f"{self._value}%")

        p.end()


# ── Breathing dot (QVariantAnimation, no pyqtProperty) ────

class BreathingDot(QLabel):
    """Pulsing status dot. Green for online, gray for offline."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self._online = True
        self._dot_opacity = 1.0
        self._anim = QVariantAnimation(self)
        self._anim.setLoopCount(-1)
        self._anim.setEasingCurve(QEasingCurve.Type.InOutSine)
        self._anim.valueChanged.connect(self._on_opacity)
        self.setText("●")
        self.setStyleSheet("font-size: 14px;")

    def set_online(self, online: bool):
        self._online = online
        color = C['success'] if online else C['text_faint']
        self.setStyleSheet(f"font-size: 14px; color: {color};")
        self._anim.stop()
        if online:
            self._anim.setDuration(1200)
            self._anim.setStartValue(0.5)
            self._anim.setEndValue(1.0)
        else:
            self._anim.setDuration(2500)
            self._anim.setStartValue(0.3)
            self._anim.setEndValue(0.6)
        self._anim.start()

    def stop(self):
        self._anim.stop()

    def _on_opacity(self, v):
        self._dot_opacity = v
        base = C['success'] if self._online else C['text_faint']
        c = QColor(base)
        c.setAlphaF(v)
        name = c.name(QColor.NameFormat.HexArgb)
        self.setStyleSheet(f"font-size: 14px; color: {name};")


# ── Animated arrow (QVariantAnimation, no pyqtProperty) ───

class AnimatedArrow(QWidget):
    """Bouncing pointing arrow."""
    def __init__(self, direction: str = "down", parent=None):
        super().__init__(parent)
        self._direction = direction
        self._arrow_off = 0
        self._bounce = QVariantAnimation(self)
        self._bounce.setDuration(1000)
        self._bounce.setLoopCount(-1)
        self._bounce.setEasingCurve(QEasingCurve.Type.InOutSine)
        self._bounce.setStartValue(0)
        self._bounce.setEndValue(8)
        self._bounce.valueChanged.connect(self._on_bounce)
        self._bounce.start()
        self.setFixedSize(40, 40)

    def _on_bounce(self, v):
        self._arrow_off = int(v)
        self.update()

    def paintEvent(self, e):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        color = QColor(C['accent'])
        color.setAlphaF(0.7)
        p.setPen(QPen(color, 3, Qt.PenStyle.SolidLine,
                       Qt.PenCapStyle.RoundCap, Qt.PenJoinStyle.RoundJoin))
        offset = self._arrow_off
        cx, cy = self.width() // 2, self.height() // 2 + offset
        s = 12
        if self._direction == "down":
            p.drawLine(cx, cy - s, cx, cy + s)
            p.drawLine(cx - s // 2, cy + s // 2, cx, cy + s)
            p.drawLine(cx + s // 2, cy + s // 2, cx, cy + s)
        elif self._direction == "up":
            p.drawLine(cx, cy + s, cx, cy - s)
            p.drawLine(cx - s // 2, cy - s // 2, cx, cy - s)
            p.drawLine(cx + s // 2, cy - s // 2, cx, cy - s)
        elif self._direction == "right":
            p.drawLine(cx - s, cy, cx + s, cy)
            p.drawLine(cx + s // 2, cy - s // 2, cx + s, cy)
            p.drawLine(cx + s // 2, cy + s // 2, cx + s, cy)
        p.end()


# ── Floating USB (QVariantAnimation, no pyqtProperty) ─────

class FloatingUSB(QLabel):
    """USB icon that gently floats up and down."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        pm = QPixmap()
        pm.loadFromData(usb_illustration(160).encode())
        self.setPixmap(pm)
        self._float_off = 0
        self._float = QVariantAnimation(self)
        self._float.setDuration(2500)
        self._float.setLoopCount(-1)
        self._float.setEasingCurve(QEasingCurve.Type.InOutSine)
        self._float.setStartValue(0)
        self._float.setEndValue(-12)
        self._float.valueChanged.connect(self._on_float)
        self._float.start()

    def _on_float(self, v):
        self._float_off = int(v)
        self.update()

    def paintEvent(self, e):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)
        pm = self.pixmap()
        if pm and not pm.isNull():
            off = self._float_off
            r = self.rect()
            x = (r.width() - pm.width()) // 2
            y = (r.height() - pm.height()) // 2 + off
            p.drawPixmap(x, y, pm)
        p.end()


# ── Plug Animation (composite laptop + USB + ESP) ────────

class PlugAnimation(QLabel):
    """Composite illustration: laptop port ← USB cable → ESP32 board.
    Shows the physical connection at realistic proportions with a pulsing glow."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setMinimumSize(240, 160)
        self._update_pixmap(240)
        self._breath = QVariantAnimation(self)
        self._breath.setDuration(2000)
        self._breath.setLoopCount(-1)
        self._breath.setEasingCurve(QEasingCurve.Type.InOutSine)
        self._breath.setStartValue(0.92)
        self._breath.setEndValue(1.08)
        self._breath.valueChanged.connect(self._on_breath)
        self._breath.start()

    def _update_pixmap(self, base_size: int):
        pm = QPixmap()
        pm.loadFromData(plug_illustration(base_size).encode())
        self._pixmap = pm
        if not pm.isNull():
            self.setFixedSize(pm.width(), pm.height())

    def _on_breath(self, v):
        pass  # SVG animation handles independent pulsing

    def paintEvent(self, e):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)
        if self._pixmap and not self._pixmap.isNull():
            pm = self._pixmap
            r = self.rect()
            x = (r.width() - pm.width()) // 2
            y = (r.height() - pm.height()) // 2
            p.drawPixmap(x, y, pm)
        p.end()


# ── Pulsing Wi-Fi ─────────────────────────────────────────

class PulsingWifi(QLabel):
    """Wi-Fi icon with pulsing signal arcs."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._wifi_pulse = 0.5
        self._pulse = QVariantAnimation(self)
        self._pulse.setDuration(2000)
        self._pulse.setLoopCount(-1)
        self._pulse.setEasingCurve(QEasingCurve.Type.InOutSine)
        self._pulse.setStartValue(0.3)
        self._pulse.setEndValue(1.0)
        self._pulse.valueChanged.connect(self._on_wifi_pulse)
        self._pulse.start()

    def _on_wifi_pulse(self, v):
        self._wifi_pulse = v
        self.update()

    def paintEvent(self, e):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        w = self.width()
        h = self.height()
        cx, cy = w // 2, h // 2 + 12
        base = min(w, h) * 0.08
        p.setPen(Qt.PenStyle.NoPen)
        for i in range(3):
            radius = base * (4 - i) * 1.2
            alpha = self._wifi_pulse * (0.3 + 0.25 * (2 - i) / 2)
            color = QColor(C['accent'])
            color.setAlphaF(max(0.05, alpha))
            p.setBrush(QBrush(color))
            p.drawChord(int(cx - radius), int(cy - radius * 1.5),
                        int(radius * 2), int(radius * 3),
                        45 * 16, 90 * 16)
        dot_color = QColor(C['accent'])
        dot_color.setAlphaF(self._wifi_pulse)
        p.setBrush(QBrush(dot_color))
        p.drawEllipse(cx - 5, cy - 5 + int(base * 1.5), 10, 10)
        p.end()


# ── Slide label (QVariantAnimation, no pyqtProperty) ──────

class SlideLabel(QLabel):
    """Label that slides in vertically."""
    def __init__(self, text: str, parent=None):
        super().__init__(text, parent)
        self._slide_offset = 20
        self._slide = QVariantAnimation(self)
        self._slide.setDuration(400)
        self._slide.setEasingCurve(QEasingCurve.Type.OutCubic)
        self._slide.valueChanged.connect(self._on_slide)
        self.setStyleSheet(f"color: {C['success']}; font-size: 16px;")

    def animate_in(self, delay: int = 0):
        from PyQt6.QtCore import QTimer as QTimer2
        QTimer2.singleShot(delay, self._do_slide)

    def _do_slide(self):
        self._slide.setStartValue(20)
        self._slide.setEndValue(0)
        self._slide.start()

    def _on_slide(self, v):
        self._slide_offset = int(v)
        self.setContentsMargins(0, self._slide_offset, 0, 0)
        self.update()


# ── Progress pulse (QVariantAnimation, no pyqtProperty) ───

class ProgressPulse(QProgressBar):
    """Progress bar with subtle glow."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self._glow = QVariantAnimation(self)
        self._glow.setDuration(1500)
        self._glow.setLoopCount(-1)
        self._glow.setEasingCurve(QEasingCurve.Type.InOutSine)
        self._glow.valueChanged.connect(self._on_glow)
        self._glow_val = 0.6

    def start_glow(self):
        self._glow.setStartValue(0.6)
        self._glow.setEndValue(1.0)
        self._glow.start()

    def stop_glow(self):
        self._glow.stop()

    def _on_glow(self, v):
        self._glow_val = v
        qss = f"""
            QProgressBar {{
                background: {C['border']};
                border: none; border-radius: 10px; height: 16px;
            }}
            QProgressBar::chunk {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 {C['accent']}, stop:1 {C['info']});
                border-radius: 10px;
            }}
        """
        self.setStyleSheet(qss)


# ══ ui/board_picker.py ═══════════════════════════════════════

class BoardCard(QFrame):
    clicked = pyqtSignal(str)

    def __init__(self, board_name: str, parent=None):
        super().__init__(parent)
        self._board_name = board_name
        self._selected = False
        self.setObjectName("card")
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setFixedSize(200, 220)
        self._build()

    def _build(self):
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setSpacing(6)
        layout.setContentsMargins(10, 10, 10, 10)

        info = BOARDS.get(self._board_name, {})
        chip = info.get("chip", "ESP32")
        flash = info.get("flash_size", "?")
        fn = BOARD_ILLUSTRATIONS.get(self._board_name)
        if fn:
            svg = fn(130)
            lbl = QLabel()
            pm = QPixmap()
            pm.loadFromData(svg.encode())
            lbl.setPixmap(pm)
            lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            lbl.setFixedSize(140, 100)
            layout.addWidget(lbl, alignment=Qt.AlignmentFlag.AlignCenter)

        name = QLabel(self._board_name)
        name.setStyleSheet(f"font-size: 13px; font-weight: 700; color: {C['text']};")
        name.setAlignment(Qt.AlignmentFlag.AlignCenter)
        name.setWordWrap(True)
        layout.addWidget(name)

        chip_label = QLabel(f"{chip} · {flash}")
        chip_label.setStyleSheet(f"font-size: 11px; color: {C['text_muted']};")
        chip_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(chip_label)

    def set_selected(self, sel: bool):
        self._selected = sel
        if sel:
            self.setStyleSheet(
                f"QFrame#card {{ background: {C['card_hover']}; "
                f"border: 2px solid {C['accent']}; border-radius: 14px; }}"
            )
        else:
            self.setStyleSheet(
                f"QFrame#card {{ background: {C['bg']}; "
                f"border: 1px solid {C['border']}; border-radius: 14px; }}"
                f"QFrame#card:hover {{ background: {C['card']}; }}"
            )

    def mousePressEvent(self, e):
        if e.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit(self._board_name)

    def enterEvent(self, e):
        if not self._selected:
            self.setStyleSheet(
                f"QFrame#card {{ background: {C['card']}; "
                f"border: 1px solid {C['accent']}; border-radius: 14px; }}"
            )

    def leaveEvent(self, e):
        if not self._selected:
            self.setStyleSheet(
                f"QFrame#card {{ background: {C['bg']}; "
                f"border: 1px solid {C['border']}; border-radius: 14px; }}"
            )


class BoardPicker(QWidget):
    board_selected = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._selected_board: str = ""
        self._cards: list[BoardCard] = []
        self._build()

    def _build(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        title = QLabel("Choose your ESP32 board")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet(
            f"font-size: 20px; font-weight: 700; color: {C['text']}; padding-bottom: 4px;"
        )
        layout.addWidget(title)

        sub = QLabel("Pick the board that matches your hardware. Check the label on the chip.")
        sub.setAlignment(Qt.AlignmentFlag.AlignCenter)
        sub.setWordWrap(True)
        sub.setStyleSheet(f"font-size: 14px; color: {C['text_muted']}; padding-bottom: 8px;")
        layout.addWidget(sub)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff
        )
        scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")

        grid_widget = QWidget()
        grid = QGridLayout(grid_widget)
        grid.setSpacing(12)
        grid.setContentsMargins(4, 4, 4, 4)

        board_names = list(BOARDS.keys())
        cols = min(3, len(board_names))
        for i, name in enumerate(board_names):
            card = BoardCard(name)
            card.clicked.connect(self._on_card_clicked)
            self._cards.append(card)
            grid.addWidget(card, i // cols, i % cols)

        scroll.setWidget(grid_widget)
        layout.addWidget(scroll, 1)

    def _on_card_clicked(self, name: str):
        self._selected_board = name
        for card in self._cards:
            card.set_selected(card._board_name == name)
        self.board_selected.emit(name)

    def selected_board(self) -> str:
        return self._selected_board


# ══ ui/drop_zone.py ═══════════════════════════════════════

class DropZone(QFrame):
    file_dropped = pyqtSignal(str)
    file_chosen = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.setObjectName("dropzone")
        self.setAcceptDrops(True)
        self.setMinimumHeight(280)
        self._enabled = True

        self._stack = QStackedLayout(self)

        # Layer 0: pulse background
        self._pulse = PulseWidget()
        self._pulse.start_pulse()
        self._stack.addWidget(self._pulse)

        # Layer 1: content
        content = QWidget()
        layout = QVBoxLayout(content)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setSpacing(12)
        layout.setContentsMargins(20, 20, 20, 20)

        self._arrow = AnimatedArrow("down")
        self._arrow.setFixedSize(32, 32)
        layout.addWidget(self._arrow, alignment=Qt.AlignmentFlag.AlignCenter)

        self._svg_label = QLabel()
        self._svg_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._svg_label.setFixedSize(180, 140)
        pixmap = QPixmap()
        pixmap.loadFromData(drop_zone_illustration().encode())
        self._svg_label.setPixmap(pixmap)
        layout.addWidget(self._svg_label)

        self._title = QLabel("Drop your .ino file here")
        self._title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._title.setStyleSheet(
            f"font-size: 22px; font-weight: 600; color: {C['text_muted']};"
        )
        layout.addWidget(self._title)

        self._sub = QLabel("or click to browse — any Arduino sketch works!")
        self._sub.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._sub.setStyleSheet(f"color: {C['text_faint']}; font-size: 16px;")
        layout.addWidget(self._sub)

        self._browse_btn = QPushButton("Choose file")
        self._browse_btn.setObjectName("secondary")
        self._browse_btn.setFixedWidth(200)
        self._browse_btn.clicked.connect(self._browse)
        self._browse_btn.setToolTip("Pick a .ino file from your computer")
        layout.addWidget(self._browse_btn, alignment=Qt.AlignmentFlag.AlignCenter)

        self._stack.addWidget(content)
        self._stack.setCurrentIndex(1)

        # Layer 2: disabled overlay
        self._disabled_overlay = QWidget()
        self._disabled_overlay.setStyleSheet(
            f"background: {C['bg']}; border-radius: 24px;"
        )
        dl = QVBoxLayout(self._disabled_overlay)
        dl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        dl.setSpacing(12)
        self._disabled_icon = QLabel("🔌")
        self._disabled_icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._disabled_icon.setStyleSheet("font-size: 36px; background: transparent;")
        dl.addWidget(self._disabled_icon)
        self._disabled_title = QLabel("No ESP32 connected")
        self._disabled_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._disabled_title.setStyleSheet(
            f"font-size: 20px; font-weight: 600; color: {C['text_faint']}; background: transparent;"
        )
        dl.addWidget(self._disabled_title)
        self._disabled_sub = QLabel("Select or set up a device from the sidebar first")
        self._disabled_sub.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._disabled_sub.setWordWrap(True)
        self._disabled_sub.setStyleSheet(
            f"font-size: 15px; color: {C['text_faint']}; background: transparent;"
        )
        dl.addWidget(self._disabled_sub)
        self._stack.addWidget(self._disabled_overlay)

        # Mascot overlay (hidden, shown on dragover)
        self._mascot_overlay = QWidget(self)
        self._mascot_overlay.setVisible(False)
        ml = QVBoxLayout(self._mascot_overlay)
        ml.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._drag_mascot = BouncyMascot()
        self._drag_mascot.set_mood("excited", 80)
        self._drag_mascot.set_bounce_style("excited")
        self._drag_mascot.start_bounce()
        ml.addWidget(self._drag_mascot, alignment=Qt.AlignmentFlag.AlignBottom)

        # Cycle hints
        self._hints = [
            "Drop your .ino file here",
            "Drag and drop Arduino sketches!",
            "Click to browse your files",
        ]
        self._hint_idx = 0
        self._hint_timer = QTimer(self)
        self._hint_timer.timeout.connect(self._cycle_hint)
        self._hint_timer.start(4000)

    def set_enabled(self, enabled: bool):
        self._enabled = enabled
        self._stack.setCurrentIndex(2 if not enabled else 1)
        self.setAcceptDrops(enabled)
        if enabled:
            self._pulse.start_pulse()
        else:
            self._pulse.stop_pulse()

    def _cycle_hint(self):
        self._hint_idx = (self._hint_idx + 1) % len(self._hints)
        self._title.setText(self._hints[self._hint_idx])

    def _browse(self):
        if not self._enabled:
            return
        path, _ = QFileDialog.getOpenFileName(
            self, "Choose an Arduino sketch", "",
            "Arduino Sketch (*.ino);;All Files (*)"
        )
        if path:
            self.file_chosen.emit(path)

    def dragEnterEvent(self, e: QDragEnterEvent):
        if not self._enabled:
            return
        if e.mimeData().hasUrls():
            urls = e.mimeData().urls()
            if any(u.toLocalFile().endswith(".ino") for u in urls):
                e.acceptProposedAction()
                self.setProperty("dragover", "true")
                self.style().unpolish(self)
                self.style().polish(self)
                self._mascot_overlay.setVisible(True)
                self._arrow.setVisible(False)

    def dragLeaveEvent(self, e):
        self.setProperty("dragover", "false")
        self.style().unpolish(self)
        self.style().polish(self)
        self._mascot_overlay.setVisible(False)
        self._arrow.setVisible(True)

    def dropEvent(self, e: QDropEvent):
        if not self._enabled:
            return
        self.setProperty("dragover", "false")
        self.style().unpolish(self)
        self.style().polish(self)
        self._mascot_overlay.setVisible(False)
        self._arrow.setVisible(True)
        for url in e.mimeData().urls():
            path = url.toLocalFile()
            if path.endswith(".ino"):
                self.file_dropped.emit(path)
                return


# ══ ui/device_list.py ═══════════════════════════════════════

class DeviceItemWidget(QWidget):
    checkbox_toggled = pyqtSignal()

    def __init__(self, device: Device, show_checkbox: bool = False):
        super().__init__()
        self.device = device
        self._show_checkbox = show_checkbox
        layout = QHBoxLayout(self)
        layout.setContentsMargins(14, 10, 14, 10)
        layout.setSpacing(10)

        if show_checkbox:
            self._checkbox = QCheckBox()
            self._checkbox.toggled.connect(self._on_check_toggled)
            self._checkbox.setStyleSheet(
                f"QCheckBox::indicator {{ width: 18px; height: 18px; }}"
                f"QCheckBox::indicator:checked {{ background: {C['accent']}; "
                f"border: 2px solid {C['accent']}; border-radius: 4px; }}"
                f"QCheckBox::indicator:unchecked {{ background: white; "
                f"border: 2px solid {C['border']}; border-radius: 4px; }}"
            )
            layout.addWidget(self._checkbox)

        self._mascot = BouncyMascot()
        self._mascot.setFixedSize(40, 48)
        if device.name and device.name != "Unknown":
            self._mascot.set_mood("happy" if device.status == "online" else "idle", 40)
        else:
            self._mascot.set_mood("surprise", 40)
        self._mascot.start_bounce()
        layout.addWidget(self._mascot)

        info = QVBoxLayout()
        info.setSpacing(2)
        name_lbl = QLabel(device.friendly_label)
        name_lbl.setStyleSheet(f"color: {C['text']}; font-weight: 600; font-size: 16px;")
        ip_lbl = QLabel(device.ip if device.ip else "Offline")
        ip_lbl.setStyleSheet(f"color: {C['text_muted']}; font-size: 14px;")
        info.addWidget(name_lbl)
        info.addWidget(ip_lbl)
        layout.addLayout(info)
        layout.addStretch()

        self._dot = BreathingDot()
        self._dot.set_online(device.status == "online")

        layout.addWidget(self._dot)

    def _on_check_toggled(self, checked: bool):
        self.checkbox_toggled.emit()

    def is_checked(self) -> bool:
        if self._show_checkbox:
            return self._checkbox.isChecked()
        return False

    def set_checked(self, checked: bool):
        if self._show_checkbox:
            self._checkbox.setChecked(checked)

    def enterEvent(self, e):
        if self.device.name and self.device.name != "Unknown":
            self._mascot.set_mood("peek", 40)
        super().enterEvent(e)

    def leaveEvent(self, e):
        if self.device.name and self.device.name != "Unknown":
            self._mascot.set_mood("happy" if self.device.status == "online" else "idle", 40)
        super().leaveEvent(e)


# ══ workers/serial_reader.py ═══════════════════════════════════════

import select


class SerialReaderWorker(QThread):
    data_received = pyqtSignal(str)
    connected = pyqtSignal()
    disconnected = pyqtSignal()
    error = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self._running = False
        self._mode: str = ""
        self._serial = None
        self._sock: socket.socket = None
        self._buffer = ""

    def connect_serial(self, port: str, baudrate: int = 115200):
        self._mode = "serial"
        self._port = port
        self._baudrate = baudrate
        self.start()

    def connect_tcp(self, host: str, port: int = 3232):
        self._mode = "tcp"
        self._host = host
        self._tcp_port = port
        self.start()

    def disconnect(self):
        self._running = False
        self.wait(2000)

    def send(self, data: str):
        if self._mode == "serial" and self._serial:
            try:
                self._serial.write(data.encode())
            except Exception as e:
                self.error.emit(f"Send failed: {e}")
        elif self._mode == "tcp" and self._sock:
            try:
                self._sock.sendall(data.encode())
            except Exception as e:
                self.error.emit(f"Send failed: {e}")

    def run(self):
        self._running = True
        try:
            if self._mode == "serial":
                self._run_serial()
            elif self._mode == "tcp":
                self._run_tcp()
        except Exception as e:
            self.error.emit(str(e))
        finally:
            self._cleanup()
            self.disconnected.emit()

    def _run_serial(self):
        import serial
        self._serial = serial.Serial(self._port, self._baudrate, timeout=0.5)
        self.connected.emit()
        while self._running:
            try:
                if self._serial.in_waiting:
                    raw = self._serial.read(self._serial.in_waiting)
                    text = raw.decode("utf-8", errors="replace")
                    self._buffer += text
                    if "\n" in self._buffer:
                        lines = self._buffer.split("\n")
                        for line in lines[:-1]:
                            self.data_received.emit(line + "\n")
                        self._buffer = lines[-1]
                else:
                    time.sleep(0.05)
            except serial.SerialException as e:
                self.error.emit(f"Serial error: {e}")
                break
            except Exception as e:
                self.error.emit(f"Read error: {e}")
                break

    def _run_tcp(self):
        self._sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._sock.settimeout(5.0)
        self._sock.connect((self._host, self._tcp_port))
        self._sock.setblocking(False)
        self.connected.emit()
        while self._running:
            try:
                r, _, _ = select.select([self._sock], [], [], 0.1)
                if r:
                    raw = self._sock.recv(4096)
                    if not raw:
                        break
                    text = raw.decode("utf-8", errors="replace")
                    self._buffer += text
                    if "\n" in self._buffer:
                        lines = self._buffer.split("\n")
                        for line in lines[:-1]:
                            self.data_received.emit(line + "\n")
                        self._buffer = lines[-1]
            except socket.timeout:
                continue
            except Exception as e:
                self.error.emit(f"TCP error: {e}")
                break

    def _cleanup(self):
        if self._serial:
            try:
                self._serial.close()
            except Exception:
                pass
            self._serial = None
        if self._sock:
            try:
                self._sock.close()
            except Exception:
                pass
            self._sock = None


# ══ workers/usb_flash.py ═══════════════════════════════════════

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
                    "Could not find esptool. Espy installation may be incomplete."
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

            # Flash base firmware
            self.progress.emit(40, "Installing Espy base firmware...")
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

            self.progress.emit(80, "Saving your settings...")
            # Settings will be configured via the captive portal on first boot
            time.sleep(1)

            self.progress.emit(100, "Done! Unplug the USB cable.")
            self.finished.emit()

        except subprocess.TimeoutExpired:
            self.failed.emit("Timed out. Is the ESP32 plugged in?")
        except Exception as e:
            self.failed.emit(str(e))


# ══ workers/compiler.py ═══════════════════════════════════════

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

    def run(self):
        cli = self._find_arduino_cli()
        if not cli:
            self.failed.emit(
                "Could not find the build tools. Espy installation may be incomplete.",
                "arduino-cli not found in PATH or bundled tools."
            )
            return

        tmp = tempfile.mkdtemp(prefix="espy_")
        try:
            sketch_name = Path(self.ino_path).stem
            sketch_dir = os.path.join(tmp, sketch_name)
            os.makedirs(sketch_dir)
            dest_ino = os.path.join(sketch_dir, f"{sketch_name}.ino")
            shutil.copy2(self.ino_path, dest_ino)

            missing_libs = [lib for lib in self.cfg.libraries if not lib.available and lib.needs_download]
            if missing_libs:
                self.progress.emit("Installing missing libraries...")
                for lib in missing_libs:
                    self.progress.emit(f"  Installing {lib.name}...")
                    r = subprocess.run(
                        [cli, "lib", "install", lib.name],
                        capture_output=True, text=True
                    )
                    if r.returncode != 0:
                        self.progress.emit(f"  Could not install '{lib.name}' — continuing anyway")

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


# ══ workers/ota.py ═══════════════════════════════════════

import urllib.request




class OtaWorker(QThread):
    progress = pyqtSignal(int, str)
    finished = pyqtSignal()
    failed = pyqtSignal(str)

    def __init__(self, device: Device, bin_path: str):
        super().__init__()
        self.device = device
        self.bin_path = bin_path

    def _post(self, path: str, data: bytes | dict,
              is_json: bool = False, timeout: int = 5) -> dict:
        url = f"http://{self.device.ip}:{self.device.port}{path}"
        if is_json:
            body = json.dumps(data).encode("utf-8")
            headers = {"Content-Type": "application/json"}
        else:
            body = data if isinstance(data, bytes) else b""
            headers = {"Content-Type": "application/octet-stream"}

        req = urllib.request.Request(url, data=body, headers=headers, method="POST")
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return json.loads(resp.read().decode("utf-8"))

    def run(self):
        try:
            with open(self.bin_path, "rb") as f:
                firmware = f.read()

            size = len(firmware)
            checksum = hashlib.sha256(firmware).hexdigest()
            deadline = time.time() + OTA_TIMEOUT_TOTAL

            # Phase 1: Handshake
            self.progress.emit(2, "Connecting to device...")
            resp = self._post("/espy/start", {
                "firmware_size_bytes": size,
                "checksum_sha256": checksum,
                "version_tag": f"user_fw_{int(time.time())}",
                "compiled_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            }, is_json=True, timeout=5)

            if resp.get("status") != "ready" and not resp.get("accepted"):
                self.failed.emit("Device is not ready to receive firmware. It may be busy.")
                return

            # Phase 2: Chunked upload
            chunks = [firmware[i:i+OTA_CHUNK_SIZE] for i in range(0, size, OTA_CHUNK_SIZE)]
            total = len(chunks)

            for i, chunk in enumerate(chunks):
                if time.time() > deadline:
                    self.failed.emit("Upload timed out. Try again with a stronger Wi-Fi signal.")
                    return

                pct = int(5 + (i / total) * 85)
                self.progress.emit(pct, f"Uploading... {i+1}/{total}")

                ok = False
                for attempt in range(3):
                    try:
                        cr = self._post(f"/espy/chunk/{i}", chunk, timeout=2)
                        if cr.get("status") == "ok" or cr.get("chunk") == i:
                            ok = True
                            break
                    except Exception:
                        if attempt == 2:
                            break
                        time.sleep(0.3)

                if not ok:
                    self.failed.emit(
                        f"Upload stopped at chunk {i+1}. "
                        "Check your Wi-Fi signal and try again."
                    )
                    return

            # Phase 3: Commit
            self.progress.emit(92, "Verifying firmware...")
            cr = self._post("/espy/commit", {
                "total_chunks": total,
                "total_bytes": size,
                "final_checksum": checksum, "checksum_type": "sha256",
            }, is_json=True, timeout=10)

            if cr.get("status") != "committed":
                reason = cr.get("reason", "unknown")
                self.failed.emit(
                    f"Verification failed ({reason}). "
                    "The device kept its previous firmware."
                )
                return

            # Phase 4: Post-reboot heartbeat
            self.progress.emit(95, "Rebooting device...")
            reboot_ms = cr.get("rebooting_in_ms", 2000)
            time.sleep(reboot_ms / 1000 + 1)

            pb_deadline = time.time() + POST_FLASH_HEARTBEAT_WINDOW
            while time.time() < pb_deadline:
                try:
                    req = urllib.request.Request(
                        f"http://{self.device.ip}:{self.device.port}/easyesp/alive"
                    )
                    with urllib.request.urlopen(req, timeout=2) as r:
                        alive = json.loads(r.read())
                        if alive.get("status") == "running":
                            self.progress.emit(100, "Done!")
                            self.device.firmware_version = alive.get("version", "unknown")
                            self.finished.emit()
                            return
                except Exception:
                    pass
                time.sleep(2)

            self.failed.emit(
                "Device didn't respond after reboot. "
                "The new firmware may have changed the OTA port, "
                "or the code has a bug. Plug in via USB to recover."
            )

        except Exception as e:
            self.failed.emit(str(e))


# ══ discovery/engine.py ═══════════════════════════════════════

class DiscoveryEngine(QThread):
    found = pyqtSignal(str, str, int)
    lost = pyqtSignal(str)
    phase_changed = pyqtSignal(str)
    done = pyqtSignal()

    def __init__(self):
        super().__init__()
        self._running = False
        self._known: dict[str, Device] = {}
        self._cache: dict = {}
        self._scan_interval = 12

    def run(self):
        self._running = True
        self._cache = load_cache()

        # Restore cached devices
        for name, data in self._cache.items():
            dev = Device.from_cache(data)
            self._known[name] = dev
            self.found.emit(name, dev.last_known_ip, dev.port)

        while self._running:
            for device_name, device in list(self._known.items()):
                if device.is_stale:
                    # Try to re-find stale devices
                    pass

            # Phase 1: mDNS
            self.phase_changed.emit("Looking for devices on Wi-Fi...")
            mdns_results = mdns_discover(timeout=1.5)
            for name, ip, port in mdns_results:
                self._upsert_device(name, ip, port)

            if not self._had_recent_activity():
                # Phase 2: cached IP
                self.phase_changed.emit("Checking known devices...")
                for name, data in list(self._cache.items()):
                    ip = data.get("last_known_ip", "")
                    if ip and check_cached_ip(ip, data.get("port", OTA_PORT)):
                        self._upsert_device(name, ip, data.get("port", OTA_PORT))

            if not self._had_recent_activity():
                # Phase 3: ARP scan
                self.phase_changed.emit("Scanning network for devices...")
                try:
                    arp_results = arp_scan(timeout=4)
                    for ip, name in arp_results:
                        self._upsert_device(name, ip, OTA_PORT)
                except Exception:
                    pass

            # Prune stale
            stale = [n for n, d in self._known.items() if d.is_stale]
            for name in stale:
                del self._known[name]
                self.lost.emit(name)

            self._save_cache()
            self.done.emit()

            # Wait before next scan cycle
            for _ in range(self._scan_interval * 2):
                if not self._running:
                    break
                time.sleep(0.5)

        self._save_cache()

    def stop(self):
        self._running = False
        self.wait()

    def _upsert_device(self, name: str, ip: str, port: int):
        now = time.time()
        if name in self._known:
            d = self._known[name]
            d.ip = ip
            d.port = port
            d.last_seen = now
        else:
            d = Device(name, ip, port)
            self._known[name] = d
            self.found.emit(name, ip, port)
        # Update cache
        if name not in self._cache:
            self._cache[name] = d.to_cache()
        else:
            self._cache[name]["last_known_ip"] = ip
            self._cache[name]["last_seen"] = now

    def _had_recent_activity(self) -> bool:
        now = time.time()
        for d in self._known.values():
            if now - d.last_seen < 8:
                return True
        return False

    def _save_cache(self):
        save_cache(self._cache)


# ══ ui/partition_editor.py ═══════════════════════════════════════

def partitions_to_csv(parts: list[dict]) -> str:
    lines = [
        "# Espy partition table",
        "# Name,         Type, SubType, Offset,   Size,     Flags",
    ]
    csv_map = {
        "nvs": ("data", "nvs"),
        "otadata": ("data", "ota"),
        "OTA Data": ("data", "ota"),
        "App (OTA 0)": ("app", "ota_0"),
        "app0": ("app", "ota_0"),
        "App (OTA 1)": ("app", "ota_1"),
        "app1": ("app", "ota_1"),
        "App": ("app", "ota_0"),
        "SPIFFS": ("data", "spiffs"),
        "LittleFS": ("data", "spiffs"),
        "Bootloader": ("app", "boot"),
        "Partition Table": ("data", "undefined"),
        "NVS": ("data", "nvs"),
        "espy_data": ("data", "nvs"),
    }
    offset_map = {
        "Bootloader": "0x1000",
        "NVS": "0x9000",
        "OTA Data": "0xE000",
        "otadata": "0x4000",
        "App (OTA 0)": "0x10000",
        "app0": "0x6000",
        "App": "0x10000",
    }
    for p in parts:
        name = p["name"]
        t, st = csv_map.get(name, ("data", "nvs"))
        off = p["offset"]
        sz = p["size"]
        sz_hex = _size_to_hex(sz)
        lines.append(f"{name.lower().replace(' ', '_')},{t},{st},{off},{sz_hex},")
    return "\n".join(lines)


def _size_to_hex(size_str: str) -> str:
    size_str = size_str.strip()
    if size_str.endswith("MB"):
        val = float(size_str.replace("MB", "").strip())
        return f"0x{int(val * 1024 * 1024):X}"
    elif size_str.endswith("KB"):
        val = float(size_str.replace("KB", "").strip())
        return f"0x{int(val * 1024):X}"
    elif size_str.endswith("B"):
        val = int(size_str.replace("B", "").strip())
        return f"0x{val:X}"
    return size_str


def csv_to_partitions(csv_text: str) -> list[dict]:
    parts = []
    for line in csv_text.strip().split("\n"):
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        fields = [f.strip() for f in line.split(",")]
        if len(fields) < 5:
            continue
        name, t, st, offset, size = fields[:5]
        size_friendly = _hex_to_friendly(size)
        parts.append({
            "name": name.replace("_", " ").title().replace("Nvs", "NVS").replace("Ota", "OTA").replace("Spiffs", "SPIFFS"),
            "offset": offset,
            "size": size_friendly,
        })
    return parts


def _hex_to_friendly(hex_size: str) -> str:
    try:
        val = int(hex_size, 16)
        if val >= 1024 * 1024:
            return f"{val / (1024 * 1024):.1f} MB"
        elif val >= 1024:
            return f"{val // 1024} KB"
        else:
            return f"{val} B"
    except ValueError:
        return hex_size


def get_max_sketch_size(flash_size: str, parts: list[dict]) -> int:
    total = 0
    for p in parts:
        sz = p["size"]
        try:
            if sz.endswith("MB"):
                total += int(float(sz.replace("MB", "")) * 1024 * 1024)
            elif sz.endswith("KB"):
                total += int(sz.replace("KB", "")) * 1024
            elif p["offset"] == "0x10000":
                continue
        except ValueError:
            pass
    return total


class PartitionEditor(QDialog):
    applied = pyqtSignal(InoConfig)

    FLASH_SIZE_OPTIONS = ["4MB", "8MB", "16MB"]

    def __init__(self, cfg: InoConfig, parent=None):
        super().__init__(parent)
        self.cfg = cfg
        self._manual_mode = False
        self.setWindowTitle("Partition Editor")
        self.setMinimumWidth(640)
        self.setMinimumHeight(560)
        self.setStyleSheet(stylesheet())
        self._build_ui()
        self._sync_from_cfg()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(16)
        layout.setContentsMargins(24, 20, 24, 20)

        title = QLabel("Partition Layout")
        title.setStyleSheet(f"font-size: 20px; font-weight: 700; color: {C['text']};")
        layout.addWidget(title)

        desc = QLabel(
            "Partitions divide the flash memory into sections. "
            "Choose a preset or edit the CSV manually."
        )
        desc.setWordWrap(True)
        desc.setStyleSheet(f"color: {C['text_muted']}; font-size: 14px;")
        layout.addWidget(desc)

        # Flash size row
        fs_row = QHBoxLayout()
        fs_label = QLabel("Flash Size:")
        fs_label.setStyleSheet(f"font-weight: 600; color: {C['text']};")
        self.flash_size_combo = QComboBox()
        self.flash_size_combo.addItems(self.FLASH_SIZE_OPTIONS)
        self.flash_size_combo.currentTextChanged.connect(self._on_flash_size_changed)
        fs_row.addWidget(fs_label)
        fs_row.addWidget(self.flash_size_combo, 1)
        layout.addLayout(fs_row)

        # Scheme row
        scheme_row = QHBoxLayout()
        scheme_label = QLabel("Scheme:")
        scheme_label.setStyleSheet(f"font-weight: 600; color: {C['text']};")
        self.scheme_combo = QComboBox()
        self.scheme_combo.currentIndexChanged.connect(self._on_scheme_changed)
        scheme_row.addWidget(scheme_label)
        scheme_row.addWidget(self.scheme_combo, 1)
        layout.addLayout(scheme_row)

        # Scheme description
        self._scheme_desc = QLabel()
        self._scheme_desc.setWordWrap(True)
        self._scheme_desc.setStyleSheet(f"color: {C['text_muted']}; font-size: 13px; padding: 0 0 6px 0;")
        layout.addWidget(self._scheme_desc)

        # Manual CSV toggle
        toggle_row = QHBoxLayout()
        self._manual_toggle = QCheckBox("Edit partition table directly (CSV)")
        self._manual_toggle.setStyleSheet(
            f"font-size: 14px; color: {C['text_muted']};"
        )
        self._manual_toggle.toggled.connect(self._on_manual_toggled)
        toggle_row.addWidget(self._manual_toggle)
        toggle_row.addStretch()
        layout.addLayout(toggle_row)

        # Partition table view (read-only)
        self._table_label = QLabel()
        self._table_label.setWordWrap(True)
        self._table_label.setStyleSheet(
            f"color: {C['text_muted']}; font-size: 13px; "
            f"font-family: 'Ubuntu Mono', 'Consolas', monospace; "
            f"background: white; border: 1px solid {C['border']}; "
            f"border-radius: 8px; padding: 12px;"
        )
        layout.addWidget(self._table_label)

        # Manual CSV editor (hidden by default)
        self._csv_editor = QPlainTextEdit()
        self._csv_editor.setPlaceholderText(
            "# Name, Type, SubType, Offset, Size, Flags\n"
            "nvs, data, nvs, 0x1000, 0x3000,\n"
            "app0, app, ota_0, 0x6000, 0x1E0000,\n"
        )
        self._csv_editor.setMinimumHeight(160)
        self._csv_editor.textChanged.connect(self._on_csv_edited)
        self._csv_editor.hide()
        layout.addWidget(self._csv_editor)

        # Summary
        self._summary_label = QLabel()
        self._summary_label.setStyleSheet(
            f"color: {C['info']}; font-size: 13px; font-weight: 600;"
        )
        layout.addWidget(self._summary_label)

        layout.addStretch()

        # Buttons
        btn_row = QHBoxLayout()
        btn_row.addStretch()
        cancel = QPushButton("Cancel")
        cancel.setObjectName("secondary")
        cancel.clicked.connect(self.reject)

        apply = QPushButton("Apply")
        apply.setObjectName("primary")
        apply.clicked.connect(self._apply)

        btn_row.addWidget(cancel)
        btn_row.addWidget(apply)
        layout.addLayout(btn_row)

    def _sync_from_cfg(self):
        fs = self.cfg.flash_size_override or self.cfg.flash_size
        if fs in self.FLASH_SIZE_OPTIONS:
            self.flash_size_combo.setCurrentText(fs)
        self._refresh_scheme_combo(fs)
        scheme = self.cfg.partition_scheme
        idx = self.scheme_combo.findData(scheme)
        if idx >= 0:
            self.scheme_combo.setCurrentIndex(idx)
        if self.cfg.partition_csv_override:
            self._manual_toggle.setChecked(True)
            self._csv_editor.setPlainText(self.cfg.partition_csv_override)

    def _refresh_scheme_combo(self, flash_size: str):
        self.scheme_combo.blockSignals(True)
        self.scheme_combo.clear()
        schemes = PARTITION_SCHEMES.get(flash_size, {})
        for key, (label, desc, _) in schemes.items():
            self.scheme_combo.addItem(label, userData=key)
        self.scheme_combo.blockSignals(False)
        if self.scheme_combo.count() > 0:
            self.scheme_combo.setCurrentIndex(0)
        self._on_scheme_changed()

    def _on_flash_size_changed(self, fs: str):
        self._refresh_scheme_combo(fs)

    def _on_scheme_changed(self):
        fs = self.flash_size_combo.currentText()
        key = self.scheme_combo.currentData()
        schemes = PARTITION_SCHEMES.get(fs, {})
        scheme = schemes.get(key)
        if scheme:
            _, desc, parts = scheme
            self._scheme_desc.setText(desc)
            self._show_partitions(parts)
            self._update_summary(parts)
        self._sync_csv_from_scheme()

    def _on_manual_toggled(self, checked: bool):
        self._manual_mode = checked
        self.scheme_combo.setEnabled(not checked)
        self._table_label.setVisible(not checked)
        self._csv_editor.setVisible(checked)
        if checked:
            self._sync_csv_from_scheme()

    def _sync_csv_from_scheme(self):
        fs = self.flash_size_combo.currentText()
        key = self.scheme_combo.currentData()
        parts = get_scheme_partitions(fs, key)
        csv = partitions_to_csv(parts)
        self._csv_editor.setPlainText(csv)

    def _on_csv_edited(self):
        if self._manual_mode:
            try:
                parts = csv_to_partitions(self._csv_editor.toPlainText())
                self._show_partitions(parts)
                self._update_summary(parts)
            except Exception:
                pass

    def _show_partitions(self, parts: list[dict]):
        lines = []
        lines.append(f"{'Name':<20} {'Offset':>10}  {'Size':>8}")
        lines.append("-" * 42)
        for p in parts:
            lines.append(f"{p['name']:<20} {p['offset']:>10}  {p['size']:>8}")
        self._table_label.setText("\n".join(lines))

    def _update_summary(self, parts: list[dict]):
        app_partitions = [p for p in parts if "ota" in p["name"].lower() or p["name"] == "App"]
        total_app = 0
        for p in app_partitions:
            s = p["size"]
            try:
                if s.endswith("MB"):
                    total_app += int(float(s.replace("MB", "")) * 1024 * 1024)
                elif s.endswith("KB"):
                    total_app += int(s.replace("KB", "")) * 1024
            except ValueError:
                pass
        if total_app:
            mb = total_app / (1024 * 1024)
            self._summary_label.setText(
                f"Total app space: {mb:.1f} MB  ·  "
                f"{len(app_partitions)} app partition{'s' if len(app_partitions) > 1 else ''}"
            )

    def _get_current_parts(self) -> list[dict]:
        if self._manual_mode:
            return csv_to_partitions(self._csv_editor.toPlainText())
        else:
            fs = self.flash_size_combo.currentText()
            key = self.scheme_combo.currentData()
            return get_scheme_partitions(fs, key)

    def _apply(self):
        self.cfg.flash_size_override = self.flash_size_combo.currentText()
        if self._manual_mode:
            self.cfg.partition_scheme = self.scheme_combo.currentData()
            self.cfg.partition_csv_override = self._csv_editor.toPlainText()
        else:
            self.cfg.partition_scheme = self.scheme_combo.currentData()
            self.cfg.partition_csv_override = ""
        self.applied.emit(self.cfg)
        self.accept()


# ══ ui/config_dialog.py ═══════════════════════════════════════

class ConfigDialog(QDialog):
    confirmed = pyqtSignal(InoConfig)

    def __init__(self, cfg: InoConfig, target_device: str = "", parent=None):
        super().__init__(parent)
        self.cfg = cfg
        self._target_device = target_device
        self.setWindowTitle("Check your settings")
        self.setMinimumWidth(680)
        self.setMinimumHeight(560)
        self.setStyleSheet(stylesheet())
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(18)
        layout.setContentsMargins(28, 24, 28, 24)

        # Header with mascot
        header = QHBoxLayout()
        title = QLabel("Here's what I found in your code:")
        title.setStyleSheet(f"font-size: 19px; font-weight: 700; color: {C['text']};")
        header.addWidget(title)
        header.addStretch()

        mascot = BouncyMascot()
        mascot.set_mood("wink", 64)
        mascot.setFixedSize(64, 76)
        mascot.start_bounce()
        mascot.setToolTip("I read your code and found these settings!")
        header.addWidget(mascot)
        layout.addLayout(header)

        # Config card
        card = QFrame()
        card.setObjectName("card")
        cl = QVBoxLayout(card)
        cl.setContentsMargins(20, 18, 20, 18)
        cl.setSpacing(14)

        # Target device (from Advanced mode sidebar selection)
        if self._target_device:
            target_row = QHBoxLayout()
            target_icon = QLabel("🎯")
            target_icon.setStyleSheet("font-size: 16px;")
            target_row.addWidget(target_icon)
            target_lbl = QLabel(f"Target: {self._target_device}")
            target_lbl.setStyleSheet(f"color: {C['accent']}; font-weight: 700; font-size: 15px;")
            target_row.addWidget(target_lbl)
            target_row.addStretch()
            cl.addLayout(target_row)

        # Board + Flash + Scheme in one row
        board_part_row = QHBoxLayout()
        board_part_row.setSpacing(10)

        bl = QLabel("Board:")
        bl.setStyleSheet(f"color: {C['text_muted']}; font-weight: 600; font-size: 16px;")
        board_part_row.addWidget(bl)

        self.board_combo = QComboBox()
        self.board_combo.addItems(list(BOARDS.keys()))
        idx = self.board_combo.findText(self.cfg.board)
        if idx >= 0:
            self.board_combo.setCurrentIndex(idx)
        self.board_combo.setToolTip("Which ESP32 model are you using? Check the label on the chip.")
        self.board_combo.currentTextChanged.connect(self._rebuild_partition_ui)
        board_part_row.addWidget(self.board_combo, 2)

        sep = QLabel("|")
        sep.setStyleSheet(f"color: {C['border']}; font-size: 14px;")
        board_part_row.addWidget(sep)

        fl = QLabel("Flash:")
        fl.setStyleSheet(f"color: {C['text_muted']}; font-weight: 600; font-size: 14px;")
        board_part_row.addWidget(fl)

        self._flash_combo = QComboBox()
        self._flash_combo.addItems(["4MB", "8MB", "16MB"])
        info = BOARDS.get(self.cfg.board, {})
        default_flash = info.get("flash_size", "4MB")
        if self.cfg.flash_size_override:
            default_flash = self.cfg.flash_size_override
        fi = self._flash_combo.findText(default_flash)
        if fi >= 0:
            self._flash_combo.setCurrentIndex(fi)
        self._flash_combo.currentTextChanged.connect(self._rebuild_partition_ui)
        self._flash_combo.setToolTip("Total flash memory size on your board")
        board_part_row.addWidget(self._flash_combo)

        sl = QLabel("Scheme:")
        sl.setStyleSheet(f"color: {C['text_muted']}; font-weight: 600; font-size: 14px;")
        board_part_row.addWidget(sl)

        self._scheme_combo = QComboBox()
        self._scheme_combo.currentTextChanged.connect(self._rebuild_partition_ui)
        self._scheme_combo.setToolTip("How the flash memory is divided up")
        board_part_row.addWidget(self._scheme_combo, 3)

        csv_btn = QPushButton("CSV")
        csv_btn.setObjectName("ghost")
        csv_btn.setStyleSheet(
            f"QPushButton{{ font-size: 12px; padding: 3px 8px; background: {C['card']}; "
            f"border: 1px solid {C['border']}; border-radius: 6px; }}"
            f"QPushButton:hover{{ background: {C['card_hover']}; }}"
        )
        csv_btn.setToolTip("Open full partition editor with manual CSV editing")
        csv_btn.clicked.connect(self._open_partition_editor)
        board_part_row.addWidget(csv_btn)

        cl.addLayout(board_part_row)

        # Board illustration + partition table side by side
        ill_table_row = QHBoxLayout()
        ill_table_row.setSpacing(16)

        self._board_ill = QLabel()
        self._board_ill.setFixedSize(130, 100)
        self._board_ill.setAlignment(Qt.AlignmentFlag.AlignCenter)
        ill_table_row.addWidget(self._board_ill)

        self._part_table = QLabel()
        self._part_table.setWordWrap(True)
        self._part_table.setStyleSheet(
            f"color: {C['text_muted']}; font-size: 13px; line-height: 1.5; "
            f"font-family: 'Courier New', monospace;"
        )
        self._part_table.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        ill_table_row.addWidget(self._part_table, 1)

        cl.addLayout(ill_table_row)

        self._rebuild_partition_ui()

        # Device name
        name_row = QHBoxLayout()
        nl = QLabel("Name:")
        nl.setStyleSheet(f"color: {C['text_muted']}; font-weight: 600; font-size: 16px;")
        self.name_edit = QLineEdit(self.cfg.device_name or "My ESP32")
        self.name_edit.setToolTip("A friendly name so you can find it in your device list")
        name_row.addWidget(nl)
        name_row.addWidget(self.name_edit, 1)
        cl.addLayout(name_row)

        # WiFi SSID
        ssid_row = QHBoxLayout()
        sl = QLabel("Wi-Fi:")
        sl.setStyleSheet(f"color: {C['text_muted']}; font-weight: 600; font-size: 16px;")
        self.ssid_edit = QLineEdit(self.cfg.wifi_ssid)
        self.ssid_edit.setPlaceholderText("Network name")
        self.ssid_edit.setToolTip("Your home network — the ESP32 connects to this for wireless updates")
        ssid_row.addWidget(sl)
        ssid_row.addWidget(self.ssid_edit, 1)
        cl.addLayout(ssid_row)

        # Password
        pass_row = QHBoxLayout()
        pl = QLabel("Password:")
        pl.setStyleSheet(f"color: {C['text_muted']}; font-weight: 600; font-size: 16px;")
        self.pass_edit = QLineEdit(self.cfg.wifi_password)
        self.pass_edit.setEchoMode(QLineEdit.EchoMode.Password)
        self.pass_edit.setToolTip("Saved on the ESP32 — never leaves your home network")
        pass_row.addWidget(pl)
        pass_row.addWidget(self.pass_edit, 1)
        cl.addLayout(pass_row)

        layout.addWidget(card)

        # Libraries
        if self.cfg.libraries:
            lib_title = QLabel("Libraries needed:")
            lib_title.setStyleSheet(f"font-weight: 600; color: {C['text']}; font-size: 16px;")
            layout.addWidget(lib_title)
            for i, lib in enumerate(self.cfg.libraries):
                status = "✓" if lib.available else "⬇"
                color = C['success'] if lib.available else C['warning']
                lbl = SlideLabel(f"  {status}  {lib.name}")
                lbl.setStyleSheet(f"color: {color}; font-size: 16px;")
                if lib.available:
                    lbl.setToolTip("This library is already installed. ✓")
                else:
                    lbl.setToolTip("I'll install this library before compiling.")
                if not lib.available:
                    pass  # keep color as warning
                lbl.animate_in(i * 80)
                layout.addWidget(lbl)

        # OTA conflict auto-fix
        if self.cfg.has_ota_conflict:
            warn = QFrame()
            warn.setObjectName("card")
            warn.setStyleSheet(
                f"QFrame#card {{ background: #FFF8EE; "
                f"border-color: {C['warning']}; }}"
            )
            wl = QVBoxLayout(warn)
            wl.setContentsMargins(16, 12, 16, 12)
            wl.setSpacing(6)
            wt = QLabel("⚠️  I found old OTA code in your sketch.")
            wt.setStyleSheet(f"color: {C['warning']}; font-weight: 600; font-size: 16px;")
            wb = QLabel(
                "Espy handles updates wirelessly for you. "
                "I'll remove the ArduinoOTA section automatically."
            )
            wb.setWordWrap(True)
            wb.setStyleSheet(f"color: {C['text_muted']}; font-size: 15px;")
            wl.addWidget(wt)
            wl.addWidget(wb)
            layout.addWidget(warn)

        # Warnings
        for w in self.cfg.warnings:
            wl = QLabel(f"  {w}")
            wl.setWordWrap(True)
            wl.setStyleSheet(f"color: {C['warning']}; font-size: 15px;")
            layout.addWidget(wl)

        # Buttons
        btn_row = QHBoxLayout()
        btn_row.addStretch()
        cancel = QPushButton("Cancel")
        cancel.setObjectName("secondary")
        cancel.clicked.connect(self.reject)
        cancel.setToolTip("Go back without flashing")

        flash = QPushButton("Flash Now →")
        flash.setObjectName("primary")
        flash.clicked.connect(self._confirm)
        flash.setToolTip("Start compiling and uploading!")

        btn_row.addWidget(cancel)
        btn_row.addWidget(flash)
        layout.addLayout(btn_row)

    def _rebuild_partition_ui(self):
        from PyQt6.QtGui import QPixmap

        # Update board illustration from current combo
        board_name = self.board_combo.currentText()
        info = BOARDS.get(board_name, {})
        fn = BOARD_ILLUSTRATIONS.get(board_name)
        if fn:
            pm = QPixmap()
            pm.loadFromData(fn(120).encode())
            self._board_ill.setPixmap(pm)
        else:
            self._board_ill.clear()

        # Sync flash combo to parsed/overridden value, else board default
        board_default = self.cfg.flash_size_override or self.cfg.flash_size or info.get("flash_size", "4MB")
        if self._flash_combo.currentText() != board_default:
            self._flash_combo.blockSignals(True)
            fi = self._flash_combo.findText(board_default)
            if fi >= 0:
                self._flash_combo.setCurrentIndex(fi)
            self._flash_combo.blockSignals(False)

        # Rebuild scheme combo for the selected flash size
        flash = self._flash_combo.currentText()
        self._scheme_combo.blockSignals(True)
        self._scheme_combo.clear()
        schemes = PARTITION_SCHEMES.get(flash, {})
        for key, (label, desc, _parts) in schemes.items():
            self._scheme_combo.addItem(f"{label} — {desc}", key)
        # Restore previously selected scheme if valid, else pick first
        for i in range(self._scheme_combo.count()):
            if self._scheme_combo.itemData(i) == self.cfg.partition_scheme:
                self._scheme_combo.setCurrentIndex(i)
                break
        else:
            if self._scheme_combo.count():
                self._scheme_combo.setCurrentIndex(0)
        self._scheme_combo.blockSignals(False)

        self._update_partition_table()

    def _update_partition_table(self):
        flash = self._flash_combo.currentText()
        scheme_key = self._scheme_combo.currentData() or "default_ota"
        parts = get_scheme_partitions(flash, scheme_key)

        board_name = self.board_combo.currentText()
        info = BOARDS.get(board_name, {})
        chip = info.get("chip", "?")
        sketch = info.get("max_sketch_size", 0)
        sketch_mb = f"{sketch / 1024 / 1024:.1f} MB" if sketch else "?"
        scheme_label = scheme_key.replace("_", " ").title()

        lines = [
            f"Chip: {chip} · {flash} · {scheme_label}",
            "",
        ]
        for p in parts:
            lines.append(f"  {p['name']:<18} {p['offset']:>8}  {p['size']:>6}")
        if self.cfg.partition_csv_override:
            lines.append("")
            lines.append("  ⚡ Custom CSV override active")
        self._part_table.setText("\n".join(lines))

    def _open_partition_editor(self):
        self.cfg.board = self.board_combo.currentText()
        self.cfg.flash_size_override = self._flash_combo.currentText()
        self.cfg.partition_scheme = self._scheme_combo.currentData() or "default_ota"
        editor = PartitionEditor(self.cfg, self)
        editor.applied.connect(self._on_partitions_applied)
        editor.exec()

    def _on_partitions_applied(self, cfg: InoConfig):
        self.cfg = cfg
        # Sync combos to the edited cfg
        fi = self._flash_combo.findText(cfg.flash_size_override or cfg.flash_size)
        if fi >= 0:
            self._flash_combo.setCurrentIndex(fi)
        self._rebuild_partition_ui()

    def _confirm(self):
        self.cfg.board = self.board_combo.currentText()
        self.cfg.flash_size_override = self._flash_combo.currentText()
        self.cfg.partition_scheme = self._scheme_combo.currentData() or "default_ota"
        self.cfg.device_name = self.name_edit.text().strip()
        self.cfg.wifi_ssid = self.ssid_edit.text().strip()
        self.cfg.wifi_password = self.pass_edit.text()
        self.confirmed.emit(self.cfg)
        self.accept()


# ══ ui/serial_logger.py ═══════════════════════════════════════

class SerialLogger(QWidget):
    closed = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._worker = SerialReaderWorker()
        self._worker.data_received.connect(self._on_data)
        self._worker.connected.connect(self._on_connected)
        self._worker.disconnected.connect(self._on_disconnected)
        self._worker.error.connect(self._on_worker_error)
        self._baudrates = ["9600", "19200", "38400", "57600", "74880", "115200", "230400", "921600"]
        self._auto_scroll = True
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(6)

        # ── Toolbar ──────────────────────────────────────────
        toolbar = QFrame()
        toolbar.setObjectName("card")
        tl = QHBoxLayout(toolbar)
        tl.setContentsMargins(12, 8, 12, 8)
        tl.setSpacing(8)

        self._mode_combo = QComboBox()
        self._mode_combo.addItems(["USB", "Wi-Fi"])
        self._mode_combo.currentTextChanged.connect(self._on_mode_changed)
        self._mode_combo.setToolTip("USB: connect via serial cable · Wi-Fi: connect via network")
        tl.addWidget(QLabel("Mode:"))
        tl.addWidget(self._mode_combo)

        tl.addWidget(QLabel("|"))

        # USB controls
        self._port_combo = QComboBox()
        self._port_combo.setMinimumWidth(160)
        self._port_combo.setToolTip("Serial port")
        self._port_combo.addItem("Detecting ports...")
        tl.addWidget(self._port_combo)

        self._baud_combo = QComboBox()
        self._baud_combo.addItems(self._baudrates)
        self._baud_combo.setCurrentText("115200")
        self._baud_combo.setToolTip("Baud rate")
        tl.addWidget(self._baud_combo)

        # Wi-Fi controls (hidden by default)
        self._host_input = QLineEdit()
        self._host_input.setPlaceholderText("192.168.1.x")
        self._host_input.setFixedWidth(140)
        self._host_input.setToolTip("ESP32 IP address")
        self._host_input.hide()
        tl.addWidget(self._host_input)

        self._tcp_port_input = QLineEdit()
        self._tcp_port_input.setPlaceholderText("3232")
        self._tcp_port_input.setFixedWidth(60)
        self._tcp_port_input.setToolTip("TCP port (default: 3232)")
        self._tcp_port_input.hide()
        tl.addWidget(self._tcp_port_input)

        self._connect_btn = QPushButton("Connect")
        self._connect_btn.setObjectName("primary")
        self._connect_btn.clicked.connect(self._toggle_connection)
        self._connect_btn.setToolTip("Connect to device")
        tl.addWidget(self._connect_btn)

        tl.addStretch()

        self._back_btn = QPushButton("← Back")
        self._back_btn.setObjectName("ghost")
        self._back_btn.clicked.connect(self._go_back)
        self._back_btn.setToolTip("Return to main page")
        tl.addWidget(self._back_btn)

        self._clear_btn = QPushButton("Clear")
        self._clear_btn.setObjectName("ghost")
        self._clear_btn.setStyleSheet(
            f"QPushButton{{ font-size: 13px; padding: 4px 10px; background: {C['card']}; "
            f"border: 1px solid {C['border']}; border-radius: 6px; }}"
            f"QPushButton:hover{{ background: {C['card_hover']}; }}"
        )
        self._clear_btn.clicked.connect(self._clear_log)
        self._clear_btn.setToolTip("Clear output")
        tl.addWidget(self._clear_btn)

        layout.addWidget(toolbar)

        # ── Status bar ───────────────────────────────────────
        self._status_lbl = QLabel("Disconnected")
        self._status_lbl.setStyleSheet(f"color: {C['text_muted']}; font-size: 13px; padding: 2px 8px;")
        layout.addWidget(self._status_lbl)

        # ── Log output ───────────────────────────────────────
        self._output = QTextEdit()
        self._output.setReadOnly(True)
        self._output.setFont(QFont("Courier New", 11))
        self._output.setStyleSheet(
            f"QTextEdit {{ background: #1a1a2e; color: #e0e0e0; border: none; "
            f"border-radius: 8px; padding: 8px; }}"
        )
        self._output.verticalScrollBar().valueChanged.connect(self._on_scroll)
        layout.addWidget(self._output, 1)

        # ── Send bar ─────────────────────────────────────────
        send_bar = QFrame()
        send_bar.setObjectName("card")
        send_bar.setStyleSheet(f"QFrame#card {{ border-top: 1px solid {C['border']}; }}")
        sl = QHBoxLayout(send_bar)
        sl.setContentsMargins(12, 6, 12, 6)
        sl.setSpacing(8)

        self._send_input = QLineEdit()
        self._send_input.setPlaceholderText("Type a command...")
        self._send_input.setStyleSheet(f"font-size: 14px; padding: 4px 8px;")
        self._send_input.returnPressed.connect(self._send)
        sl.addWidget(self._send_input, 1)

        self._send_btn = QPushButton("Send")
        self._send_btn.setObjectName("primary")
        self._send_btn.setEnabled(False)
        self._send_btn.clicked.connect(self._send)
        self._send_btn.setToolTip("Send command to device")
        sl.addWidget(self._send_btn)

        layout.addWidget(send_bar)

        # Refresh ports on startup
        QTimer.singleShot(200, self._refresh_ports)

    def _on_mode_changed(self, mode: str):
        is_usb = mode == "USB"
        self._port_combo.setVisible(is_usb)
        self._baud_combo.setVisible(is_usb)
        self._host_input.setVisible(not is_usb)
        self._tcp_port_input.setVisible(not is_usb)
        if is_usb:
            self._refresh_ports()

    def _refresh_ports(self):
        try:
            import serial.tools.list_ports
            ports = list(serial.tools.list_ports.comports())
            self._port_combo.clear()
            for p in ports:
                self._port_combo.addItem(f"{p.device} ({p.description})", p.device)
            if not ports:
                self._port_combo.addItem("No ports found")
        except Exception:
            self._port_combo.clear()
            self._port_combo.addItem("Could not scan ports")

    def _toggle_connection(self):
        if self._worker.isRunning():
            self._disconnect()
        else:
            self._connect()

    def _connect(self):
        if self._mode_combo.currentText() == "USB":
            if self._port_combo.count() == 0 or self._port_combo.currentData() is None:
                self._log_line("No serial port selected")
                return
            port = self._port_combo.currentData()
            baud = int(self._baud_combo.currentText())
            self._log_line(f"Connecting to {port} @ {baud} baud...")
            self._status_lbl.setText(f"Connecting to {port}...")
            self._worker.connect_serial(port, baud)
        else:
            host = self._host_input.text().strip()
            if not host:
                self._log_line("Enter an IP address")
                return
            port_text = self._tcp_port_input.text().strip() or "3232"
            try:
                tcp_port = int(port_text)
            except ValueError:
                self._log_line("Invalid port number")
                return
            self._log_line(f"Connecting to {host}:{tcp_port}...")
            self._status_lbl.setText(f"Connecting to {host}:{tcp_port}...")
            self._worker.connect_tcp(host, tcp_port)

    def _disconnect(self):
        self._worker.disconnect()
        self._connect_btn.setText("Connect")
        self._connect_btn.setEnabled(True)
        self._send_btn.setEnabled(False)
        self._send_input.setEnabled(False)
        self._status_lbl.setText("Disconnected")
        self._log_line("Disconnected")

    def _on_connected(self):
        self._connect_btn.setText("Disconnect")
        self._send_btn.setEnabled(True)
        self._send_input.setEnabled(True)
        self._status_lbl.setText("Connected")
        self._log_line("Connected")

    def _on_disconnected(self):
        self._connect_btn.setText("Connect")
        self._connect_btn.setEnabled(True)
        self._send_btn.setEnabled(False)
        self._send_input.setEnabled(False)
        self._status_lbl.setText("Disconnected")

    def _on_worker_error(self, msg: str):
        self._log_line(f"ERROR: {msg}")
        self._status_lbl.setText(f"Error: {msg}")
        self._disconnect()

    def _on_data(self, text: str):
        self._log_line(text.rstrip())

    def _send(self):
        text = self._send_input.text()
        if text and self._worker.isRunning():
            self._worker.send(text + "\n")
            self._log_line(f">>> {text}")
            self._send_input.clear()

    def _clear_log(self):
        self._output.clear()

    def _log_line(self, text: str):
        self._output.append(text)
        if self._auto_scroll:
            sb = self._output.verticalScrollBar()
            sb.setValue(sb.maximum())

    def _on_scroll(self, val: int):
        sb = self._output.verticalScrollBar()
        self._auto_scroll = val >= sb.maximum() - 5

    def _go_back(self):
        self._worker.disconnect()
        self.closed.emit()

    def closeEvent(self, event):
        self._worker.disconnect()
        self.closed.emit()
        super().closeEvent(event)


# ══ ui/progress_scene.py ═══════════════════════════════════════

class StepDot(QLabel):
    def __init__(self, label: str, parent=None):
        super().__init__(parent)
        self.setText("○")
        self._label = label
        self.set_active(False)

    def set_active(self, active: bool):
        self.setText("●" if active else "○")
        color = C['accent'] if active else C['text_faint']
        self.setStyleSheet(f"font-size: 24px; color: {color};")

    def set_done(self):
        self.setText("✓")
        self.setStyleSheet(f"font-size: 24px; color: {C['success']};")


class ProgressScene(QWidget):
    save_binary_requested = pyqtSignal(str)
    flash_now_requested = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self._mascot = BouncyMascot()
        self._title = QLabel()
        self._status = QLabel()
        self._bar = MascotProgressBar()
        self._back_btn = QPushButton("← Back")
        self._error_detail_btn = QPushButton("Copy for AI assistant")
        self._save_btn = QPushButton("Save Binary")
        self._flash_btn = QPushButton("Flash Now")
        self._step_dots: list[StepDot] = []
        self._confetti = ConfettiWidget()
        self._loading_dots = LoadingDots()
        self._checkmark = AnimatedCheckmark()
        self._bin_path: str = ""
        self._last_friendly: str = ""
        self._last_raw: str = ""
        self._error_cfg: object = None
        self._build_ui()
        self._state = "idle"

    def _build_ui(self):
        self.setStyleSheet(f"background: {C['bg']};")
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setContentsMargins(50, 40, 50, 40)
        layout.setSpacing(14)

        # Confetti
        self._confetti.setVisible(False)
        layout.addWidget(self._confetti, stretch=1)

        # Mascot
        self._mascot.setFixedSize(160, 180)
        self._mascot.set_mood("idle", 160)
        layout.addWidget(self._mascot, alignment=Qt.AlignmentFlag.AlignCenter)

        # Loading dots
        self._loading_dots.setVisible(False)
        layout.addWidget(self._loading_dots, alignment=Qt.AlignmentFlag.AlignCenter)

        # Checkmark
        self._checkmark.setFixedSize(120, 120)
        self._checkmark.setVisible(False)
        layout.addWidget(self._checkmark, alignment=Qt.AlignmentFlag.AlignCenter)

        # Title
        self._title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._title.setStyleSheet(f"font-size: {T}px; font-weight: 700; color: {C['text']};")
        layout.addWidget(self._title)

        # Step dots
        steps_layout = QHBoxLayout()
        steps_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        steps_layout.setSpacing(6)
        for step_name in ["Compile", "Upload", "Verify", "Done"]:
            dot = StepDot("")
            steps_layout.addWidget(dot)
            if step_name != "Done":
                arrow = QLabel("→")
                arrow.setStyleSheet(f"color: {C['text_faint']}; font-size: 18px;")
                steps_layout.addWidget(arrow)
            self._step_dots.append(dot)
        layout.addLayout(steps_layout)

        step_label_layout = QHBoxLayout()
        step_label_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        step_label_layout.setSpacing(28)
        for step_name in ["Compile", "Upload", "Verify", "Done"]:
            lbl = QLabel(step_name)
            lbl.setStyleSheet(f"color: {C['text_faint']}; font-size: 14px;")
            lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            step_label_layout.addWidget(lbl)
        layout.addLayout(step_label_layout)

        # Status
        self._status.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._status.setStyleSheet(f"color: {C['text_muted']}; font-size: {B}px;")
        layout.addWidget(self._status)

        # Mascot progress bar
        self._bar.setFixedWidth(380)
        layout.addWidget(self._bar, alignment=Qt.AlignmentFlag.AlignCenter)

        # Error button
        self._error_detail_btn.setObjectName("ghost")
        self._error_detail_btn.hide()
        self._error_detail_btn.clicked.connect(self._copy_error)
        layout.addWidget(self._error_detail_btn, alignment=Qt.AlignmentFlag.AlignCenter)

        # Save / Flash action row (hidden until compilation ready)
        action_row = QHBoxLayout()
        action_row.setAlignment(Qt.AlignmentFlag.AlignCenter)
        action_row.setSpacing(16)

        self._save_btn.setObjectName("secondary")
        self._save_btn.clicked.connect(self._on_save)
        self._save_btn.hide()
        action_row.addWidget(self._save_btn)

        self._flash_btn.setObjectName("primary")
        self._flash_btn.clicked.connect(self._on_flash)
        self._flash_btn.hide()
        action_row.addWidget(self._flash_btn)

        layout.addLayout(action_row)

        # Back button
        self._back_btn.setObjectName("secondary")
        self._back_btn.hide()
        self._back_btn.clicked.connect(self._go_back)
        layout.addWidget(self._back_btn, alignment=Qt.AlignmentFlag.AlignCenter)

    def start_compile(self, board: str = ""):
        self._state = "compile"
        self._checkmark.setVisible(False)
        self._loading_dots.setVisible(True)
        self._loading_dots.start()
        self._mascot.set_mood("focused", 160)
        self._mascot.set_bounce_style("idle")
        self._mascot.start_bounce()
        self._title.setText("Cooking your code...")
        self._status.setText(f"Building for {board}" if board else "Compiling...")
        self._bar.set_value(0)
        self._back_btn.hide()
        self._error_detail_btn.hide()
        self._confetti.setVisible(False)
        self._confetti.stop()
        self._update_steps(0)

    def start_ota(self):
        self._state = "upload"
        self._mascot.set_mood("sweat", 160)
        self._title.setText("Sending to your ESP32...")
        self._status.setText("Connecting...")
        self._bar.set_value(5)
        self._update_steps(1)
        self._loading_dots.setVisible(True)
        self._loading_dots.start()

    def set_status(self, msg: str):
        self._status.setText(msg)

    def set_progress(self, pct: int, msg: str):
        self._bar.set_value(pct)
        self._status.setText(msg)
        if pct < 90:
            self._update_steps(1)
        elif pct < 100:
            self._update_steps(2)

    def show_success(self, device_name: str):
        self._state = "done"
        self._loading_dots.stop()
        self._loading_dots.setVisible(False)
        self._mascot.stop_bounce()
        self._mascot.set_mood("excited", 160)
        self._mascot.set_bounce_style("excited")
        self._mascot.start_bounce()
        self._checkmark.setVisible(True)
        QTimer.singleShot(200, self._checkmark.start_animate)

        self._title.setText("It works! 🎉")
        self._status.setText(f"{device_name} is running your code.")
        self._bar.set_value(100)
        self._update_steps(3)

        self._confetti.setVisible(True)
        self._confetti.start(80)
        QTimer.singleShot(5000, self._confetti.stop)

        self._back_btn.setText("← Flash another")
        self._back_btn.show()

    def show_compilation_ready(self, bin_path: str, has_device: bool):
        self._state = "ready"
        self._bin_path = bin_path
        self._loading_dots.stop()
        self._loading_dots.setVisible(False)
        self._checkmark.setVisible(False)
        self._mascot.set_mood("wink", 160)
        self._mascot.set_bounce_style("idle")
        self._mascot.start_bounce()
        self._title.setText("Compilation ready!")
        self._status.setText("Connect an ESP32 and click Flash Now, or save the binary for later.")
        self._bar.set_value(100)
        self._update_steps(1)
        self._step_dots[0].set_done()

        self._save_btn.show()
        self._flash_btn.show()
        self._flash_btn.setEnabled(has_device)
        self._flash_btn.setText("Flash Now" if has_device else "Flash Now (no device)")
        self._back_btn.setText("← Back")
        self._back_btn.show()

    def show_error(self, friendly: str, raw: str):
        self._state = "error"
        self._last_friendly = friendly
        self._last_raw = raw
        self._loading_dots.stop()
        self._loading_dots.setVisible(False)
        self._mascot.set_mood("surprise", 160)
        self._checkmark.setVisible(False)
        self._title.setText("Something went wrong")
        self._status.setText(friendly)
        self._error_detail_btn.show()
        self._back_btn.setText("← Try again")
        self._back_btn.show()

    def set_error_context(self, cfg):
        self._error_cfg = cfg

    def set_flash_enabled(self, enabled: bool):
        self._flash_btn.setEnabled(enabled)
        self._flash_btn.setText("Flash Now" if enabled else "Flash Now (no device)")

    def _on_save(self):
        if self._bin_path:
            self.save_binary_requested.emit(self._bin_path)

    def _on_flash(self):
        if self._bin_path:
            self.flash_now_requested.emit(self._bin_path)

    def _update_steps(self, active_index: int):
        for i, dot in enumerate(self._step_dots):
            if i < active_index:
                dot.set_done()
            elif i == active_index:
                dot.set_active(True)
            else:
                dot.set_active(False)

    def _copy_error(self):
        parts = []
        cfg = self._error_cfg
        if cfg:
            parts.append(f"Board: {cfg.board}")
            parts.append(f"Flash: {cfg.flash_size_override or cfg.flash_size}")
            parts.append(f"Partition: {cfg.partition_scheme}")
            if cfg.device_name:
                parts.append(f"Device: {cfg.device_name}")
            if cfg.wifi_ssid:
                parts.append(f"Wi-Fi: {cfg.wifi_ssid}")
            parts.append("")
        parts.append(self._last_friendly or "")
        if self._last_raw:
            parts.append("")
            parts.append("--- Build output ---")
            parts.append(self._last_raw.strip()[:2000])
        QApplication.clipboard().setText("\n".join(parts))
        self._error_detail_btn.setText("✓ Copied!")

    def _go_back(self):
        parent = self.parentWidget()
        if parent and hasattr(parent, "setCurrentIndex"):
            parent.setCurrentIndex(0)


# ══ ui/setup_wizard.py ═══════════════════════════════════════

class SetupWizard(QWidget):
    finished = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._current_step = 0
        self._steps = ["Plug in", "Wi-Fi", "Name", "Flash"]
        self._usb_worker = None
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(40, 30, 40, 30)
        layout.setSpacing(18)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Step indicator
        self._step_indicator = QLabel()
        self._step_indicator.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._step_indicator.setStyleSheet(f"color: {C['text_muted']}; font-size: 16px;")
        layout.addWidget(self._step_indicator)

        # Progress dots (animated)
        dots_layout = QHBoxLayout()
        dots_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._step_dots: list[QLabel] = []
        for i, name in enumerate(self._steps):
            dot = QLabel("○")
            dot.setStyleSheet(f"font-size: 24px; color: {C['text_faint']};")
            self._step_dots.append(dot)
            dots_layout.addWidget(dot)
            if i < len(self._steps) - 1:
                line = QLabel("——")
                line.setStyleSheet(f"color: {C['text_faint']}; font-size: 18px;")
                dots_layout.addWidget(line)
        layout.addLayout(dots_layout)

        # Step labels
        step_label_layout = QHBoxLayout()
        step_label_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        step_label_layout.setSpacing(16)
        for name in self._steps:
            lbl = QLabel(name)
            lbl.setStyleSheet(f"color: {C['text_faint']}; font-size: 12px;")
            lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            step_label_layout.addWidget(lbl)
        layout.addLayout(step_label_layout)

        # Content area
        self._content_stack = QWidget()
        self._content_layout = QVBoxLayout(self._content_stack)
        self._content_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._content_layout.setSpacing(16)
        layout.addWidget(self._content_stack)

        # Navigation
        nav_layout = QHBoxLayout()
        nav_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        nav_layout.setSpacing(20)

        self._back_btn = QPushButton("← Back")
        self._back_btn.setObjectName("secondary")
        self._back_btn.clicked.connect(self._go_back)
        self._back_btn.setVisible(False)
        nav_layout.addWidget(self._back_btn)

        self._next_btn = QPushButton("Next →")
        self._next_btn.setObjectName("primary")
        self._next_btn.clicked.connect(self._go_next)
        nav_layout.addWidget(self._next_btn)

        layout.addLayout(nav_layout)

        self._render_step(0)

    def _render_step(self, step: int):
        for i in reversed(range(self._content_layout.count())):
            w = self._content_layout.itemAt(i).widget()
            if w:
                w.deleteLater()

        self._current_step = step
        self._back_btn.setVisible(step > 0)
        self._step_indicator.setText(f"Step {step + 1} of {len(self._steps)}")

        # Update dots with animation
        for i, dot in enumerate(self._step_dots):
            if i < step:
                dot.setText("●")
                dot.setStyleSheet(f"font-size: 24px; color: {C['success']};")
            elif i == step:
                dot.setText("●")
                dot.setStyleSheet(f"font-size: 24px; color: {C['accent']};")
            else:
                dot.setText("○")
                dot.setStyleSheet(f"font-size: 24px; color: {C['text_faint']};")

        if step == 0:
            self._render_plug_step()
        elif step == 1:
            self._render_wifi_step()
        elif step == 2:
            self._render_name_step()
        elif step == 3:
            self._render_flash_step()

    def _render_plug_step(self):
        vis_row = QHBoxLayout()
        vis_row.setAlignment(Qt.AlignmentFlag.AlignCenter)
        vis_row.setSpacing(12)

        mascot = BouncyMascot()
        mascot.set_mood("happy", 60)
        mascot.setFixedSize(60, 72)
        mascot.start_bounce()
        vis_row.addWidget(mascot)

        from ui.illustrations import usb_illustration
        usb_lbl = QLabel()
        pm = QPixmap()
        pm.loadFromData(usb_illustration(80).encode())
        usb_lbl.setPixmap(pm)
        usb_lbl.setFixedSize(80, 64)
        vis_row.addWidget(usb_lbl)

        self._content_layout.addLayout(vis_row)

        title = QLabel("Plug in your ESP32")
        title.setStyleSheet(f"font-size: {EASY_MODE_TITLE_FONT}px; font-weight: 700; color: {C['text']};")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._content_layout.addWidget(title)

        sub = QLabel(
            "Connect the USB cable between your computer\n"
            "and the ESP32 board. Then click Next."
        )
        sub.setAlignment(Qt.AlignmentFlag.AlignCenter)
        sub.setStyleSheet(f"color: {C['text_muted']}; font-size: {EASY_MODE_BODY_FONT}px;")
        self._content_layout.addWidget(sub)

        self._port_label = QLabel("")
        self._port_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._port_label.setStyleSheet(f"color: {C['success']}; font-size: 17px;")
        self._content_layout.addWidget(self._port_label)

        self._check_port()

    def _check_port(self):
        ports = usb_probe()
        if ports:
            self._port_label.setText(f"✓ Found it! ({ports[0]['port']})")
            self._next_btn.setEnabled(True)
        else:
            self._port_label.setText("Looking for your ESP32... 🔍")
            self._next_btn.setEnabled(False)
            QTimer.singleShot(2000, self._check_port)

    def _render_wifi_step(self):
        pw = PulsingWifi()
        pw.setFixedSize(100, 80)
        self._content_layout.addWidget(pw, alignment=Qt.AlignmentFlag.AlignCenter)

        mascot = BouncyMascot()
        mascot.set_mood("searching", 60)
        mascot.setFixedSize(60, 72)
        mascot.start_bounce()
        self._content_layout.addWidget(mascot, alignment=Qt.AlignmentFlag.AlignCenter)

        title = QLabel("Connect to Wi-Fi")
        title.setStyleSheet(f"font-size: {EASY_MODE_TITLE_FONT}px; font-weight: 700; color: {C['text']};")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._content_layout.addWidget(title)

        self._setup_ssid = QLineEdit()
        self._setup_ssid.setPlaceholderText("Your Wi-Fi name (e.g. MyHomeNetwork)")
        self._setup_ssid.setMinimumWidth(320)
        self._setup_ssid.setToolTip("The name of your home Wi-Fi network")
        self._content_layout.addWidget(self._setup_ssid)

        self._setup_password = QLineEdit()
        self._setup_password.setEchoMode(QLineEdit.EchoMode.Password)
        self._setup_password.setPlaceholderText("Wi-Fi password")
        self._setup_password.setMinimumWidth(320)
        self._setup_password.setToolTip("Saved on your ESP32, not your computer")
        self._content_layout.addWidget(self._setup_password)

        self._setup_ssid.textChanged.connect(self._validate_wifi)
        self._setup_password.textChanged.connect(self._validate_wifi)

        sub = QLabel("This is saved on your ESP32, not on your computer.")
        sub.setAlignment(Qt.AlignmentFlag.AlignCenter)
        sub.setStyleSheet(f"color: {C['text_faint']}; font-size: 15px;")
        self._content_layout.addWidget(sub)

    def _validate_wifi(self):
        ssid = self._setup_ssid.text().strip()
        pw = self._setup_password.text()
        self._next_btn.setEnabled(bool(ssid and pw))

    def _render_name_step(self):
        mascot = BouncyMascot()
        mascot.set_mood("happy", 100)
        mascot.setFixedSize(100, 120)
        mascot.start_bounce()
        self._content_layout.addWidget(mascot, alignment=Qt.AlignmentFlag.AlignCenter)

        title = QLabel("What should I call this device?")
        title.setStyleSheet(f"font-size: {EASY_MODE_TITLE_FONT}px; font-weight: 700; color: {C['text']};")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._content_layout.addWidget(title)

        self._setup_name = QLineEdit()
        self._setup_name.setPlaceholderText("e.g. Kitchen Light, Garage Sensor")
        self._setup_name.setText("My ESP32")
        self._setup_name.setMinimumWidth(320)
        self._setup_name.setToolTip("Pick a name you'll recognize in your device list")
        self._content_layout.addWidget(self._setup_name)

        # Name suggestions
        chips_layout = QHBoxLayout()
        chips_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        chips_layout.setSpacing(8)
        for suggestion in ["Kitchen Light", "Garage Sensor", "Plant Monitor"]:
            chip = QPushButton(suggestion)
            chip.setObjectName("ghost")
            chip.setStyleSheet(
                f"QPushButton{{background: {C['card']}; border: 1px solid {C['border']}; "
                f"border-radius: 16px; padding: 8px 16px; font-size: 14px; color: {C['text_muted']};}}"
                f"QPushButton:hover{{background: {C['card_hover']}; color: {C['accent']};}}"
            )
            chip.clicked.connect(lambda _, s=suggestion: self._setup_name.setText(s))
            chips_layout.addWidget(chip)
        self._content_layout.addLayout(chips_layout)

        sub = QLabel("Pick a name you'll recognize in the device list.")
        sub.setAlignment(Qt.AlignmentFlag.AlignCenter)
        sub.setStyleSheet(f"color: {C['text_faint']}; font-size: 15px;")
        self._content_layout.addWidget(sub)

    def _render_flash_step(self):
        mascot = BouncyMascot()
        mascot.set_mood("excited", 100)
        mascot.setFixedSize(100, 120)
        mascot.start_bounce()
        self._content_layout.addWidget(mascot, alignment=Qt.AlignmentFlag.AlignCenter)

        self._flash_title = QLabel("Ready to set up your ESP32!")
        self._flash_title.setStyleSheet(f"font-size: {EASY_MODE_TITLE_FONT}px; font-weight: 700; color: {C['text']};")
        self._flash_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._content_layout.addWidget(self._flash_title)

        self._flash_status = QLabel("")
        self._flash_status.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._flash_status.setStyleSheet(f"color: {C['text_muted']}; font-size: {EASY_MODE_BODY_FONT}px;")
        self._content_layout.addWidget(self._flash_status)

        self._flash_bar = MascotProgressBar()
        self._flash_bar.set_value(0, animate=False)
        self._flash_bar.hide()
        self._content_layout.addWidget(self._flash_bar, alignment=Qt.AlignmentFlag.AlignCenter)

        self._next_btn.setText("Start Setup →")
        try:
            self._next_btn.clicked.disconnect()
        except TypeError:
            pass
        self._next_btn.clicked.connect(self._start_usb_flash)

    def _start_usb_flash(self):
        name = self._setup_name.text().strip() or "My ESP32"
        ssid = self._setup_ssid.text().strip()
        password = self._setup_password.text()
        port = autodetect_port()

        if not ssid:
            self._flash_status.setText("Please enter your Wi-Fi name first.")
            return
        if not port:
            self._flash_status.setText("Could not find your ESP32. Check the USB cable.")
            return

        import sys
        from pathlib import Path
        if getattr(sys, "frozen", False):
            base = sys._MEIPASS
        else:
            base = str(Path(__file__).parent.parent)
        base_fw = Path(base) / "firmware" / "espy_base.bin"

        if not base_fw.exists():
            self._flash_status.setText("Base firmware not found. Reinstall Espy.")
            return

        self._flash_bar.show()
        self._next_btn.setEnabled(False)
        self._next_btn.setText("Setting up...")

        self._usb_worker = UsbFlashWorker(port, str(base_fw), name, ssid, password)
        self._usb_worker.progress.connect(self._on_flash_progress)
        self._usb_worker.finished.connect(self._on_flash_done)
        self._usb_worker.failed.connect(self._on_flash_failed)
        self._usb_worker.start()

    def _on_flash_progress(self, pct: int, msg: str):
        self._flash_bar.set_value(pct)
        self._flash_status.setText(msg)

    def _on_flash_done(self):
        self._flash_bar.set_value(100)
        self._setup_check = AnimatedCheckmark()
        self._setup_check.setFixedSize(120, 120)
        self._content_layout.insertWidget(2, self._setup_check)
        QTimer.singleShot(200, self._setup_check.start_animate)

        mascot = BouncyMascot()
        mascot.set_mood("excited", 80)
        mascot.setFixedSize(80, 96)
        mascot.start_bounce()
        self._content_layout.insertWidget(1, mascot)

        self._flash_title.setText("All done! 🎉")
        self._flash_status.setText(
            "Unplug the USB cable. Your ESP32 will appear in the device list shortly."
        )
        self._flash_status.setStyleSheet(f"color: {C['success']}; font-size: {EASY_MODE_BODY_FONT}px;")
        self._next_btn.setText("Finish")
        self._next_btn.setEnabled(True)
        try:
            self._next_btn.clicked.disconnect()
        except TypeError:
            pass
        self._next_btn.clicked.connect(self._finish)

    def _on_flash_failed(self, msg: str):
        self._flash_title.setText("Something went wrong")
        self._flash_status.setText(f"✗ {msg}")
        self._flash_status.setStyleSheet(f"color: {C['error']}; font-size: {EASY_MODE_BODY_FONT}px;")
        self._next_btn.setText("Try again")
        self._next_btn.setEnabled(True)
        try:
            self._next_btn.clicked.disconnect()
        except TypeError:
            pass
        self._next_btn.clicked.connect(lambda: self._render_step(3))

    def _go_back(self):
        if self._current_step > 0:
            self._render_step(self._current_step - 1)

    def _go_next(self):
        if self._current_step < len(self._steps) - 1:
            self._render_step(self._current_step + 1)

    def _finish(self):
        self.finished.emit()


# ══ ui/easy_overlay.py ═══════════════════════════════════════

T = EASY_MODE_TITLE_FONT
B = EASY_MODE_BODY_FONT
M = EASY_MODE_MIN_FONT


class EasyOverlay(QWidget):
    switch_to_advanced = pyqtSignal()
    file_selected = pyqtSignal(str)
    start_setup = pyqtSignal()
    plug_connected = pyqtSignal()
    mode_chosen = pyqtSignal(str)
    device_selected = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self._devices: list[Device] = []
        self._selected_device: Device = None
        self._pending_cfg: InoConfig = None
        self._pending_path: str = ""
        self._usb_port: str = ""
        self._selected_board: str = ""
        self._is_onboarding = not FIRST_RUN_FILE.exists()
        self._build_ui()

    def _make_top_bar(self) -> QWidget:
        top = QWidget()
        tl = QHBoxLayout(top)
        tl.setContentsMargins(0, 0, 0, 0)

        self._back_btn = QPushButton("← Back")
        self._back_btn.setObjectName("ghost")
        self._back_btn.clicked.connect(self._go_back)
        self._back_btn.setVisible(False)
        self._back_btn.setToolTip("Go to the previous page")
        tl.addWidget(self._back_btn)

        # Mascot logo (replaces ⚡ emoji)
        self._logo_mascot = BouncyMascot()
        self._logo_mascot.set_mood("idle", 28)
        self._logo_mascot.setFixedSize(28, 34)
        tl.addWidget(self._logo_mascot)

        logo = QLabel("Espy")
        logo.setStyleSheet(f"font-size: 22px; font-weight: 800; color: {C['accent']};")
        tl.addWidget(logo)
        tl.addStretch()

        self._status_label = QLabel("")
        self._status_label.setStyleSheet(f"color: {C['text_muted']}; font-size: 15px;")
        tl.addWidget(self._status_label)

        advanced_btn = QPushButton("Advanced")
        advanced_btn.setObjectName("ghost")
        advanced_btn.clicked.connect(self.switch_to_advanced)
        advanced_btn.setToolTip("Switch to Advanced mode with more controls")
        tl.addWidget(advanced_btn)

        return top

    def _build_ui(self):
        self.setStyleSheet(f"background: {C['bg']};")
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(30, 16, 30, 20)
        main_layout.setSpacing(8)

        self._top_bar = self._make_top_bar()
        main_layout.addWidget(self._top_bar)

        self._stack = FadeStack()
        self._build_onboarding_pages()       # 0
        self._stack.addWidget(self._make_mode_choice_page())     # 3
        self._stack.addWidget(self._make_home_page())            # 4
        self._stack.addWidget(self._make_no_device_page())       # 5
        self._stack.addWidget(self._make_setup_page())           # 6
        self._stack.addWidget(self._make_plug_wait_page())       # 7
        self._stack.addWidget(self._make_wifi_page())            # 8
        self._stack.addWidget(self._make_success_page())         # 9
        self._stack.addWidget(self._make_config_page())          # 10
        self._stack.addWidget(self._make_admin_page())           # 11
        self._stack.addWidget(self._make_board_page())           # 12
        self._stack.addWidget(self._make_flash_progress_page())  # 13
        main_layout.addWidget(self._stack, 1)

        if self._is_onboarding:
            self._stack.setCurrentIndex(self._page_index("onboard"))
        else:
            self._stack.setCurrentIndex(self._page_index("home"))

    def _page_index(self, name: str) -> int:
        pages = {
            "onboard": 0,
            "mode_choice": 1,
            "home": 2, "no_device": 3,
            "setup": 4, "plug_wait": 5, "wifi": 6,
            "success": 7, "config": 8, "admin": 9,
            "board": 10, "flash_progress": 11,
        }
        return pages.get(name, 2)

    def set_mascot_mood(self, mood: str):
        if hasattr(self, "_home_mascot"):
            self._home_mascot.set_mood(mood)

    # ── Onboarding ─────────────────────────────────────────

    def _build_onboarding_pages(self):
        from ui.illustrations import onboarding_flow_svg

        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setSpacing(14)

        mascot = BouncyMascot()
        mascot.set_mood("happy", 48)
        mascot.setFixedSize(48, 60)
        mascot.start_bounce()
        layout.addWidget(mascot, alignment=Qt.AlignmentFlag.AlignCenter)

        title = QLabel("How Espy works")
        title.setStyleSheet(f"font-size: {T}px; font-weight: 700; color: {C['text']};")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        sub = QLabel("No cables. No technical stuff. Just drop and flash.")
        sub.setAlignment(Qt.AlignmentFlag.AlignCenter)
        sub.setStyleSheet(f"color: {C['text_muted']}; font-size: {B - 1}px;")
        layout.addWidget(sub)

        # Flow diagram
        flow_lbl = QLabel()
        pm = QPixmap()
        svg = onboarding_flow_svg(320, 340)
        pm.loadFromData(svg.encode())
        flow_lbl.setPixmap(pm)
        flow_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(flow_lbl, stretch=1)

        # Single page indicator (1/1)
        dot = QLabel("●")
        dot.setStyleSheet(f"font-size: 18px; color: {C['accent']};")
        dot.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(dot)

        btn = QPushButton("Let's go! →")
        btn.setObjectName("primary")
        btn.clicked.connect(lambda: self._stack.fade_to(self._page_index("mode_choice")))
        btn.setToolTip("Set up your ESP32")
        layout.addWidget(btn, alignment=Qt.AlignmentFlag.AlignCenter)

        skip = QPushButton("Skip for now")
        skip.setObjectName("ghost")
        skip.clicked.connect(self._finish_onboarding)
        skip.setToolTip("You can always set this up later")
        layout.addWidget(skip, alignment=Qt.AlignmentFlag.AlignCenter)

        self._stack.addWidget(page)

    def _finish_onboarding(self):
        FIRST_RUN_FILE.parent.mkdir(parents=True, exist_ok=True)
        FIRST_RUN_FILE.write_text("done")
        self._is_onboarding = False
        self._update_home_page()
        self._stack.fade_to(self._page_index("home"))

    def _finish_onboarding_to_setup(self):
        self._finish_onboarding()
        self._stack.fade_to(self._page_index("setup"))

    # ── Mode choice page ────────────────────────────────────

    def _make_mode_choice_page(self) -> QWidget:
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setSpacing(20)

        mascot = BouncyMascot()
        mascot.set_mood("excited", 80)
        mascot.setFixedSize(80, 96)
        mascot.start_bounce()
        layout.addWidget(mascot, alignment=Qt.AlignmentFlag.AlignCenter)

        title = QLabel("How do you want to use Espy?")
        title.setStyleSheet(f"font-size: {T}px; font-weight: 700; color: {C['text']};")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        cards_row = QHBoxLayout()
        cards_row.setSpacing(20)
        cards_row.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Simple mode card
        simple_card = QFrame()
        simple_card.setObjectName("card")
        simple_card.setCursor(Qt.CursorShape.PointingHandCursor)
        simple_card.setFixedSize(260, 210)
        sc = QVBoxLayout(simple_card)
        sc.setAlignment(Qt.AlignmentFlag.AlignCenter)
        sc.setSpacing(10)
        sc.setContentsMargins(18, 18, 18, 18)

        simple_icon = QLabel("✨")
        simple_icon.setStyleSheet("font-size: 36px;")
        simple_icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        sc.addWidget(simple_icon)

        simple_title = QLabel("Simple")
        simple_title.setStyleSheet(f"font-size: 22px; font-weight: 800; color: {C['text']};")
        simple_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        sc.addWidget(simple_title)

        simple_desc = QLabel("Drag, drop, done.\nNo technical stuff.\nJust works.")
        simple_desc.setAlignment(Qt.AlignmentFlag.AlignCenter)
        simple_desc.setStyleSheet(f"font-size: 15px; color: {C['text_muted']}; line-height: 1.4;")
        sc.addWidget(simple_desc)

        simple_btn = QPushButton("Choose Simple")
        simple_btn.setObjectName("primary")
        simple_btn.clicked.connect(lambda: self._choose_mode("simple"))
        sc.addWidget(simple_btn, alignment=Qt.AlignmentFlag.AlignCenter)

        # Advanced mode card
        adv_card = QFrame()
        adv_card.setObjectName("card")
        adv_card.setCursor(Qt.CursorShape.PointingHandCursor)
        adv_card.setFixedSize(260, 210)
        ac = QVBoxLayout(adv_card)
        ac.setAlignment(Qt.AlignmentFlag.AlignCenter)
        ac.setSpacing(10)
        ac.setContentsMargins(18, 18, 18, 18)

        adv_icon = QLabel("⚙️")
        adv_icon.setStyleSheet("font-size: 36px;")
        adv_icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        ac.addWidget(adv_icon)

        adv_title = QLabel("Advanced")
        adv_title.setStyleSheet(f"font-size: 22px; font-weight: 800; color: {C['text']};")
        adv_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        ac.addWidget(adv_title)

        adv_desc = QLabel("Full control over\npartitions, board config,\nOTA settings, and more.")
        adv_desc.setAlignment(Qt.AlignmentFlag.AlignCenter)
        adv_desc.setStyleSheet(f"font-size: 15px; color: {C['text_muted']}; line-height: 1.4;")
        ac.addWidget(adv_desc)

        adv_btn = QPushButton("Choose Advanced")
        adv_btn.setObjectName("secondary")
        adv_btn.clicked.connect(lambda: self._choose_mode("advanced"))
        ac.addWidget(adv_btn, alignment=Qt.AlignmentFlag.AlignCenter)

        cards_row.addWidget(simple_card)
        cards_row.addWidget(adv_card)
        layout.addLayout(cards_row)

        skip_btn = QPushButton("Skip for now — go to app")
        skip_btn.setObjectName("ghost")
        skip_btn.clicked.connect(self._finish_onboarding)
        skip_btn.setToolTip("You can change this later in settings")
        layout.addWidget(skip_btn, alignment=Qt.AlignmentFlag.AlignCenter)

        return page

    def _choose_mode(self, mode: str):
        MODE_PREF_FILE.parent.mkdir(parents=True, exist_ok=True)
        MODE_PREF_FILE.write_text(mode)
        self._finish_onboarding()
        if mode == "advanced":
            self._onboarding_chose_advanced = True
            QTimer.singleShot(400, self.switch_to_advanced.emit)

    # ── Dynamic home page ───────────────────────────────────

    def _make_home_page(self) -> QWidget:
        page = QWidget()
        self._home_layout = QVBoxLayout(page)
        self._home_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._home_layout.setSpacing(16)

        self._home_mascot = BouncyMascot()
        self._home_mascot.setFixedSize(160, 180)
        self._home_mascot.set_mood("idle")
        self._home_mascot.set_bounce_style("idle")
        self._home_mascot.start_bounce()
        self._home_layout.addWidget(self._home_mascot, alignment=Qt.AlignmentFlag.AlignCenter)

        self._home_arrow = AnimatedArrow("down")
        self._home_arrow.setFixedSize(40, 40)
        self._home_arrow.hide()
        self._home_layout.addWidget(self._home_arrow, alignment=Qt.AlignmentFlag.AlignCenter)

        self._home_title = QLabel()
        self._home_title.setStyleSheet(f"font-size: {T}px; font-weight: 700; color: {C['text']};")
        self._home_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._home_layout.addWidget(self._home_title)

        self._home_sub = QLabel()
        self._home_sub.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._home_sub.setWordWrap(True)
        self._home_sub.setStyleSheet(f"color: {C['text_muted']}; font-size: {B}px;")
        self._home_layout.addWidget(self._home_sub)

        self._home_dev_picker = QPushButton("Choose device...")
        self._home_dev_picker.setObjectName("secondary")
        self._home_dev_picker.setFixedWidth(280)
        self._home_dev_picker.clicked.connect(self._cycle_device)
        self._home_dev_picker.hide()
        self._home_dev_picker.setToolTip("Select which ESP32 to flash")
        self._home_layout.addWidget(self._home_dev_picker, alignment=Qt.AlignmentFlag.AlignCenter)

        self._home_drop = DropZone()
        self._home_drop.file_dropped.connect(self._on_file)
        self._home_drop.file_chosen.connect(self._on_file)
        self._home_drop.hide()
        self._home_layout.addWidget(self._home_drop, stretch=1)

        self._home_btn = QPushButton()
        self._home_btn.setObjectName("primary")
        self._home_btn.clicked.connect(self._on_home_btn)
        self._home_btn.setToolTip("Plug in your ESP32 via USB to get started")
        self._home_layout.addWidget(self._home_btn, alignment=Qt.AlignmentFlag.AlignCenter)

        self._update_home_page()
        return page

    def _on_home_btn(self):
        self._stack.fade_to(self._page_index("setup"))

    def _update_home_page(self):
        count = len(self._devices)
        if count == 0:
            self._home_mascot.set_mood("sad", 160)
            self._home_mascot.set_bounce_style("sad")
            self._home_title.setText("No ESP32s yet!")
            self._home_sub.setText("Set up your first ESP32 to\nstart flashing over Wi-Fi.")
            self._home_dev_picker.hide()
            self._home_drop.hide()
            self._home_btn.setText("Set up my ESP32 →")
            self._home_btn.show()
            self._home_arrow.show()
        elif count == 1:
            self._home_mascot.set_mood("happy", 160)
            self._home_mascot.set_bounce_style("happy")
            dev = self._devices[0]
            self._selected_device = dev
            self._home_title.setText(f"{dev.friendly_label} is ready!")
            self._home_sub.setText("Drop your .ino file to flash it.")
            self._home_dev_picker.hide()
            self._home_drop.show()
            self._home_btn.hide()
            self._home_arrow.hide()
            self.device_selected.emit(dev.name)
        else:
            self._home_mascot.set_mood("happy", 160)
            self._home_mascot.set_bounce_style("happy")
            self._home_title.setText(f"{count} ESP32s found!")
            self._home_sub.setText("Pick a device, then drop your code.")
            self._home_dev_picker.show()
            self._update_device_picker()
            self._home_drop.show()
            self._home_btn.hide()
            self._home_arrow.hide()
            if self._selected_device:
                self.device_selected.emit(self._selected_device.name)

    # ── Setup flow pages ────────────────────────────────────

    def _make_setup_page(self) -> QWidget:
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setSpacing(16)

        # Mascot + small USB cable side by side
        vis_row = QHBoxLayout()
        vis_row.setAlignment(Qt.AlignmentFlag.AlignCenter)
        vis_row.setSpacing(12)

        mascot = BouncyMascot()
        mascot.set_mood("happy", 80)
        mascot.setFixedSize(80, 96)
        mascot.start_bounce()
        vis_row.addWidget(mascot)

        from ui.illustrations import usb_illustration
        usb_lbl = QLabel()
        pm = QPixmap()
        pm.loadFromData(usb_illustration(100).encode())
        usb_lbl.setPixmap(pm)
        usb_lbl.setFixedSize(100, 80)
        vis_row.addWidget(usb_lbl)

        layout.addLayout(vis_row)

        title = QLabel("Plug in your ESP32")
        title.setStyleSheet(f"font-size: {T}px; font-weight: 700; color: {C['text']};")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        sub = QLabel(
            "Connect the USB cable between your computer\n"
            "and the ESP32 board. I'll handle the rest."
        )
        sub.setAlignment(Qt.AlignmentFlag.AlignCenter)
        sub.setStyleSheet(f"color: {C['text_muted']}; font-size: {B}px;")
        layout.addWidget(sub)

        big_btn = QPushButton("I plugged it in! →")
        big_btn.setObjectName("primary")
        big_btn.clicked.connect(self._on_plug_button)
        big_btn.setToolTip("Make sure the USB cable is connected to your ESP32 and this computer")
        layout.addWidget(big_btn, alignment=Qt.AlignmentFlag.AlignCenter)

        skip_btn = QPushButton("Skip — take me to the app")
        skip_btn.setObjectName("ghost")
        skip_btn.clicked.connect(self._skip_setup)
        skip_btn.setToolTip("You can always set this up later")
        layout.addWidget(skip_btn, alignment=Qt.AlignmentFlag.AlignCenter)

        return page

    def _make_plug_wait_page(self) -> QWidget:
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setSpacing(18)

        self._plug_dots = LoadingDots()
        layout.addWidget(self._plug_dots, alignment=Qt.AlignmentFlag.AlignCenter)

        title = QLabel("Looking for your ESP32...")
        title.setStyleSheet(f"font-size: {T - 2}px; font-weight: 700; color: {C['text']};")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        self._plug_status = QLabel("Check that the USB cable is connected.")
        self._plug_status.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._plug_status.setStyleSheet(f"color: {C['text_muted']}; font-size: {B}px;")
        layout.addWidget(self._plug_status)

        retry_btn = QPushButton("Try again")
        retry_btn.setObjectName("secondary")
        retry_btn.clicked.connect(self._retry_usb_detect)
        retry_btn.setToolTip("Check your cable and try again")
        layout.addWidget(retry_btn, alignment=Qt.AlignmentFlag.AlignCenter)

        back_btn = QPushButton("← Back")
        back_btn.setObjectName("ghost")
        back_btn.clicked.connect(lambda: self._stack.fade_to(self._page_index("setup")))
        back_btn.setToolTip("Go back to the setup page")
        layout.addWidget(back_btn, alignment=Qt.AlignmentFlag.AlignCenter)

        return page

    def _make_wifi_page(self) -> QWidget:
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setSpacing(16)

        from ui.animations import PulsingWifi
        pw = PulsingWifi()
        pw.setFixedSize(100, 80)
        layout.addWidget(pw, alignment=Qt.AlignmentFlag.AlignCenter)

        mascot = BouncyMascot()
        mascot.set_mood("searching", 50)
        mascot.setFixedSize(50, 62)
        mascot.start_bounce()
        layout.addWidget(mascot, alignment=Qt.AlignmentFlag.AlignCenter)

        title = QLabel("Connect to Wi-Fi")
        title.setStyleSheet(f"font-size: {T}px; font-weight: 700; color: {C['text']};")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        sub = QLabel("Your ESP32 will use this to receive updates wirelessly.")
        sub.setAlignment(Qt.AlignmentFlag.AlignCenter)
        sub.setStyleSheet(f"color: {C['text_muted']}; font-size: {B - 1}px;")
        layout.addWidget(sub)

        self._setup_ssid = QLineEdit()
        self._setup_ssid.setPlaceholderText("Your Wi-Fi name (e.g. MyHomeNetwork)")
        self._setup_ssid.setMinimumWidth(320)
        self._setup_ssid.setToolTip("The name of your home Wi-Fi network")
        layout.addWidget(self._setup_ssid)

        self._setup_password = QLineEdit()
        self._setup_password.setEchoMode(QLineEdit.EchoMode.Password)
        self._setup_password.setPlaceholderText("Wi-Fi password")
        self._setup_password.setMinimumWidth(320)
        self._setup_password.setToolTip("Saved on your ESP32 — not your computer")
        layout.addWidget(self._setup_password)

        self._wifi_error = QLabel("")
        self._wifi_error.setStyleSheet(f"color: {C['error']}; font-size: 15px;")
        self._wifi_error.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._wifi_error.hide()
        layout.addWidget(self._wifi_error)

        btn = QPushButton("Save & Continue →")
        btn.setObjectName("primary")
        btn.clicked.connect(self._on_wifi_save)
        btn.setToolTip("Save Wi-Fi details to your ESP32")
        layout.addWidget(btn, alignment=Qt.AlignmentFlag.AlignCenter)

        back_btn = QPushButton("← Back")
        back_btn.setObjectName("ghost")
        back_btn.clicked.connect(lambda: self._stack.fade_to(self._page_index("setup")))
        back_btn.setToolTip("Go back to the previous step")
        layout.addWidget(back_btn, alignment=Qt.AlignmentFlag.AlignCenter)

        return page

    def _make_no_device_page(self) -> QWidget:
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setSpacing(18)

        mascot = BouncyMascot()
        mascot.set_mood("surprise", 120)
        mascot.setFixedSize(120, 140)
        mascot.start_bounce()
        layout.addWidget(mascot, alignment=Qt.AlignmentFlag.AlignCenter)

        title = QLabel("I can't find your ESP32")
        title.setStyleSheet(f"font-size: {T}px; font-weight: 700; color: {C['text']};")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        sub = QLabel(
            "Make sure it's powered on and on the same Wi‑Fi.\n"
            "For a new device, set it up with USB first."
        )
        sub.setAlignment(Qt.AlignmentFlag.AlignCenter)
        sub.setStyleSheet(f"color: {C['text_muted']}; font-size: {B}px;")
        layout.addWidget(sub)

        btn = QPushButton("Set up with USB →")
        btn.setObjectName("primary")
        btn.clicked.connect(lambda: self._stack.fade_to(self._page_index("setup")))
        btn.setToolTip("Plug your ESP32 in via USB to set it up")
        layout.addWidget(btn, alignment=Qt.AlignmentFlag.AlignCenter)

        return page

    def _make_success_page(self) -> QWidget:
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setSpacing(18)

        self._success_check = AnimatedCheckmark()
        self._success_check.setFixedSize(120, 120)
        layout.addWidget(self._success_check, alignment=Qt.AlignmentFlag.AlignCenter)

        self._success_title = QLabel("It works! 🎉")
        self._success_title.setStyleSheet(f"font-size: {T}px; font-weight: 700; color: {C['success']};")
        self._success_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self._success_title)

        self._success_sub = QLabel("")
        self._success_sub.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._success_sub.setStyleSheet(f"color: {C['text_muted']}; font-size: {B}px;")
        layout.addWidget(self._success_sub)

        btn = QPushButton("Flash another →")
        btn.setObjectName("primary")
        btn.clicked.connect(lambda: self._back_to_home())
        btn.setToolTip("Go back to flash another device")
        layout.addWidget(btn, alignment=Qt.AlignmentFlag.AlignCenter)

        return page

    def _make_config_page(self) -> QWidget:
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setSpacing(14)
        layout.setContentsMargins(40, 16, 40, 16)

        mascot = BouncyMascot()
        mascot.set_mood("wink", 100)
        mascot.setFixedSize(100, 120)
        mascot.start_bounce()
        layout.addWidget(mascot, alignment=Qt.AlignmentFlag.AlignCenter)

        title = QLabel("I read your code!")
        title.setStyleSheet(f"font-size: {T - 2}px; font-weight: 700; color: {C['text']};")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        card = QFrame()
        card.setObjectName("card")
        cl = QVBoxLayout(card)
        cl.setSpacing(8)
        cl.setContentsMargins(20, 16, 20, 16)
        self._config_target_lbl = QLabel("")
        self._config_target_lbl.setStyleSheet(f"color: {C['accent']}; font-size: 17px; font-weight: 700;")
        cl.addWidget(self._config_target_lbl)
        self._config_name_lbl = QLabel("")
        self._config_board_lbl = QLabel("")
        self._config_partition_lbl = QLabel("")
        self._config_wifi_lbl = QLabel("")
        self._config_libs_lbl = QLabel("")
        for lbl in [self._config_name_lbl, self._config_board_lbl,
                     self._config_partition_lbl, self._config_wifi_lbl,
                     self._config_libs_lbl]:
            lbl.setStyleSheet(f"color: {C['text']}; font-size: 17px;")
            cl.addWidget(lbl)
        self._config_partition_lbl.hide()
        self._config_warning_lbl = QLabel("")
        self._config_warning_lbl.setStyleSheet(f"color: {C['warning']}; font-size: 15px;")
        self._config_warning_lbl.setWordWrap(True)
        self._config_warning_lbl.hide()
        cl.addWidget(self._config_warning_lbl)

        part_edit_btn = QPushButton("Edit partition layout")
        part_edit_btn.setObjectName("ghost")
        part_edit_btn.setStyleSheet(
            f"QPushButton{{ font-size: 14px; color: {C['accent']}; }}"
        )
        part_edit_btn.clicked.connect(self._edit_partitions)
        part_edit_btn.setToolTip("Change flash size, partition scheme, or custom partition table")
        cl.addWidget(part_edit_btn)

        layout.addWidget(card)

        btn = QPushButton("Looks good! Flash it →")
        btn.setObjectName("primary")
        btn.clicked.connect(self._confirm_config)
        btn.setToolTip("Start compiling and uploading to your ESP32")
        layout.addWidget(btn, alignment=Qt.AlignmentFlag.AlignCenter)

        back_btn = QPushButton("← Choose a different file")
        back_btn.setObjectName("ghost")
        back_btn.clicked.connect(lambda: self._back_to_home())
        back_btn.setToolTip("Pick a different .ino file")
        layout.addWidget(back_btn, alignment=Qt.AlignmentFlag.AlignCenter)

        return page

    def _make_admin_page(self) -> QWidget:
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setSpacing(18)

        mascot = BouncyMascot()
        mascot.set_mood("idle", 80)
        mascot.setFixedSize(80, 96)
        mascot.start_bounce()
        layout.addWidget(mascot, alignment=Qt.AlignmentFlag.AlignCenter)

        title = QLabel("Admin")
        title.setStyleSheet(f"font-size: {T}px; font-weight: 700; color: {C['text']};")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        sub = QLabel("Reset or reconfigure your ESP32s.")
        sub.setAlignment(Qt.AlignmentFlag.AlignCenter)
        sub.setStyleSheet(f"color: {C['text_muted']}; font-size: {B}px;")
        layout.addWidget(sub)

        btn = QPushButton("Set up a new ESP32")
        btn.setObjectName("primary")
        btn.clicked.connect(lambda: self._stack.fade_to(self._page_index("setup")))
        btn.setToolTip("Plug in a new ESP32 via USB to get started")
        layout.addWidget(btn, alignment=Qt.AlignmentFlag.AlignCenter)

        part_btn = QPushButton("Partition settings")
        part_btn.setObjectName("secondary")
        part_btn.clicked.connect(self._edit_partitions_default)
        part_btn.setToolTip("Change flash size, partition scheme, or edit partition table")
        layout.addWidget(part_btn, alignment=Qt.AlignmentFlag.AlignCenter)

        back_btn = QPushButton("← Back to home")
        back_btn.setObjectName("ghost")
        back_btn.clicked.connect(lambda: self._back_to_home())
        back_btn.setToolTip("Go back to the home page")
        layout.addWidget(back_btn, alignment=Qt.AlignmentFlag.AlignCenter)

        return page

    def _make_board_page(self) -> QWidget:
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setSpacing(14)

        mascot = BouncyMascot()
        mascot.set_mood("happy", 60)
        mascot.setFixedSize(60, 72)
        mascot.start_bounce()
        layout.addWidget(mascot, alignment=Qt.AlignmentFlag.AlignCenter)

        title = QLabel("Which ESP32 do you have?")
        title.setStyleSheet(f"font-size: {T}px; font-weight: 700; color: {C['text']};")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        sub = QLabel(
            "Pick the board that matches your hardware.\n"
            "Check the label on the metal chip on your board."
        )
        sub.setAlignment(Qt.AlignmentFlag.AlignCenter)
        sub.setStyleSheet(f"color: {C['text_muted']}; font-size: {B - 1}px;")
        layout.addWidget(sub)

        from ui.board_picker import BoardPicker
        self._board_picker = BoardPicker()
        self._board_picker.board_selected.connect(self._on_board_selected)
        layout.addWidget(self._board_picker, stretch=1)

        self._board_next_btn = QPushButton("Next →")
        self._board_next_btn.setObjectName("primary")
        self._board_next_btn.setEnabled(False)
        self._board_next_btn.clicked.connect(self._after_board_chosen)
        self._board_next_btn.setToolTip("Select a board first")
        layout.addWidget(self._board_next_btn, alignment=Qt.AlignmentFlag.AlignCenter)

        back_btn = QPushButton("← Back")
        back_btn.setObjectName("ghost")
        back_btn.clicked.connect(lambda: self._stack.fade_to(self._page_index("plug_wait")))
        layout.addWidget(back_btn, alignment=Qt.AlignmentFlag.AlignCenter)

        return page

    def _on_board_selected(self, name: str):
        self._selected_board = name
        self._board_next_btn.setEnabled(True)
        self._board_next_btn.setText(f"Next — {name} →")

    def _after_board_chosen(self):
        self._stack.fade_to(self._page_index("wifi"))

    def _make_flash_progress_page(self) -> QWidget:
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setSpacing(18)

        self._flash_progress = QProgressBar()
        self._flash_progress.setMinimum(0)
        self._flash_progress.setMaximum(100)
        self._flash_progress.setValue(0)
        self._flash_progress.setMinimumWidth(300)
        self._flash_progress.setTextVisible(True)
        layout.addWidget(self._flash_progress, alignment=Qt.AlignmentFlag.AlignCenter)

        self._flash_status = QLabel("Preparing to flash...")
        self._flash_status.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._flash_status.setStyleSheet(f"color: {C['text_muted']}; font-size: {B}px;")
        layout.addWidget(self._flash_status)

        return page

    # ── Public API ──────────────────────────────────────────

    def set_devices(self, devices: list[Device]):
        self._devices = devices
        if devices and not self._selected_device:
            self._selected_device = devices[0]
            self._update_device_picker()
        self._update_home_page()

    def set_status(self, msg: str):
        self._status_label.setText(msg)

    def show_no_device(self):
        self.set_mascot_mood("surprise")
        self._stack.fade_to(self._page_index("no_device"))

    def show_success(self, device_name: str):
        self.set_mascot_mood("excited")
        self._success_title.setText("It works! 🎉")
        self._success_sub.setText(f"{device_name} is running your code.")
        self._stack.fade_to(self._page_index("success"))
        QTimer.singleShot(200, self._success_check.start_animate)

    def show_config_review(self, cfg: InoConfig, path: str):
        self.set_mascot_mood("wink")
        self._pending_cfg = cfg
        self._pending_path = path
        target = self._selected_device.friendly_label if self._selected_device else ""
        self._config_target_lbl.setText(f"🎯  Target: {target}" if target else "")
        self._config_name_lbl.setText(f"  Device: {cfg.device_name or 'My ESP32'}")
        self._config_board_lbl.setText(f"  Board: {cfg.board}")
        flash = cfg.flash_size_override or cfg.flash_size
        scheme = cfg.partition_scheme.replace("_", " ").title()
        if cfg.partition_csv_override:
            pt = f"  Partitions: {flash} · {scheme} (custom CSV)"
        else:
            pt = f"  Partitions: {flash} · {scheme}"
        self._config_partition_lbl.setText(pt)
        self._config_partition_lbl.show()
        self._config_wifi_lbl.setText(f"  Wi‑Fi: {cfg.wifi_ssid or '(from device)'}")
        libs_text = "  " + ", ".join(l.name for l in cfg.libraries) if cfg.libraries else ""
        self._config_libs_lbl.setText(libs_text)
        if cfg.has_ota_conflict:
            self._config_warning_lbl.setText("I'll remove old OTA code for you.")
            self._config_warning_lbl.show()
        else:
            self._config_warning_lbl.hide()
        self._stack.fade_to(self._page_index("config"))

    def show_setup(self):
        self._stack.fade_to(self._page_index("setup"))

    # ── Internal: setup flow ────────────────────────────────

    def _on_plug_button(self):
        self.set_mascot_mood("searching")
        self._stack.fade_to(self._page_index("plug_wait"))
        self._plug_dots.start()
        self._plug_status.setText("Check that the USB cable is connected.")
        QTimer.singleShot(1500, self._do_usb_detect)

    def _do_usb_detect(self):
        from discovery.usb import usb_probe
        ports = usb_probe()
        if ports:
            self._plug_dots.stop()
            self._plug_status.setText(f"✓ Found it! ({ports[0]['port']})")
            self._plug_status.setStyleSheet(f"color: {C['success']}; font-size: {B}px;")
            self._usb_port = ports[0]['port']
            self.set_mascot_mood("happy")
            QTimer.singleShot(800, lambda: self._stack.fade_to(self._page_index("board")))
        else:
            self._plug_dots.stop()
            self._plug_status.setText("✗ Could not find your ESP32. Try a different USB cable.")
            self._plug_status.setStyleSheet(f"color: {C['error']}; font-size: {B}px;")

    def _retry_usb_detect(self):
        self._plug_dots.start()
        self._plug_status.setText("Check that the USB cable is connected.")
        self._plug_status.setStyleSheet(f"color: {C['text_muted']}; font-size: {B}px;")
        QTimer.singleShot(1500, self._do_usb_detect)

    def _on_wifi_save(self):
        ssid = self._setup_ssid.text().strip()
        if not ssid:
            self._wifi_error.setText("Please enter your Wi-Fi network name.")
            self._wifi_error.show()
            return
        password = self._setup_password.text().strip()
        self._wifi_error.hide()

        self._stack.fade_to(self._page_index("flash_progress"))
        self._flash_status.setText("Flashing your ESP32...")
        self._flash_progress.setValue(10)
        self._start_usb_flash(ssid, password)

    def _start_usb_flash(self, ssid: str, password: str):
        from workers.usb_flash import UsbFlashWorker
        from pathlib import Path

        if getattr(sys, "frozen", False):
            base = sys._MEIPASS
        else:
            base = str(Path(__file__).parent.parent)
        base_fw = Path(base) / "firmware" / "espy_base.bin"
        if not base_fw.exists():
            self._flash_status.setText("Base firmware not found — reinstall Espy.")
            return

        if not self._usb_port:
            self._flash_status.setText("No USB port found — try plugging in again.")
            return

        name = "My ESP32"
        self._usb_worker = UsbFlashWorker(self._usb_port, str(base_fw),
                                          name, ssid, password,
                                          board=self._selected_board)
        self._usb_worker.progress.connect(self._on_flash_progress)
        self._usb_worker.finished.connect(self._on_flash_done)
        self._usb_worker.failed.connect(self._on_flash_failed)
        self._usb_worker.start()

    def _on_flash_progress(self, pct: int, msg: str):
        self._flash_progress.setValue(pct)
        self._flash_status.setText(msg)

    def _on_flash_done(self):
        self._confirming = False
        self._flash_progress.setValue(100)
        self._finish_onboarding_if_needed()
        self.show_success("Your ESP32")

    def _on_flash_failed(self, msg: str):
        self._confirming = False
        self._flash_status.setText(msg)
        self._flash_status.setStyleSheet(f"color: {C['error']}; font-size: {B}px;")

    # ── Partition editor (shared) ───────────────────────────

    def _confirm_config(self):
        if getattr(self, '_confirming', False):
            return
        if self._pending_path and self._pending_cfg:
            self._confirming = True
            self._pending_cfg.bin_size_bytes = 0
            self._config_confirmed = True
            self._flash_progress.setValue(0)
            self._flash_status.setText("Starting compilation...")
            self._stack.fade_to(self._page_index("flash_progress"))
            QTimer.singleShot(100, lambda: self.file_selected.emit(self._pending_path))

    def _edit_partitions(self):
        if self._pending_cfg is None:
            return
        from ui.partition_editor import PartitionEditor
        editor = PartitionEditor(self._pending_cfg, self)
        editor.applied.connect(self._on_partitions_edited)
        editor.exec()

    def _edit_partitions_default(self):
        cfg = InoConfig()
        from ui.partition_editor import PartitionEditor
        editor = PartitionEditor(cfg, self)
        editor.applied.connect(self._on_partitions_edited_default)
        editor.exec()

    def _on_partitions_edited_default(self, cfg: InoConfig):
        self._pending_cfg = cfg
        self._status_label.setText(f"Partitions: {cfg.partition_scheme.replace('_', ' ').title()} · {cfg.flash_size}")

    def _on_partitions_edited(self, cfg: InoConfig):
        self._pending_cfg = cfg
        if self._pending_path:
            self.show_config_review(cfg, self._pending_path)

    # ── Internal: file handling ─────────────────────────────

    def _on_file(self, path: str):
        self._pending_path = path
        self.set_mascot_mood("wink")
        self.file_selected.emit(path)

    def _update_device_picker(self):
        if self._selected_device:
            txt = self._selected_device.friendly_label
            self._home_dev_picker.setText(txt)
        elif self._devices:
            self._selected_device = self._devices[0]
            self._home_dev_picker.setText(self._selected_device.friendly_label)
        else:
            self._home_dev_picker.setText("No device")

    def _cycle_device(self):
        if not self._devices:
            self.show_no_device()
            return
        idx = 0
        for i, d in enumerate(self._devices):
            if d is self._selected_device:
                idx = (i + 1) % len(self._devices)
                break
        self._selected_device = self._devices[idx]
        self._update_device_picker()
        self._home_title.setText(f"{self._selected_device.friendly_label} is ready!")
        self._home_sub.setText("Drop your .ino file to flash it.")
        self.device_selected.emit(self._selected_device.name)

    def _go_back(self):
        current = self._stack.currentIndex()
        if current > 0:
            self._stack.fade_to(current - 1)

    def _skip_setup(self):
        self._finish_onboarding_if_needed()
        self._back_to_home()
        self.set_mascot_mood("idle")
        self._status_label.setText("You can set up an ESP32 anytime from the button above.")

    def _finish_onboarding_if_needed(self):
        if self._is_onboarding:
            FIRST_RUN_FILE.parent.mkdir(parents=True, exist_ok=True)
            FIRST_RUN_FILE.write_text("done")
            self._is_onboarding = False

    def _back_to_home(self):
        self._update_home_page()
        self._stack.fade_to(self._page_index("home"))


# ══ ui/main_window.py ═══════════════════════════════════════

class MainWindow(QMainWindow):
    mode_changed = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.setWindowTitle(f"{APP_NAME} — Flash your ESP32 in one click")
        self.setMinimumSize(900, 700)
        self.resize(1024, 740)
        self.setStyleSheet(stylesheet())

        self._devices: dict[str, Device] = {}
        self._selected_device: Optional[Device] = None
        self._pending_bin: Optional[str] = None
        self._pending_cfg: Optional[InoConfig] = None
        self._compiler: Optional[CompilerWorker] = None
        self._ota: Optional[OtaWorker] = None
        self._batch_ino_path: str = ""
        self._batch_queue: list[Device] = []
        self._batch_index: int = 0

        self._easy_mode = True

        self._manual_board = "ESP32 Dev Module"
        self._build_ui()
        self._start_discovery()

    def _build_ui(self):
        root = QWidget()
        root_layout = QHBoxLayout(root)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)
        self.setCentralWidget(root)

        # Sidebar
        self._sidebar = self._make_sidebar()
        root_layout.addWidget(self._sidebar)

        # Divider
        div = QFrame()
        div.setFrameShape(QFrame.Shape.VLine)
        div.setStyleSheet(f"color: {C['border']};")
        root_layout.addWidget(div)

        # Main content
        self._stack = QStackedWidget()
        self._stack.addWidget(self._make_main_page())      # 0
        self._stack.addWidget(self._make_flash_page())     # 1
        self._serial_logger = SerialLogger()
        self._serial_logger.closed.connect(lambda: self._stack.setCurrentIndex(0))
        self._stack.addWidget(self._serial_logger)         # 2
        root_layout.addWidget(self._stack, 1)

        # Easy Mode overlay
        self._easy_overlay = EasyOverlay()
        self._easy_overlay.setVisible(False)
        self._easy_overlay.switch_to_advanced.connect(self._switch_to_advanced)
        self._easy_overlay.file_selected.connect(self._on_ino_received)
        self._easy_overlay.start_setup.connect(self._show_setup_wizard)
        self._easy_overlay.plug_connected.connect(self._on_plug_connected)
        self._easy_overlay.device_selected.connect(self._on_easy_device_selected)
        root_layout.addWidget(self._easy_overlay)

        if self._easy_mode:
            self._show_easy_mode()
            QTimer.singleShot(100, self._check_mode_pref)

    def _check_mode_pref(self):
        if MODE_PREF_FILE.exists():
            pref = MODE_PREF_FILE.read_text().strip()
            if pref == "advanced":
                self._switch_to_advanced()

    def _make_sidebar(self):
        sidebar = QWidget()
        sidebar.setObjectName("sidebar")
        sidebar.setFixedWidth(250)

        layout = QVBoxLayout(sidebar)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Logo area with mascot
        logo_area = QWidget()
        logo_area.setFixedHeight(70)
        logo_area.setStyleSheet(f"border-bottom: 1px solid {C['border']};")
        ll = QHBoxLayout(logo_area)
        ll.setContentsMargins(16, 0, 16, 0)

        logo_mascot = BouncyMascot()
        logo_mascot.set_mood("happy", 28)
        logo_mascot.setFixedSize(28, 34)
        ll.addWidget(logo_mascot)

        logo_txt = QLabel("Espy")
        logo_txt.setStyleSheet(
            f"font-size: 19px; font-weight: 800; color: {C['accent']};"
            f"background: transparent;"
        )
        ll.addWidget(logo_txt)
        layout.addWidget(logo_area)

        # Section header
        dev_header = QLabel("  MY DEVICES")
        dev_header.setObjectName("section_title")
        layout.addWidget(dev_header)

        # Device list
        self._device_list = QListWidget()
        self._device_list.setStyleSheet(
            f"QListWidget {{ background: transparent; border: none; }}"
            f"QListWidget::item:selected {{ background: {C['card']}; }}"
            f"QListWidget::item:hover {{ background: {C['card_hover']}; }}"
        )
        self._device_list.itemClicked.connect(self._on_device_selected)
        layout.addWidget(self._device_list, 1)

        # Batch flash bar
        self._batch_bar = QProgressBar()
        self._batch_bar.setMinimum(0)
        self._batch_bar.setMaximum(100)
        self._batch_bar.setTextVisible(True)
        self._batch_bar.hide()
        layout.addWidget(self._batch_bar)

        # Bottom buttons
        btn_area = QWidget()
        btn_area.setStyleSheet(f"border-top: 1px solid {C['border']};")
        bl = QVBoxLayout(btn_area)
        bl.setContentsMargins(12, 12, 12, 12)
        bl.setSpacing(8)

        self._batch_btn = QPushButton("Flash Selected (0)")
        self._batch_btn.setObjectName("primary")
        self._batch_btn.setEnabled(False)
        self._batch_btn.clicked.connect(self._start_batch_flash)
        self._batch_btn.setToolTip("Flash code to all selected devices (one at a time)")
        self._batch_btn.hide()
        bl.addWidget(self._batch_btn)

        self._serial_btn = QPushButton("Serial Monitor")
        self._serial_btn.setObjectName("secondary")
        self._serial_btn.clicked.connect(self._show_serial_logger)
        self._serial_btn.setToolTip("Open serial monitor (USB or Wi-Fi)")
        bl.addWidget(self._serial_btn)

        add_btn = QPushButton("+ Add device")
        add_btn.setObjectName("secondary")
        add_btn.clicked.connect(self._show_setup_wizard)
        add_btn.setToolTip("Set up a new ESP32 via USB")
        bl.addWidget(add_btn)

        # Mascot icon replaces 🌻
        mode_btn = QPushButton("  Easy Mode")
        mode_btn.setObjectName("ghost")
        mode_btn.setIcon(QIcon())
        mode_btn.clicked.connect(self._toggle_mode)
        mode_btn.setToolTip("Switch between Easy and Advanced modes")
        bl.addWidget(mode_btn)

        layout.addWidget(btn_area)
        return sidebar

    def _make_main_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(32, 28, 32, 28)
        layout.setSpacing(16)

        # ── Device status banner ─────────────────────────────
        self._status_banner = QFrame()
        self._status_banner.setObjectName("card")
        self._status_banner.setStyleSheet(
            f"QFrame#card {{ background: {C['card']}; border-color: {C['border']}; }}"
        )
        banner_layout = QHBoxLayout(self._status_banner)
        banner_layout.setContentsMargins(16, 12, 16, 12)
        banner_layout.setSpacing(10)

        self._status_dot = BreathingDot()
        self._status_dot.set_online(False)
        banner_layout.addWidget(self._status_dot)

        self._status_text = QLabel("Looking for devices on your network...")
        self._status_text.setStyleSheet(f"color: {C['text_muted']}; font-size: 15px; background: transparent;")
        banner_layout.addWidget(self._status_text, 1)

        self._setup_btn = QPushButton("Set up new ESP32 →")
        self._setup_btn.setObjectName("secondary")
        self._setup_btn.setFixedWidth(200)
        self._setup_btn.clicked.connect(self._show_setup_wizard)
        self._setup_btn.hide()
        banner_layout.addWidget(self._setup_btn)
        layout.addWidget(self._status_banner)

        # ── Partition info card ──────────────────────────────
        self._part_card = QFrame()
        self._part_card.setObjectName("card")
        part_layout = QHBoxLayout(self._part_card)
        part_layout.setContentsMargins(16, 10, 16, 10)
        part_layout.setSpacing(10)

        self._part_label = QLabel("")
        self._part_label.setStyleSheet(f"color: {C['text_muted']}; font-size: 13px; background: transparent;")
        part_layout.addWidget(self._part_label, 1)

        self._part_btn = QPushButton("Edit Partitions")
        self._part_btn.setObjectName("ghost")
        self._part_btn.setStyleSheet(
            f"QPushButton{{ font-size: 12px; padding: 3px 10px; background: {C['card']}; "
            f"border: 1px solid {C['border']}; border-radius: 6px; }}"
            f"QPushButton:hover{{ background: {C['card_hover']}; }}"
        )
        self._part_btn.clicked.connect(self._open_partition_settings)
        self._part_btn.setToolTip("Change flash size, partition scheme, or edit partition table")
        part_layout.addWidget(self._part_btn)
        layout.addWidget(self._part_card)

        # ── Header row ──────────────────────────────────────
        header = QHBoxLayout()
        title = QLabel("Drop your code here")
        title.setStyleSheet(f"font-size: 22px; font-weight: 700; color: {C['text']};")
        header.addWidget(title)
        header.addStretch()

        self._board_selector = QComboBox()
        self._board_selector.setFixedWidth(200)
        board_names = list(BOARDS.keys())
        self._board_selector.addItems(board_names)
        self._board_selector.setCurrentText("ESP32 Dev Module")
        self._board_selector.currentTextChanged.connect(self._on_board_changed)
        self._board_selector.setToolTip("Select your ESP32 board model")
        header.addWidget(QLabel("Board:"))
        header.addWidget(self._board_selector)

        self._device_selector = QComboBox()
        self._device_selector.setFixedWidth(180)
        self._device_selector.setPlaceholderText("Target device...")
        self._device_selector.currentTextChanged.connect(self._on_device_combo_changed)
        header.addWidget(self._device_selector)
        layout.addLayout(header)

        self._drop_zone = DropZone()
        self._drop_zone.file_dropped.connect(self._on_ino_received)
        self._drop_zone.file_chosen.connect(self._on_ino_received)
        self._drop_zone.set_enabled(False)
        layout.addWidget(self._drop_zone, 1)

        self._status_card = QFrame()
        self._status_card.setObjectName("card")
        self._status_card.hide()
        sc = QVBoxLayout(self._status_card)
        sc.setContentsMargins(20, 16, 20, 16)
        sc.setSpacing(10)

        self._status_label = QLabel("")
        self._status_label.setStyleSheet(f"color: {C['text_muted']}; font-size: 16px;")
        self._progress_bar = QProgressBar()
        self._progress_bar.setRange(0, 100)
        self._progress_bar.setValue(0)
        self._progress_bar.setFixedHeight(16)
        self._progress_bar.setTextVisible(False)

        sc.addWidget(self._status_label)
        sc.addWidget(self._progress_bar)
        layout.addWidget(self._status_card)

        tip = QLabel(
            "Tip: Add // DEVICE_NAME: Kitchen Light at the top of your sketch "
            "for automatic naming when using AI assistants."
        )
        tip.setWordWrap(True)
        tip.setStyleSheet(f"color: {C['text_faint']}; font-size: 15px; padding-top: 6px;")
        layout.addWidget(tip)

        return page

    def _make_flash_page(self):
        self._flash_scene = ProgressScene()
        self._flash_scene.save_binary_requested.connect(self._on_save_binary)
        self._flash_scene.flash_now_requested.connect(self._on_flash_now)
        return self._flash_scene

    def _start_discovery(self):
        self._discovery = DiscoveryEngine()
        self._discovery.found.connect(self._on_device_found)
        self._discovery.lost.connect(self._on_device_lost)
        self._discovery.phase_changed.connect(self._on_discovery_phase)
        self._discovery.start()

    def _on_device_found(self, name: str, ip: str, port: int):
        if name in self._devices:
            self._devices[name].ip = ip
            self._devices[name].last_seen = time.time()
        else:
            self._devices[name] = Device(name, ip, port)
        self._refresh_device_ui()
        self._update_device_status()
        self._easy_overlay.set_devices(list(self._devices.values()))
        self._easy_overlay.set_mascot_mood("happy")
        if self._pending_bin:
            self._flash_scene.set_flash_enabled(True)

    def _on_device_lost(self, name: str):
        if name in self._devices:
            del self._devices[name]
            self._refresh_device_ui()
        if self._selected_device and self._selected_device.name == name:
            self._selected_device = next(iter(self._devices.values())) if self._devices else None
        self._update_device_status()
        if not self._devices:
            self._easy_overlay.set_mascot_mood("sad")
        self._easy_overlay.set_devices(list(self._devices.values()))

    def _on_discovery_phase(self, msg: str):
        self._easy_overlay.set_status(msg)
        if not self._devices:
            self._status_text.setText(msg)

    def _update_partition_card(self):
        board = self._board_selector.currentText() if hasattr(self, '_board_selector') else "ESP32 Dev Module"
        info = BOARDS.get(board, {})
        flash = info.get("flash_size", "4MB")
        chip = info.get("chip", "ESP32")
        self._part_label.setText(
            f"Board: {board} · {chip} · {flash}"
        )
        self._part_card.show()

    def _on_board_changed(self, board: str):
        self._manual_board = board
        self._update_partition_card()

    def _open_partition_settings(self):
        from ui.partition_editor import PartitionEditor
        from models import InoConfig
        cfg = InoConfig()
        cfg.board = self._board_selector.currentText()
        cfg.flash_size = BOARDS.get(cfg.board, {}).get("flash_size", "4MB")
        editor = PartitionEditor(cfg, self)
        editor.applied.connect(self._on_partition_settings_applied)
        editor.exec()

    def _on_partition_settings_applied(self, cfg):
        self._update_partition_card()

    def _refresh_device_ui(self):
        self._device_list.clear()
        self._device_selector.clear()
        multi = len(self._devices) > 1
        self._batch_btn.setVisible(multi)
        for name, device in self._devices.items():
            item = QListWidgetItem(self._device_list)
            widget = DeviceItemWidget(device, show_checkbox=multi)
            item.setSizeHint(QSize(0, 60))
            self._device_list.setItemWidget(item, widget)
            self._device_selector.addItem(name)
            if multi:
                widget.checkbox_toggled.connect(self._update_batch_button)
        if multi:
            self._update_batch_button()

    def _update_device_status(self):
        count = len(self._devices)
        if count == 0:
            self._status_dot.set_online(False)
            self._status_text.setText("No devices found. Make sure your ESP32 is powered on and on the same Wi-Fi.")
            self._setup_btn.setText("Set up new ESP32 →")
            self._setup_btn.show()
            self._drop_zone.set_enabled(True)
            self._update_partition_card()
        else:
            self._status_dot.set_online(True)
            if self._selected_device:
                self._status_text.setText(
                    f"{count} device{'s' if count > 1 else ''} online · "
                    f"Selected: {self._selected_device.friendly_label}"
                )
            else:
                self._status_text.setText(f"{count} device{'s' if count > 1 else ''} found — select one to start")
                self._selected_device = next(iter(self._devices.values()))
                self._device_selector.setCurrentText(self._selected_device.name)
            self._setup_btn.setText("+ Add another device")
            self._setup_btn.show()
            self._drop_zone.set_enabled(True)
            self._update_partition_card()

    def _on_device_selected(self, item: QListWidgetItem):
        row = self._device_list.row(item)
        name = list(self._devices.keys())[row]
        self._selected_device = self._devices[name]
        self._device_selector.setCurrentText(name)
        self._update_device_status()
        self._update_partition_card()

    def _on_device_combo_changed(self, name: str):
        if name and name in self._devices:
            self._selected_device = self._devices[name]
            self._update_device_status()
            self._update_partition_card()

    # ── Batch flash ───────────────────────────────────────

    def _get_checked_devices(self) -> list[Device]:
        checked = []
        for i in range(self._device_list.count()):
            item = self._device_list.item(i)
            widget: DeviceItemWidget = self._device_list.itemWidget(item)
            if widget and widget.is_checked():
                checked.append(widget.device)
        return checked

    def _update_batch_button(self):
        checked = self._get_checked_devices()
        count = len(checked)
        self._batch_btn.setText(f"Flash Selected ({count})")
        self._batch_btn.setEnabled(count > 0)

    def _start_batch_flash(self):
        devices = self._get_checked_devices()
        if not devices:
            return
        self._batch_queue = list(devices)
        self._batch_index = 0
        self._batch_bar.show()
        self._batch_bar.setValue(0)
        self._batch_btn.setEnabled(False)
        self._process_next_batch()

    def _process_next_batch(self):
        if self._batch_index >= len(self._batch_queue):
            self._batch_bar.hide()
            self._batch_btn.setEnabled(True)
            self._update_batch_button()
            return

        device = self._batch_queue[self._batch_index]
        self._selected_device = device
        total = len(self._batch_queue)
        self._batch_bar.setFormat(
            f"Flashing {self._batch_index + 1}/{total}: {device.friendly_label} ..."
        )
        self._on_ino_received(self._batch_ino_path)

    def _advance_batch(self):
        self._batch_index += 1
        if self._batch_index < len(self._batch_queue):
            pct = int(self._batch_index / len(self._batch_queue) * 100)
            self._batch_bar.setValue(pct)
        QTimer.singleShot(800, self._process_next_batch)

    # ── INO handling ──────────────────────────────────────

    def _on_ino_received(self, path: str):
        self._batch_ino_path = path

        # If coming from config confirm, skip preview and compile directly
        if getattr(self._easy_overlay, '_config_confirmed', False):
            self._easy_overlay._config_confirmed = False
            cfg = getattr(self._easy_overlay, '_pending_cfg', None)
            if cfg is None:
                cfg = parse_ino(path)
            self._start_compile(path, cfg)
            return

        if not self._selected_device and self._devices:
            self._selected_device = next(iter(self._devices.values()))

        if not self._selected_device:
            if self._easy_mode:
                self._easy_overlay.show_no_device()
            else:
                msg = QMessageBox(self)
                msg.setWindowTitle("No device found")
                msg.setText("No ESP32 found on your network.")
                msg.setInformativeText(
                    "You can still configure and compile. "
                    "Upload will happen once a device is online.\n\n"
                    "For a new device, plug it in via USB to flash the base firmware first."
                )
                msg.addButton("Continue anyway", QMessageBox.ButtonRole.ActionRole)
                msg.addButton("Cancel", QMessageBox.ButtonRole.RejectRole)
                msg.exec()
                if msg.clickedButton().text() != "Continue anyway":
                    return

        cfg = parse_ino(path)
        if not cfg.board or cfg.board not in BOARDS:
            cfg.board = self._board_selector.currentText()
            cfg.flash_size = BOARDS.get(cfg.board, {}).get("flash_size", "4MB")

        if self._easy_mode:
            self._easy_overlay.show_config_review(cfg, path)
        else:
            target_name = self._selected_device.friendly_label if self._selected_device else ""
            dlg = ConfigDialog(cfg, target_device=target_name, parent=self)
            dlg.confirmed.connect(lambda c: self._start_compile(path, c))
            dlg.exec()

    def _start_compile(self, ino_path: str, cfg: InoConfig):
        self._stack.setCurrentIndex(1)
        self._flash_scene.start_compile(cfg.board)
        self._pending_cfg = cfg

        self._compiler = CompilerWorker(ino_path, cfg)
        self._compiler.progress.connect(self._on_compile_progress)
        self._compiler.finished.connect(lambda p: self._start_ota(p, cfg))
        self._compiler.failed.connect(self._on_error)
        self._compiler.start()

    def _on_compile_progress(self, msg: str):
        ml = msg.lower()
        if "check" in ml or "list" in ml:
            pct = 5
        elif "installing" in ml:
            pct = 15
        elif "compiling" in ml:
            pct = 40
        elif "done" in ml or "ready" in ml:
            pct = 90
        else:
            pct = 10
        self._flash_scene.set_progress(pct, msg)
        self._flash_scene.set_status(msg)
        self._easy_overlay.set_mascot_mood("focused")
        if self._easy_mode:
            self._easy_overlay._flash_status.setText(msg)

    def _on_error(self, friendly: str, raw: str):
        self._flash_scene.show_error(friendly, raw)
        cfg = self._pending_cfg or getattr(self, '_last_error_cfg', None)
        if cfg:
            self._flash_scene.set_error_context(cfg)
        self._easy_overlay.set_mascot_mood("surprise")

    def _on_save_binary(self, bin_path: str):
        import shutil
        from pathlib import Path
        from PyQt6.QtWidgets import QFileDialog
        suggested = Path(bin_path).name or "firmware.bin"
        path, _ = QFileDialog.getSaveFileName(
            self, "Save compiled binary", suggested,
            "Binary files (*.bin);;All files (*)"
        )
        if path:
            shutil.copy2(bin_path, path)

    def _on_flash_now(self, bin_path: str):
        if not self._selected_device or self._selected_device.name not in self._devices:
            return
        cfg = self._pending_cfg or InoConfig()
        self._flash_scene.start_ota()
        self._easy_overlay.set_mascot_mood("sweat")
        if self._easy_mode:
            self._easy_overlay._flash_status.setText("Uploading to ESP32...")
        self._ota = OtaWorker(self._selected_device, bin_path)
        self._ota.progress.connect(self._flash_scene.set_progress)
        self._ota.finished.connect(self._on_ota_finished)
        self._ota.failed.connect(self._on_ota_error)
        self._ota.start()

    def _start_ota(self, bin_path: str, cfg: InoConfig = None):
        self._pending_bin = bin_path
        self._pending_cfg = cfg

        if not self._selected_device or self._selected_device.name not in self._devices:
            self._flash_scene.show_compilation_ready(bin_path, has_device=False)
            if self._easy_mode:
                self._easy_overlay._flash_status.setText("Compilation done! Connect an ESP32 to flash.")
            return

        self._flash_scene.start_ota()
        self._easy_overlay.set_mascot_mood("sweat")
        if self._easy_mode:
            self._easy_overlay._flash_status.setText("Uploading to ESP32...")

        self._ota = OtaWorker(self._selected_device, bin_path)
        self._ota.progress.connect(self._flash_scene.set_progress)
        self._ota.finished.connect(self._on_ota_finished)
        self._ota.failed.connect(self._on_ota_error)
        self._ota.start()

    def _on_ota_error(self, msg: str):
        self._flash_scene.show_error(msg, "")
        self._easy_overlay.set_mascot_mood("surprise")
        if self._easy_mode:
            self._easy_overlay._flash_status.setText(msg)
        if hasattr(self, '_batch_queue') and self._batch_queue:
            QTimer.singleShot(2000, self._advance_batch)

    def _on_ota_finished(self):
        self._flash_scene.show_success(self._selected_device.name)
        self._easy_overlay.set_mascot_mood("excited")
        if self._easy_mode:
            self._easy_overlay._flash_progress.setValue(100)
            self._easy_overlay._flash_status.setText("Done! Rebooting...")
            QTimer.singleShot(1200, lambda: self._easy_overlay.show_success(self._selected_device.name))
        else:
            self._easy_overlay.show_success(self._selected_device.name)
        if hasattr(self, '_batch_queue') and self._batch_queue:
            QTimer.singleShot(1500, self._advance_batch)

    # ── USB Setup ─────────────────────────────────────────

    def _show_setup_wizard(self):
        if self._easy_mode:
            self._easy_overlay.show_setup()
        else:
            self._show_wizard_page()

    def _on_easy_device_selected(self, name: str):
        if name in self._devices:
            self._selected_device = self._devices[name]
        elif self._devices:
            self._selected_device = next(iter(self._devices.values()))

    def _on_plug_connected(self):
        from workers.usb_flash import UsbFlashWorker
        from discovery.usb import autodetect_port
        from pathlib import Path

        port = autodetect_port()
        if not port:
            return

        if getattr(sys, "frozen", False):
            base = sys._MEIPASS
        else:
            base = str(Path(__file__).parent.parent)
        base_fw = Path(base) / "firmware" / "espy_base.bin"
        if not base_fw.exists():
            return

        self._usb_worker = UsbFlashWorker(
            port, str(base_fw), "My ESP32", "", ""
        )
        self._usb_worker.finished.connect(lambda: self._show_usb_done())
        self._usb_worker.start()

    def _show_usb_done(self):
        self._easy_overlay.show_success("Your ESP32")

    def _show_serial_logger(self):
        self._serial_logger._refresh_ports()
        self._stack.setCurrentWidget(self._serial_logger)

    def _show_wizard_page(self):
        wizard = SetupWizard(self)
        wizard.finished.connect(lambda: self._stack.setCurrentIndex(0))
        self._stack.addWidget(wizard)
        self._stack.setCurrentWidget(wizard)

    # ── Mode switching ────────────────────────────────────

    def _show_easy_mode(self):
        self._easy_mode = True
        self._sidebar.hide()
        self._stack.hide()
        self._easy_overlay.setVisible(True)
        self._easy_overlay.raise_()

    def _switch_to_advanced(self):
        self._easy_mode = False
        self._easy_overlay.setVisible(False)
        self._sidebar.show()
        self._stack.show()
        self._stack.setCurrentIndex(0)
        self._update_device_status()

    def _toggle_mode(self):
        if self._easy_mode:
            self._switch_to_advanced()
        else:
            self._show_easy_mode()

    def closeEvent(self, e):
        if hasattr(self, "_discovery"):
            self._discovery.stop()
        if hasattr(self, "_compiler") and self._compiler:
            self._compiler.wait()
        if hasattr(self, "_ota") and self._ota:
            self._ota.wait()
        super().closeEvent(e)


# ══ parser.py ═══════════════════════════════════════

FRIENDLY_ERRORS: list[tuple[str, str]] = [
    (r"was not declared in this scope",
     "A function or variable is used before it's defined. Share the error below with your AI assistant."),
    (r"sketch uses .+ \((\d+)%\) of storage",
     "Your sketch is too large for this ESP32. Ask your AI assistant to remove unused libraries or simplify the code."),
    (r"multiple definition of",
     "Your code has a duplicate function — likely a copy-paste issue. Share the error below with your AI assistant."),
    (r"No such file or directory",
     "A required library is missing. Espy tried to install it automatically."),
    (r"'DHT' was not declared",
     "Missing DHT sensor library. Espy can install it automatically."),
    (r"board manager: esp32:esp32 not installed",
     "ESP32 support needs repair. Click to fix (one-time, ~10 seconds)."),
    (r"exit status 1",
     "Compilation failed. Here's the error log to share with your AI assistant:"),
]

COMMON_LIBRARY_HEADERS: dict[str, str] = {
    "DHT.h": "DHT sensor library",
    "DHT_U.h": "DHT sensor library",
    "Adafruit_Sensor.h": "Adafruit Unified Sensor",
    "PubSubClient.h": "PubSubClient",
    "ArduinoJson.h": "ArduinoJson",
    "SSD1306.h": "Adafruit SSD1306",
    "Adafruit_SSD1306.h": "Adafruit SSD1306",
    "Adafruit_GFX.h": "Adafruit GFX Library",
    "Adafruit_NeoPixel.h": "Adafruit NeoPixel",
    "FastLED.h": "FastLED",
    "Servo.h": "Servo",
    "OneWire.h": "OneWire",
    "DallasTemperature.h": "DallasTemperature",
    "SD.h": "SD",
    "SPI.h": "SPI",
    "Wire.h": "Wire",
    "WiFi.h": "WiFi",
    "WebServer.h": "WebServer",
    "ESPmDNS.h": "ESPmDNS",
    "Update.h": "Update",
    "Preferences.h": "Preferences",
    "LittleFS.h": "LittleFS",
    "LiquidCrystal_I2C.h": "LiquidCrystal I2C",
    "MQTT.h": "PubSubClient",
    "WiFiClient.h": "WiFiClient",
    "WiFiUdp.h": "WiFiUdp",
    "HTTPClient.h": "HTTPClient",
    "ESPAsyncWebServer.h": "ESPAsyncWebServer",
    "AsyncTCP.h": "AsyncTCP",
    "AsyncUDP.h": "AsyncUDP",
    "TFT_eSPI.h": "TFT_eSPI",
    "U8g2lib.h": "U8g2",
    "U8g2.h": "U8g2",
    "Adafruit_ILI9341.h": "Adafruit ILI9341",
    "Adafruit_ST7735.h": "Adafruit ST7735",
    "Adafruit_ST7789.h": "Adafruit ST7789",
    "Adafruit_SH110X.h": "Adafruit SH110X",
    "Adafruit_HX8357.h": "Adafruit HX8357",
    "BME280.h": "BME280",
    "BMP280.h": "BMP280",
    "Adafruit_BMP280.h": "Adafruit BMP280 Library",
    "Adafruit_BME280.h": "Adafruit BME280 Library",
    "Adafruit_BME680.h": "Adafruit BME680",
    "Adafruit_MQTT.h": "Adafruit MQTT Library",
    "HX711.h": "HX711",
    "MAX6675.h": "MAX6675",
    "IRremote.h": "IRremote",
    "LoRa.h": "LoRa",
    "MFRC522.h": "MFRC522",
    "PN532.h": "PN532",
    "RadioHead.h": "RadioHead",
    "nRF24L01.h": "nRF24L01",
    "ESP32Servo.h": "ESP32Servo",
    "Stepper.h": "Stepper",
    "AccelStepper.h": "AccelStepper",
    "NeoPixelBus.h": "NeoPixelBus",
    "EEPROM.h": "EEPROM",
    "SD_MMC.h": "SD_MMC",
    "FFat.h": "FFat",
    "SdFat.h": "SdFat",
    "BluetoothSerial.h": "BluetoothSerial",
    "ESP_NOW.h": "ESP_NOW",
    "ArduinoOTA.h": "ArduinoOTA",
    "NTPClient.h": "NTPClient",
    "Timezone.h": "Timezone",
    "SimpleTimer.h": "SimpleTimer",
    "TaskScheduler.h": "TaskScheduler",
    "ESP32Ping.h": "ESP32Ping",
    "DNSServer.h": "DNSServer",
    "StreamUtils.h": "StreamUtils",
}


def translate_error(stderr: str) -> str:
    for pattern, message in FRIENDLY_ERRORS:
        if re.search(pattern, stderr):
            return message
    # Generic fallback
    lines = [l for l in stderr.split("\n") if l.strip() and "warning" not in l.lower()]
    if lines:
        return f"Compilation failed. Share this error with your AI assistant:\n\n{lines[-1]}"
    return "Compilation failed. Share the error log with your AI assistant."


def extract_directive(content: str, key: str) -> str:
    m = re.search(rf"//\s*{key}\s*:\s*(.+)", content, re.IGNORECASE)
    if m:
        return m.group(1).strip()
    m = re.search(rf"\*\s*{key}\s*:\s*(.+)", content, re.IGNORECASE)
    if m:
        return m.group(1).strip()
    return ""



# Shorthand board name → full BOARDS key mapping
BOARD_ALIASES: dict[str, str] = {
    "ESP32C3": "ESP32-C3 DevKit",
    "ESP32-C3": "ESP32-C3 DevKit",
    "C3": "ESP32-C3 DevKit",
    "ESP32S3": "ESP32-S3 DevKitC",
    "ESP32-S3": "ESP32-S3 DevKitC",
    "S3": "ESP32-S3 DevKitC",
    "ESP32S2": "ESP32-S2 Saola",
    "ESP32-S2": "ESP32-S2 Saola",
    "S2": "ESP32-S2 Saola",
    "ESP32C6": "ESP32-C6 Dev Module",
    "ESP32-C6": "ESP32-C6 Dev Module",
    "C6": "ESP32-C6 Dev Module",
    "ESP32H2": "ESP32-H2 Dev Module",
    "ESP32-H2": "ESP32-H2 Dev Module",
    "H2": "ESP32-H2 Dev Module",
    "NodeMCU": "NodeMCU-32S",
    "ESP32": "ESP32 Dev Module",
}


# Chip headers that hint at the target board
CHIP_HEADER_TO_BOARD: dict[str, str] = {
    "esp32c3": "ESP32-C3 DevKit",
    "esp32s3": "ESP32-S3 DevKitC",
    "esp32s2": "ESP32-S2 Saola",
    "esp32c6": "ESP32-C6 Dev Module",
    "esp32h2": "ESP32-H2 Dev Module",
}


def detect_libraries_from_source(content: str) -> list[str]:
    found: list[str] = []
    for include in re.finditer(r'#include\s*[<"](.+?)[>"]', content):
        header = include.group(1).strip()
        if header in COMMON_LIBRARY_HEADERS:
            lib = COMMON_LIBRARY_HEADERS[header]
            if lib not in found:
                found.append(lib)
    return found


def parse_ino(path: str) -> InoConfig:
    cfg = InoConfig()
    try:
        with open(path, "r", encoding="utf-8", errors="replace") as f:
            content = f.read()
    except Exception as e:
        cfg.warnings.append(f"Could not open file: {e}")
        return cfg
    cfg.raw_content = content

    # Board
    board = extract_directive(content, "BOARD")
    if board:
        board_clean = board.split("(")[0].strip()
        if board_clean in BOARDS:
            cfg.board = board_clean
        elif board_clean in BOARD_ALIASES:
            cfg.board = BOARD_ALIASES[board_clean]
        else:
            for bname in BOARDS:
                if bname.lower().startswith(board_clean.lower()[:6]):
                    cfg.board = bname
                    break
    else:
        # Try to infer board from chip-specific #include directives
        for include in re.finditer(r'#include\s*[<"](.+?)[>"]', content, re.IGNORECASE):
            header = include.group(1).strip().lower()
            for chip_name, board_name in CHIP_HEADER_TO_BOARD.items():
                if chip_name in header:
                    cfg.board = board_name
                    break
            if cfg.board:
                break

    # Flash size
    flash = extract_directive(content, "FLASH_SIZE")
    if flash:
        cfg.flash_size = flash
    elif board:
        # Try to extract flash size from parenthesized part of board directive
        m = re.search(r'\([^)]*?(\d+)\s*MB[^)]*\)', board, re.IGNORECASE)
        if m:
            cfg.flash_size = f"{m.group(1)}MB"

    # Partition scheme — check code first, then parsed flash, then board default, fallback 4MB
    scheme = extract_directive(content, "PARTITION_SCHEME")
    if scheme:
        cfg.partition_scheme = scheme
    elif cfg.board and cfg.board in BOARDS:
        board_flash = cfg.flash_size or BOARDS[cfg.board].get("flash_size", "4MB")
        default_schemes = PARTITION_SCHEMES.get(board_flash, {})
        if not default_schemes:
            board_flash = BOARDS[cfg.board].get("flash_size", "4MB")
            default_schemes = PARTITION_SCHEMES.get(board_flash, {})
        cfg.partition_scheme = next(iter(default_schemes), "default_ota")

    # WiFi
    cfg.wifi_ssid = extract_directive(content, "WIFI_SSID")
    cfg.wifi_password = extract_directive(content, "WIFI_PASSWORD")

    # Device name
    cfg.device_name = extract_directive(content, "DEVICE_NAME")

    # OTA password
    cfg.ota_password = extract_directive(content, "OTA_PASSWORD")

    # Deep sleep
    ds = extract_directive(content, "DEEP_SLEEP")
    cfg.deep_sleep = ds.lower() in ("true", "yes", "1") if ds else False
    dsi = extract_directive(content, "DEEP_SLEEP_INTERVAL")
    cfg.deep_sleep_interval = int(dsi) if dsi.isdigit() else 0

    # Libraries from comments
    comment_libs: list[str] = []
    for key in ("LIBRARIES", "LIBRARY"):
        val = extract_directive(content, key)
        if val:
            comment_libs += [l.strip() for l in val.split(",") if l.strip()]

    # Libraries from #include detection
    source_libs = detect_libraries_from_source(content)

    # Merge: comment directives take priority
    all_lib_names: list[str] = []
    seen: set[str] = set()
    for lib in comment_libs + source_libs:
        if lib.lower() not in seen:
            seen.add(lib.lower())
            all_lib_names.append(lib)

    # Build LibraryInfo objects
    for lib_name in all_lib_names:
        available = lib_name in TOP_LIBRARIES
        cfg.libraries.append(LibraryInfo(
            name=lib_name,
            version="",
            available=available,
            needs_download=not available,
        ))

    # OTA conflict detection
    ota_patterns = [
        r'#include\s*[<"]ArduinoOTA\.h[">]',
        r'ArduinoOTA\.begin\s*\(',
        r'ArduinoOTA\.handle\s*\(',
        r'ArduinoOTA\s+ota',
    ]
    for pat in ota_patterns:
        if re.search(pat, content):
            cfg.has_ota_conflict = True
            cfg.auto_fixes.append({
                "type": "remove_ota",
                "label": "Remove ArduinoOTA code",
                "description": "Espy handles OTA automatically. Stripping ArduinoOTA includes and calls.",
            })
            break

    # Blocking loop detection
    if re.search(r'while\s*\(\s*true\s*\)', content):
        if not re.search(r'yield\s*\(\s*\)', content):
            cfg.warnings.append(
                "Your code has a while(true) loop without yield(). "
                "OTA updates may not work. Add a small delay or yield() inside the loop."
            )

    # Deep sleep + OTA conflict
    if cfg.deep_sleep and not cfg.has_ota_conflict:
        cfg.warnings.append(
            "Deep sleep is enabled. The device will wake periodically to check for OTA updates "
            "if you keep the OTA server running before sleeping."
        )

    return cfg


def _run_installer():
    try:
        from tools.install_arduino import download_arduino_cli, install_esp32_core
        cli = download_arduino_cli()
        if cli:
            install_esp32_core(cli)
    except Exception:
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    import sys
    from PyQt6.QtWidgets import QApplication
    _run_installer()
    if not QApplication.instance():
        app = QApplication(sys.argv)
        w = MainWindow()
        w.show()
        sys.exit(app.exec())
    else:
        print("Espy loaded (QApplication already exists)")
