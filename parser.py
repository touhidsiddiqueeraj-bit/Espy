from __future__ import annotations
import re
import os
from typing import Optional
from models import InoConfig, LibraryInfo
from constants import BOARDS, TOP_LIBRARIES, PARTITION_SCHEMES

FRIENDLY_ERRORS: list[tuple[str, str]] = [
    (r"was not declared in this scope",
     "A function or variable is used before it's defined. Share the error below with your AI assistant."),
    (r"sketch uses .+ \((\d+)%\) of storage",
     "Your sketch is too large for this ESP32. Ask your AI assistant to remove unused libraries or simplify the code."),
    (r"multiple definition of",
     "Your code has a duplicate function — likely a copy-paste issue. Share the error below with your AI assistant."),
    (r"No such file or directory",
     "A required library is missing. EasyESP tried to install it automatically."),
    (r"'DHT' was not declared",
     "Missing DHT sensor library. EasyESP can install it automatically."),
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
                "description": "EasyESP handles OTA automatically. Stripping ArduinoOTA includes and calls.",
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
