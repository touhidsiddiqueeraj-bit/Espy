from constants import BOARDS

# LED_BUILTIN pins for each supported board
LED_PINS = {
    "ESP32 Dev Module": 2,
    "NodeMCU-32S":      2,
    "ESP32-S3 DevKitC": 48,
    "ESP32-C3 DevKit":  8,
    "ESP32-S2 Saola":   15,
    "ESP32-C6 Dev Module": 8,
    "ESP32-H2 Dev Module": 8,
}

BLINK_EXAMPLES = {}

for name, info in BOARDS.items():
    pin = LED_PINS.get(name, 2)
    chip = info.get("chip", "ESP32")
    fqbn = info.get("fqbn", "esp32:esp32:esp32")
    flash = info.get("flash_size", "4MB")
    BLINK_EXAMPLES[name] = f"""\
// Blink - {name} ({chip})
// Built-in LED on GPIO {pin}
// Board: {name} · Flash: {flash} · FQBN: {fqbn}
// BOARD: {name}
// FLASH_SIZE: {flash}

void setup() {{
  pinMode({pin}, OUTPUT);
}}

void loop() {{
  digitalWrite({pin}, HIGH);
  delay(500);
  digitalWrite({pin}, LOW);
  delay(500);
}}
"""

def get_blink_code(board_name: str) -> str:
    return BLINK_EXAMPLES.get(board_name, BLINK_EXAMPLES["ESP32 Dev Module"])

def get_led_pin(board_name: str) -> int:
    return LED_PINS.get(board_name, 2)
