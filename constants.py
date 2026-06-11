import sys
from pathlib import Path

APP_VERSION = "1.0.0"
APP_NAME = "EasyESP"

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
    APP_DIR = Path.home() / ".config" / "easyesp"
    USB_PORT_PATTERNS = ("ttyUSB", "ttyACM")
    SYSTEM_FONT = "'Ubuntu', 'Noto Sans', system-ui, sans-serif"
    MONO_FONT = "'Ubuntu Mono', 'Consolas', monospace"
elif sys.platform == "win32":
    APP_DIR = Path.home() / "AppData" / "Local" / "EasyESP"
    USB_PORT_PATTERNS = ("COM",)
    SYSTEM_FONT = "'Segoe UI', system-ui, sans-serif"
    MONO_FONT = "'Consolas', 'Courier New', monospace"
else:
    APP_DIR = Path.home() / ".config" / "easyesp"
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
    # Sensors
    "DHT sensor library",
    "Adafruit Unified Sensor",
    "DallasTemperature",
    "OneWire",
    "BME280",
    "BMP280",
    "Adafruit BMP280 Library",
    "Adafruit BME280 Library",
    "Adafruit BME680",
    "Adafruit MQTT Library",
    "Adafruit MCP9808",
    "Adafruit VEML6070",
    "Adafruit TSL2561",
    "Adafruit SHT31",
    "Adafruit SGP30",
    "Adafruit MPRLS",
    "Adafruit LPS35HW",
    "Adafruit ADXL345",
    "Adafruit MPU6050",
    "Adafruit HMC5883",
    "AM2320",
    "DS18B20",
    "MAX6675",
    "HX711",
    "HC-SR04",
    "PulseSensor Playground",
    "MLX90614",
    "MQ135",
    "MQ2",
    "MQ7",
    # Displays
    "Adafruit SSD1306",
    "Adafruit GFX Library",
    "TFT_eSPI",
    "LiquidCrystal I2C",
    "LiquidCrystal",
    "U8g2",
    "Adafruit ILI9341",
    "Adafruit ST7735",
    "Adafruit ST7789",
    "Adafruit SH110X",
    "Adafruit HX8357",
    # Communication & Protocols
    "WiFi",
    "WebServer",
    "ESPmDNS",
    "Update",
    "PubSubClient",
    "ArduinoJson",
    "ESPAsyncWebServer",
    "AsyncTCP",
    "AsyncUDP",
    "HTTPClient",
    "WiFiClient",
    "WiFiUdp",
    "ESP_NOW",
    "BluetoothSerial",
    "Modbus RTU",
    "Modbus",
    "IRremote",
    "RadioHead",
    "LoRa",
    "nRF24L01",
    "MFRC522",
    "PN532",
    # Storage & Filesystem
    "Preferences",
    "LittleFS",
    "SD",
    "SPI",
    "Wire",
    "SD_MMC",
    "FFat",
    "SdFat",
    "EEPROM",
    # Audio
    "ESP8266Audio",
    "AudioFileSourceICYStream",
    "AudioOutputI2S",
    "AudioGeneratorMP3",
    "TMRpcm",
    "DFRobotDFPlayerMini",
    # Motors & Actuators
    "Servo",
    "ESP32Servo",
    "Stepper",
    "AccelStepper",
    "Adafruit Motor Shield",
    "DRV8825",
    "A4988",
    # LEDs & Lighting
    "Adafruit NeoPixel",
    "FastLED",
    "NeoPixelBus",
    "Adafruit DotStar",
    "TLC5947",
    # Networking & IoT
    "MQTT",
    "ArduinoOTA",
    "TelnetStream",
    "ESP32Ping",
    "NTPClient",
    "Timezone",
    "SimpleTimer",
    "TaskScheduler",
    "EEPROMRotator",
    "ConfigPortal32",
]

# ── Board pinouts for wiring detection ──────────────────────

BOARD_PINOUTS = {
    "ESP32 Dev Module": {
        "builtin_led": 2,
        "voltage": "3.3V",
        "default_pins": {
            "i2c": {"SDA": 21, "SCL": 22},
            "spi": {"MOSI": 23, "MISO": 19, "SCLK": 18, "CS": 5},
            "uart": {"TX": 1, "RX": 3},
        },
        "gpio_caps": {
            0:  ["pwm", "touch", "adc2"],
            1:  ["pwm", "uart_tx"],
            2:  ["pwm", "touch", "adc2", "led"],
            3:  ["pwm", "uart_rx"],
            4:  ["pwm", "touch", "adc2"],
            5:  ["pwm", "spi_cs"],
            12: ["pwm", "touch", "adc2"],
            13: ["pwm", "touch", "adc2"],
            14: ["pwm", "touch", "adc2"],
            15: ["pwm", "touch", "adc2"],
            16: ["pwm", "uart2_tx"],
            17: ["pwm", "uart2_rx"],
            18: ["pwm", "spi_sclk"],
            19: ["pwm", "spi_miso"],
            21: ["pwm", "i2c_sda"],
            22: ["pwm", "i2c_scl"],
            23: ["pwm", "spi_mosi"],
            25: ["pwm", "dac", "adc2"],
            26: ["pwm", "dac", "adc2"],
            27: ["pwm", "touch", "adc2"],
            32: ["pwm", "touch", "adc1"],
            33: ["pwm", "touch", "adc1"],
            34: ["adc1", "input_only"],
            35: ["adc1", "input_only"],
            36: ["adc1", "input_only"],
            39: ["adc1", "input_only"],
        },
    },
    "NodeMCU-32S": {
        "builtin_led": 2,
        "voltage": "3.3V",
        "default_pins": {
            "i2c": {"SDA": 21, "SCL": 22},
            "spi": {"MOSI": 23, "MISO": 19, "SCLK": 18, "CS": 5},
            "uart": {"TX": 1, "RX": 3},
        },
        "gpio_caps": {
            0:  ["pwm", "touch", "adc2"],
            1:  ["pwm", "uart_tx"],
            2:  ["pwm", "touch", "adc2", "led"],
            3:  ["pwm", "uart_rx"],
            4:  ["pwm", "touch", "adc2"],
            5:  ["pwm", "spi_cs"],
            12: ["pwm", "touch", "adc2"],
            13: ["pwm", "touch", "adc2", "spi_mosi"],
            14: ["pwm", "touch", "adc2", "spi_sclk"],
            15: ["pwm", "touch", "adc2", "spi_miso"],
            16: ["pwm", "uart2_tx"],
            17: ["pwm", "uart2_rx"],
            18: ["pwm", "spi_sclk"],
            19: ["pwm", "spi_miso"],
            21: ["pwm", "i2c_sda"],
            22: ["pwm", "i2c_scl"],
            23: ["pwm", "spi_mosi"],
            25: ["pwm", "dac", "adc2"],
            26: ["pwm", "dac", "adc2"],
            27: ["pwm", "touch", "adc2"],
            32: ["pwm", "touch", "adc1"],
            33: ["pwm", "touch", "adc1"],
            34: ["adc1", "input_only"],
            35: ["adc1", "input_only"],
            36: ["adc1", "input_only"],
            39: ["adc1", "input_only"],
        },
    },
    "ESP32-S3 DevKitC": {
        "builtin_led": 48,
        "voltage": "3.3V",
        "default_pins": {
            "i2c": {"SDA": 1, "SCL": 2},
            "spi": {"MOSI": 11, "MISO": 13, "SCLK": 12, "CS": 10},
            "uart": {"TX": 43, "RX": 44},
        },
        "gpio_caps": {
            1:  ["pwm", "adc", "i2c_sda"],
            2:  ["pwm", "adc", "i2c_scl"],
            3:  ["pwm", "adc"],
            4:  ["pwm", "adc"],
            5:  ["pwm", "adc"],
            6:  ["pwm", "adc"],
            7:  ["pwm", "adc"],
            8:  ["pwm", "adc"],
            9:  ["pwm", "adc"],
            10: ["pwm", "spi_cs"],
            11: ["pwm", "spi_mosi"],
            12: ["pwm", "spi_sclk"],
            13: ["pwm", "spi_miso"],
            14: ["pwm", "adc"],
            15: ["pwm", "adc"],
            16: ["pwm", "adc"],
            17: ["pwm", "adc"],
            18: ["pwm", "adc", "usb_dminus"],
            19: ["pwm", "adc", "usb_dplus"],
            20: ["pwm", "adc"],
            21: ["pwm", "adc"],
            35: ["pwm"],
            36: ["pwm"],
            37: ["pwm"],
            38: ["pwm"],
            39: ["pwm"],
            40: ["pwm"],
            41: ["pwm"],
            42: ["pwm"],
            43: ["pwm", "uart_tx"],
            44: ["pwm", "uart_rx"],
            45: ["pwm"],
            46: ["pwm"],
            47: ["pwm"],
            48: ["pwm", "led"],
        },
    },
    "ESP32-C3 DevKit": {
        "builtin_led": 8,
        "voltage": "3.3V",
        "default_pins": {
            "i2c": {"SDA": 0, "SCL": 1},
            "spi": {"MOSI": 6, "MISO": 2, "SCLK": 3, "CS": 7},
            "uart": {"TX": 21, "RX": 20},
        },
        "gpio_caps": {
            0:  ["pwm", "adc", "i2c_sda"],
            1:  ["pwm", "adc", "i2c_scl"],
            2:  ["pwm", "adc", "spi_miso"],
            3:  ["pwm", "adc", "spi_sclk"],
            4:  ["pwm", "adc"],
            5:  ["pwm", "adc"],
            6:  ["pwm", "adc", "spi_mosi"],
            7:  ["pwm", "adc", "spi_cs"],
            8:  ["pwm", "adc", "led"],
            9:  ["pwm", "adc"],
            10: ["pwm", "adc"],
            18: ["pwm"],
            19: ["pwm"],
            20: ["pwm", "uart_rx"],
            21: ["pwm", "uart_tx"],
        },
    },
    "ESP32-S2 Saola": {
        "builtin_led": 15,
        "voltage": "3.3V",
        "default_pins": {
            "i2c": {"SDA": 1, "SCL": 2},
            "spi": {"MOSI": 35, "MISO": 37, "SCLK": 36, "CS": 34},
            "uart": {"TX": 43, "RX": 44},
        },
        "gpio_caps": {
            0:  ["pwm", "touch", "adc"],
            1:  ["pwm", "touch", "adc", "i2c_sda"],
            2:  ["pwm", "touch", "adc", "i2c_scl"],
            3:  ["pwm", "touch", "adc"],
            4:  ["pwm", "touch", "adc"],
            5:  ["pwm", "touch", "adc"],
            6:  ["pwm", "touch", "adc"],
            7:  ["pwm", "touch", "adc"],
            8:  ["pwm", "touch", "adc"],
            9:  ["pwm", "touch", "adc"],
            10: ["pwm", "touch", "adc"],
            11: ["pwm", "touch", "adc"],
            12: ["pwm", "touch", "adc"],
            13: ["pwm", "touch", "adc"],
            14: ["pwm", "touch", "adc"],
            15: ["pwm", "touch", "adc", "led"],
            16: ["pwm", "touch", "adc"],
            17: ["pwm", "dac", "adc"],
            18: ["pwm", "dac", "adc"],
            19: ["pwm", "adc"],
            20: ["pwm", "adc"],
            21: ["pwm", "adc"],
            26: ["pwm", "adc"],
            33: ["pwm", "adc"],
            34: ["pwm", "spi_cs"],
            35: ["pwm", "spi_mosi"],
            36: ["pwm", "spi_sclk"],
            37: ["pwm", "spi_miso"],
            38: ["pwm"],
            39: ["pwm"],
            40: ["pwm"],
            41: ["pwm"],
            42: ["pwm"],
            43: ["pwm", "uart_tx"],
            44: ["pwm", "uart_rx"],
            45: ["pwm"],
            46: ["pwm"],
        },
    },
    "ESP32-C6 Dev Module": {
        "builtin_led": 8,
        "voltage": "3.3V",
        "default_pins": {
            "i2c": {"SDA": 22, "SCL": 23},
            "spi": {"MOSI": 6, "MISO": 5, "SCLK": 4, "CS": 7},
            "uart": {"TX": 19, "RX": 20},
        },
        "gpio_caps": {
            0:  ["pwm", "adc"],
            1:  ["pwm", "adc"],
            2:  ["pwm", "adc"],
            3:  ["pwm", "adc"],
            4:  ["pwm", "adc", "spi_sclk"],
            5:  ["pwm", "adc", "spi_miso"],
            6:  ["pwm", "adc", "spi_mosi"],
            7:  ["pwm", "adc", "spi_cs"],
            8:  ["pwm", "adc", "led"],
            9:  ["pwm", "adc"],
            10: ["pwm", "adc"],
            11: ["pwm", "adc"],
            12: ["pwm", "adc"],
            13: ["pwm", "adc"],
            14: ["pwm", "adc"],
            15: ["pwm", "adc"],
            16: ["pwm", "adc"],
            17: ["pwm", "adc"],
            18: ["pwm", "adc"],
            19: ["pwm", "uart_tx"],
            20: ["pwm", "uart_rx"],
            21: ["pwm", "adc"],
            22: ["pwm", "i2c_sda"],
            23: ["pwm", "i2c_scl"],
        },
    },
    "ESP32-H2 Dev Module": {
        "builtin_led": 8,
        "voltage": "3.3V",
        "default_pins": {
            "i2c": {"SDA": 1, "SCL": 2},
            "spi": {"MOSI": 6, "MISO": 5, "SCLK": 4, "CS": 7},
            "uart": {"TX": 19, "RX": 20},
        },
        "gpio_caps": {
            0:  ["pwm", "adc"],
            1:  ["pwm", "adc", "i2c_sda"],
            2:  ["pwm", "adc", "i2c_scl"],
            3:  ["pwm", "adc"],
            4:  ["pwm", "adc", "spi_sclk"],
            5:  ["pwm", "adc", "spi_miso"],
            6:  ["pwm", "adc", "spi_mosi"],
            7:  ["pwm", "adc", "spi_cs"],
            8:  ["pwm", "adc", "led"],
            9:  ["pwm", "adc"],
            10: ["pwm", "adc"],
            11: ["pwm", "adc"],
            12: ["pwm", "adc"],
            13: ["pwm", "adc"],
            14: ["pwm", "adc"],
            15: ["pwm", "adc"],
            16: ["pwm", "adc"],
            17: ["pwm", "adc"],
            18: ["pwm", "adc"],
            19: ["pwm", "uart_tx"],
            20: ["pwm", "uart_rx"],
            21: ["pwm", "adc"],
            22: ["pwm", "adc"],
        },
    },
}
