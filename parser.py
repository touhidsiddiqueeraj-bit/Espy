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


def resolve_gpio(raw: str) -> int:
    raw = raw.strip()
    if raw.startswith("D") and raw[1:].isdigit():
        return int(raw[1:])
    if raw.isdigit():
        return int(raw)
    return -1


def detect_pins(content: str, board: str, libraries) -> tuple:
    from models import DetectedPin, WiringSuggestion
    from constants import BOARD_PINOUTS

    pinout = BOARD_PINOUTS.get(board, {})
    caps = pinout.get("gpio_caps", {})
    builtin_led = pinout.get("builtin_led", 2)

    detected_pins: list[DetectedPin] = []
    suggestions: list[WiringSuggestion] = []
    seen_gpios: set[int] = set()
    seen_components: set[str] = set()

    def add_pin(gpio: int, name: str, direction: str, function: str,
                lib: str = "", notes: str = ""):
        if gpio < 0 or gpio in seen_gpios:
            return
        seen_gpios.add(gpio)
        pin_caps = caps.get(gpio, [])
        if "input_only" in pin_caps and direction == "output":
            notes += f" ⚠ GPIO{gpio} is input-only on {board}!"
        detected_pins.append(DetectedPin(
            name=name, gpio=gpio, direction=direction,
            function=function, library=lib, notes=notes
        ))

    def add_suggestion(component: str, pins_list, protocol: str,
                       lib: str = "", notes: str = "", color: str = "#4A90D9"):
        if component in seen_components:
            return
        seen_components.add(component)
        suggestions.append(WiringSuggestion(
            component=component, pins=pins_list,
            protocol=protocol, library=lib, notes=notes, color=color
        ))

    # 1. Basic GPIO pinMode / digitalWrite / digitalRead / analogRead / analogWrite
    for m in re.finditer(r'pinMode\s*\(\s*(\w+|D\d+)\s*,\s*(OUTPUT|INPUT|INPUT_PULLUP)\s*\)', content):
        gpio = resolve_gpio(m.group(1))
        direction = "output" if m.group(2) == "OUTPUT" else "input"
        if direction == "output":
            add_pin(gpio, f"GPIO{gpio} (pinMode OUTPUT)", "output", "digital")
        else:
            add_pin(gpio, f"GPIO{gpio} (pinMode {m.group(2)})", "input", "digital")

    for m in re.finditer(r'digitalWrite\s*\(\s*(\w+|D\d+)\s*,', content):
        gpio = resolve_gpio(m.group(1))
        add_pin(gpio, f"GPIO{gpio} (digital output)", "output", "digital")

    for m in re.finditer(r'digitalRead\s*\(\s*(\w+|D\d+)\s*\)', content):
        gpio = resolve_gpio(m.group(1))
        add_pin(gpio, f"GPIO{gpio} (digital input)", "input", "digital")

    for m in re.finditer(r'analogRead\s*\(\s*(\w+|D\d+)\s*\)', content):
        gpio = resolve_gpio(m.group(1))
        pin_caps = caps.get(gpio, [])
        adc_type = next((c for c in pin_caps if c.startswith("adc")), "adc?")
        add_pin(gpio, f"GPIO{gpio} (analog in - {adc_type})", "input", "analog")

    for m in re.finditer(r'analogWrite\s*\(\s*(\w+|D\d+)\s*,', content):
        gpio = resolve_gpio(m.group(1))
        add_pin(gpio, f"GPIO{gpio} (PWM out)", "output", "pwm")

    # 2. I2C — Wire.begin(SDA, SCL)
    for m in re.finditer(r'Wire\.(?:begin|setPins)\s*\(\s*(\d+)\s*,\s*(\d+)\s*\)', content):
        sda, scl = int(m.group(1)), int(m.group(2))
        add_pin(sda, "I2C SDA", "bidirectional", "i2c", "Wire")
        add_pin(scl, "I2C SCL", "output", "i2c", "Wire")
        add_suggestion("I2C Bus", [("SDA", sda), ("SCL", scl)],
                       "I2C", "Wire",
                       "Connect SDA→SDA and SCL→SCL. Use 3.3V logic level.",
                       "#FF6B6B")

    # 3. SPI — SPI.begin(SCLK, MISO, MOSI, CS)
    for m in re.finditer(r'SPI\.(?:begin|setPins)\s*\(\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*\)', content):
        sclk, miso, mosi, cs = int(m.group(1)), int(m.group(2)), int(m.group(3)), int(m.group(4))
        add_pin(sclk, "SPI SCLK", "output", "spi", "SPI")
        add_pin(miso, "SPI MISO", "input", "spi", "SPI")
        add_pin(mosi, "SPI MOSI", "output", "spi", "SPI")
        add_pin(cs, "SPI CS/SS", "output", "spi", "SPI")
        add_suggestion("SPI Bus", [("SCLK", sclk), ("MISO", miso), ("MOSI", mosi), ("CS", cs)],
                       "SPI", "SPI",
                       "Connect MOSI→MOSI, MISO→MISO, SCLK→SCLK, CS→CS. Use 3.3V.",
                       "#845EC2")

    # 4. OneWire
    for m in re.finditer(r'OneWire\s+\w+\s*\(\s*(\d+)\s*\)', content):
        gpio = int(m.group(1))
        add_pin(gpio, "OneWire data", "bidirectional", "onewire", "OneWire")
        add_suggestion("OneWire Bus", [("DATA", gpio)],
                       "OneWire", "OneWire",
                       "Connect DATA pin. Add 4.7kΩ pull-up resistor between DATA and 3.3V.",
                       "#FFC75F")

    for m in re.finditer(r'DallasTemperature\s+\w+\s*\(', content):
        if not any("OneWire" in s.component for s in suggestions):
            add_suggestion("DS18B20 (DallasTemperature)", [("DATA", "OneWire pin")],
                           "OneWire", "DallasTemperature",
                           "Connect DS18B20 DATA to OneWire pin. Add 4.7kΩ pull-up.",
                           "#FFC75F")

    # 5. DHT sensor
    for m in re.finditer(r'(dht|DHT)\s+\w+\s*[;=]', content):
        pass

    for m in re.finditer(r'(?:dht|DHT)\s*\.\s*begin\s*\(\s*(\d+)\s*\)', content):
        gpio = int(m.group(1))
        add_pin(gpio, "DHT data", "bidirectional", "onewire", "DHT sensor library")
        add_suggestion("DHT Sensor", [("DATA", gpio)],
                       "OneWire", "DHT sensor library",
                       "Connect DHT VCC→3.3V, DATA→GPIO{gpio}, GND→GND. "
                       "Add 10kΩ pull-up between DATA and 3.3V.",
                       "#FF6B6B")

    for m in re.finditer(r'#include\s*[<"]DHT\.h[>"]', content):
        # Try to find DHT.begin() on same or next lines
        dht_match = re.search(r'DHT\w*\s*\w*\s*[;=].*?begin\s*\(\s*(\d+)', content, re.DOTALL)
        if dht_match:
            gpio = int(dht_match.group(1))
            if gpio not in seen_gpios:
                add_pin(gpio, "DHT data", "bidirectional", "onewire", "DHT sensor library")
                add_suggestion("DHT Sensor", [("DATA", gpio)],
                               "OneWire", "DHT sensor library",
                               "Connect DHT VCC→3.3V, DATA→GPIO{gpio}, GND→GND. Add 10kΩ pull-up.",
                               "#FF6B6B")

    # 6. Servo
    for m in re.finditer(r'(\w+)\.attach\s*\(\s*(\d+)', content):
        servo_name = m.group(1).lower()
        gpio = int(m.group(2))
        if "servo" in servo_name or m.group(1) in content:
            add_pin(gpio, f"Servo signal ({m.group(1)})", "output", "pwm", "Servo/ESP32Servo")
            add_suggestion(f"Servo ({m.group(1)})", [("Signal", gpio)],
                           "PWM", "Servo",
                           "Connect servo signal wire→GPIO{gpio}, VCC→5V (external), GND→GND (common).",
                           "#4B7BEC")

    # 7. LED strips — FastLED / NeoPixel
    for m in re.finditer(r'FastLED\s*\.\s*addLeds\s*<\s*([^,>]+),\s*(\d+)', content):
        gpio = int(m.group(2))
        pin_caps = caps.get(gpio, [])
        if "pwm" in pin_caps or "digital" in pin_caps:
            add_pin(gpio, "LED strip data", "output", "digital", "FastLED")
            add_suggestion("Addressable LEDs (FastLED)", [("DATA", gpio)],
                           "Digital", "FastLED",
                           f"Connect LED strip DATA→GPIO{gpio}, VCC→5V, GND→GND. "
                           "Add 470Ω resistor on data line.",
                           "#F9A825")
    for m in re.finditer(r'FastLED\s*\.\s*addLeds\s*<\s*[^,>]+\s*>\s*\(\s*\w+\s*,\s*(\d+)', content):
        gpio = int(m.group(1))
        add_pin(gpio, "LED strip data", "output", "digital", "FastLED")
        add_suggestion("Addressable LEDs (FastLED)", [("DATA", gpio)],
                       "Digital", "FastLED",
                       "Connect LED strip DATA→GPIO{gpio}, VCC→5V, GND→GND. "
                       "Add 470Ω resistor on data line.",
                       "#F9A825")

    for m in re.finditer(r'Adafruit_NeoPixel\s+\w+\s*\(\s*\d+\s*,\s*(\d+)', content):
        gpio = int(m.group(1))
        add_pin(gpio, "NeoPixel data", "output", "digital", "Adafruit NeoPixel")
        add_suggestion("NeoPixel LEDs", [("DATA", gpio)],
                       "Digital", "Adafruit NeoPixel",
                       "Connect NeoPixel DATA→GPIO{gpio}, VCC→5V, GND→GND. "
                       "Add 300-500Ω resistor on data line.",
                       "#F9A825")

    # 8. I2C LCD
    if any("LiquidCrystal I2C" in lib.name for lib in libraries):
        default_i2c = pinout.get("default_pins", {}).get("i2c", {})
        sda = default_i2c.get("SDA", 21)
        scl = default_i2c.get("SCL", 22)
        add_pin(sda, "I2C SDA (LCD)", "bidirectional", "i2c", "LiquidCrystal I2C")
        add_pin(scl, "I2C SCL (LCD)", "output", "i2c", "LiquidCrystal I2C")
        add_suggestion("I2C LCD Display", [("SDA", sda), ("SCL", scl)],
                       "I2C", "LiquidCrystal I2C",
                       f"Connect LCD SDA→GPIO{sda}, SCL→GPIO{scl}, VCC→5V, GND→GND.",
                       "#00BFA5")

    # 9. OLED displays (I2C or SPI)
    if any("SSD1306" in lib.name for lib in libraries):
        if re.search(r'Wire', content):
            default_i2c = pinout.get("default_pins", {}).get("i2c", {})
            sda = default_i2c.get("SDA", 21)
            scl = default_i2c.get("SCL", 22)
            add_suggestion("OLED Display (I2C)", [("SDA", sda), ("SCL", scl)],
                           "I2C", "Adafruit SSD1306",
                           f"Connect OLED SDA→GPIO{sda}, SCL→GPIO{scl}, VCC→3.3V, GND→GND.",
                           "#00BFA5")
        elif re.search(r'SPI', content):
            default_spi = pinout.get("default_pins", {}).get("spi", {})
            add_suggestion("OLED Display (SPI)", [
                ("MOSI", default_spi.get("MOSI", 23)),
                ("SCLK", default_spi.get("SCLK", 18)),
            ], "SPI", "Adafruit SSD1306",
                           "Connect OLED MOSI→MOSI, SCLK→SCLK, DC→any GPIO, CS→any GPIO, "
                           "VCC→3.3V, GND→GND.",
                           "#00BFA5")

    # 10. HX711 load cell amp
    for m in re.finditer(r'HX711\s+\w+\s*\(\s*(\d+)\s*,\s*(\d+)\s*\)', content):
        dout, sck = int(m.group(1)), int(m.group(2))
        add_pin(dout, "HX711 DOUT", "input", "digital", "HX711")
        add_pin(sck, "HX711 SCK", "output", "digital", "HX711")
        add_suggestion("Load Cell (HX711)", [("DOUT", dout), ("SCK", sck)],
                       "Digital", "HX711",
                       f"Connect HX711 DOUT→GPIO{dout}, SCK→GPIO{sck}, VCC→5V, GND→GND.",
                       "#9C27B0")

    # 11. MAX6675 thermocouple
    for m in re.finditer(r'MAX6675\s+\w+\s*\(\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*\)', content):
        cs, so, sck = int(m.group(1)), int(m.group(2)), int(m.group(3))
        add_pin(cs, "MAX6675 CS", "output", "spi", "MAX6675")
        add_pin(so, "MAX6675 SO", "input", "spi", "MAX6675")
        add_pin(sck, "MAX6675 SCK", "output", "spi", "MAX6675")
        add_suggestion("Thermocouple (MAX6675)", [("CS", cs), ("SO", so), ("SCK", sck)],
                       "SPI", "MAX6675",
                       f"Connect MAX6675 CS→GPIO{cs}, SO→MISO, SCK→SCLK, VCC→3.3V, GND→GND.",
                       "#FF7043")

    # 12. #define / const pin constants
    for m in re.finditer(r'#define\s+(\w*(?:PIN|pin)\w*)\s+(\d+)', content):
        name = m.group(1)
        gpio = int(m.group(2))
        add_pin(gpio, f"{name}", "output", "digital")

    for m in re.finditer(r'const\s+(int|uint8_t)\s+(\w*(?:PIN|pin)\w*)\s*=\s*(\d+)', content):
        name = m.group(2)
        gpio = int(m.group(3))
        add_pin(gpio, f"{name}", "output", "digital")

    # 13. DHT constructor with pin: DHT dht(pin, type)
    for m in re.finditer(r'(?:DHT|dht)\s+\w+\s*\(\s*(\d+)\s*,', content):
        gpio = int(m.group(1))
        if gpio not in seen_gpios:
            add_pin(gpio, "DHT data pin", "bidirectional", "onewire", "DHT sensor library")
        add_suggestion("DHT Sensor", [("DATA", gpio)],
                       "OneWire", "DHT sensor library",
                       f"Connect DHT VCC→3.3V, DATA→GPIO{gpio}, GND→GND. "
                       "Add 10kΩ pull-up between DATA and 3.3V.",
                       "#FF6B6B")

    # 14. Built-in LED check (after all pin detection)
    if builtin_led in seen_gpios:
        # Update existing pin name and add suggestion
        for p in detected_pins:
            if p.gpio == builtin_led:
                p.name = f"Built-in LED (GPIO{builtin_led})"
                p.notes = f"Built-in LED is connected to GPIO{builtin_led} on this board."
        if "Built-in LED" not in str(seen_components):
            add_suggestion("Built-in LED", [("LED", builtin_led)],
                           "Digital", "",
                           f"Built-in LED is on GPIO{builtin_led}. No external wiring needed.",
                           "#FFD54F")
    else:
        has_led = re.search(r'pinMode\s*\(\s*' + str(builtin_led) + r'\s*,\s*OUTPUT\s*\)', content)
        if has_led:
            add_pin(builtin_led, f"Built-in LED (GPIO{builtin_led})", "output", "digital",
                    notes=f"Built-in LED on GPIO{builtin_led}.")
            add_suggestion("Built-in LED", [("LED", builtin_led)],
                           "Digital", "",
                           f"Built-in LED is on GPIO{builtin_led}. No external wiring needed.",
                           "#FFD54F")

    # 15. Check for unconnected detected components from #include
    for m in re.finditer(r'#include\s*[<"](.+?)[>"]', content):
        header = m.group(1).strip()
        if header == "DHT.h" and "DHT" not in str(seen_components):
            gpio = 4  # Common default
            if gpio not in seen_gpios:
                add_suggestion("DHT Sensor (detected)", [("DATA", f"GPIO{gpio} (default)")],
                               "OneWire", "DHT sensor library",
                               f"Connect DHT VCC→3.3V, DATA→GPIO{gpio}, GND→GND. "
                               "Add 10kΩ pull-up resistor.",
                               "#FF6B6B")

    # — LED blink special case (external LED, not built-in) —
    has_led_suggestion = any("LED" in s.component for s in suggestions)
    if not has_led_suggestion:
        for m in re.finditer(r'digitalWrite\s*\(\s*(\w+|D\d+)\s*,', content):
            gpio = resolve_gpio(m.group(1))
            if gpio > 0 and gpio != builtin_led:
                has_existing_name = any(
                    "LED" in p.name or p.gpio == gpio for p in detected_pins
                )
                if not has_existing_name:
                    add_pin(gpio, "External LED (blink)", "output", "digital")
                add_suggestion("External LED (Blink)", [("Anode (+)", gpio), ("Cathode (-)", "GND")],
                               "Digital", "",
                               f"Connect LED anode(+)→GPIO{gpio} via 220Ω resistor, cathode(-)→GND.",
                               "#FFD54F")
                break

    return detected_pins, suggestions


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
                if bname.lower().startswith(board_clean.lower()):
                    cfg.board = bname
                    break
            if not cfg.board:
                cfg.board = board_clean
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

    # Pin and wiring detection
    cfg.detected_pins, cfg.wiring_suggestions = detect_pins(content, cfg.board, cfg.libraries)
    for s in cfg.wiring_suggestions:
        if s.notes:
            cfg.warnings.append(s.notes)

    return cfg
