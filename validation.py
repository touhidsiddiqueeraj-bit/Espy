"""Pre-flash validation — catch problems BEFORE they brick a remote device.

Checks performed on the InoConfig + source code:
  1. Board is in the supported BOARDS list
  2. WiFi SSID and password are non-empty
  3. Sketch size fits the board's max_sketch_size (if known)
  4. No use of strapping pins (GPIO 0/2/12/15) as outputs
  5. No `delay()` > 5000ms in loop()
  6. No `while(true)` without yield/delay (would starve OTA task)
  7. No known conflicting libraries (ArduinoOTA + Espy's built-in OTA)
  8. Device name is set (or will fall back to "Unknown")
"""
from __future__ import annotations
import re
from dataclasses import dataclass, field
from typing import Literal

from constants import BOARDS
from models import InoConfig
from espy_logging import get_logger

_log = get_logger("validation")

# GPIO strapping pins on ESP32 — using these as outputs can prevent boot.
STRAPPING_PINS_ESP32 = {0, 2, 12, 15}
STRAPPING_PINS_ESP32_S3 = {0, 3, 45, 46}
STRAPPING_PINS_ESP32_C3 = {2, 8, 9}
STRAPPING_PINS_ESP32_H2 = {}  # not a concern on H2


@dataclass
class ValidationIssue:
    severity: Literal["error", "warning", "info"]
    code: str        # short identifier, e.g. "strapping_pin"
    message: str
    fix_hint: str = ""


@dataclass
class ValidationResult:
    issues: list[ValidationIssue] = field(default_factory=list)

    @property
    def has_errors(self) -> bool:
        return any(i.severity == "error" for i in self.issues)

    @property
    def has_warnings(self) -> bool:
        return any(i.severity == "warning" for i in self.issues)

    @property
    def can_flash(self) -> bool:
        """True if no errors block flashing."""
        return not self.has_errors


def validate(cfg: InoConfig, source: str = "") -> ValidationResult:
    """Run all pre-flash checks. Returns a ValidationResult."""
    result = ValidationResult()
    source = source or cfg.raw_content

    # 1. Board supported
    if cfg.board not in BOARDS:
        result.issues.append(ValidationIssue(
            severity="error",
            code="unsupported_board",
            message=f"Board '{cfg.board}' is not in the supported list.",
            fix_hint="Choose one of: " + ", ".join(list(BOARDS.keys())[:5]) + ", …"
        ))

    # 2. WiFi credentials
    if not cfg.wifi_ssid:
        result.issues.append(ValidationIssue(
            severity="error",
            code="missing_ssid",
            message="Wi-Fi SSID is empty — the device won't be able to join your network.",
            fix_hint="Add `// WIFI_SSID: YourNetwork` to the top of your sketch, "
                     "or fill it in the config dialog."
        ))
    if not cfg.wifi_password:
        # Warning, not error — open networks exist
        result.issues.append(ValidationIssue(
            severity="warning",
            code="empty_password",
            message="Wi-Fi password is empty. This is fine for open networks, "
                    "but most home networks require one.",
        ))

    # 3. Sketch size (only if we know it)
    board_info = BOARDS.get(cfg.board, {})
    max_size = board_info.get("max_sketch_size")
    if max_size and cfg.bin_size_bytes > 0:
        pct = (cfg.bin_size_bytes / max_size) * 100
        if cfg.bin_size_bytes > max_size:
            result.issues.append(ValidationIssue(
                severity="error",
                code="sketch_too_large",
                message=f"Sketch is {cfg.bin_size_bytes:,} bytes but the board's "
                        f"max app size is {max_size:,} bytes ({pct:.0f}%).",
                fix_hint="Remove unused libraries, simplify logic, or use a board "
                         "with more flash (e.g. ESP32-S3 with 16MB)."
            ))
        elif pct > 85:
            result.issues.append(ValidationIssue(
                severity="warning",
                code="sketch_near_limit",
                message=f"Sketch uses {pct:.0f}% of available flash "
                        f"({cfg.bin_size_bytes:,} / {max_size:,} bytes). "
                        "Future updates may not fit.",
            ))

    # 4. Strapping pins — scan source for pinMode(N, OUTPUT) where N is strapping
    if source:
        _check_strapping_pins(cfg, source, result)
        _check_blocking_loop(source, result)
        _check_ota_conflict(cfg, source, result)

    # 5. Device name
    if not cfg.device_name:
        result.issues.append(ValidationIssue(
            severity="info",
            code="no_device_name",
            message="No device name set. The device will appear as 'Unknown' in Espy.",
            fix_hint="Add `// DEVICE_NAME: Kitchen Light` to the top of your sketch."
        ))

    return result


def _check_strapping_pins(cfg: InoConfig, source: str, result: ValidationResult):
    """Flag use of strapping pins as outputs."""
    chip = BOARDS.get(cfg.board, {}).get("chip", "ESP32")
    if "S3" in chip:
        strapping = STRAPPING_PINS_ESP32_S3
    elif "C3" in chip:
        strapping = STRAPPING_PINS_ESP32_C3
    elif "H2" in chip:
        strapping = STRAPPING_PINS_ESP32_H2
    else:
        strapping = STRAPPING_PINS_ESP32

    if not strapping:
        return

    # Match pinMode(0, OUTPUT) or pinMode(0, OUTPUT_OPEN_DRAIN)
    pattern = re.compile(
        r"pinMode\s*\(\s*(\d+)\s*,\s*(OUTPUT[_A-Z]*)\s*\)",
        re.IGNORECASE,
    )
    for match in pattern.finditer(source):
        pin = int(match.group(1))
        mode = match.group(2).upper()
        if pin in strapping and "OUTPUT" in mode:
            result.issues.append(ValidationIssue(
                severity="error",
                code="strapping_pin",
                message=f"GPIO {pin} is a strapping pin and is being used as OUTPUT "
                        f"({mode}). This can prevent the ESP32 from booting.",
                fix_hint=f"Use a different pin. On {chip}, avoid: "
                         + ", ".join(f"GPIO {p}" for p in sorted(strapping))
            ))


def _check_blocking_loop(source: str, result: ValidationResult):
    """Flag long delay() calls and bare while(true) loops in the sketch."""
    # delay(N) where N > 5000 — would block the OTA task
    for match in re.finditer(r"delay\s*\(\s*(\d+)\s*\)", source):
        ms = int(match.group(1))
        if ms > 5000:
            result.issues.append(ValidationIssue(
                severity="warning",
                code="long_delay",
                message=f"delay({ms}) is longer than 5 seconds. "
                        "Long delays block the OTA task and may make the device "
                        "unresponsive to future updates.",
                fix_hint="Split into multiple shorter delays, or use millis()-based timing."
            ))

    # while(true) without delay/yield inside — would starve OTA task
    # Simple heuristic: find while(true) { ... } blocks
    for match in re.finditer(r"while\s*\(\s*(?:true|1)\s*\)\s*\{([^}]*)\}", source):
        body = match.group(1)
        if "delay" not in body.lower() and "yield" not in body.lower():
            result.issues.append(ValidationIssue(
                severity="warning",
                code="blocking_loop",
                message="Found `while(true) { ... }` without delay() or yield(). "
                        "This will starve the OTA task and prevent future wireless updates.",
                fix_hint="Add `delay(1);` or `yield();` inside the loop."
            ))


def _check_ota_conflict(cfg: InoConfig, source: str, result: ValidationResult):
    """Flag ArduinoOTA usage — conflicts with Espy's built-in OTA."""
    if "ArduinoOTA" in source or "ArduinoOTA.h" in source:
        cfg.has_ota_conflict = True  # set so ConfigDialog shows the existing warning
        result.issues.append(ValidationIssue(
            severity="error",
            code="ota_conflict",
            message="Sketch uses ArduinoOTA, which conflicts with Espy's built-in OTA.",
            fix_hint="Remove `#include <ArduinoOTA.h>` and all ArduinoOTA.* calls. "
                     "Espy provides OTA for you."
        ))


def format_result(result: ValidationResult) -> str:
    """Render a ValidationResult as a human-readable string for dialogs."""
    if not result.issues:
        return "✓ All checks passed. Safe to flash."
    lines = []
    errors = [i for i in result.issues if i.severity == "error"]
    warnings = [i for i in result.issues if i.severity == "warning"]
    infos = [i for i in result.issues if i.severity == "info"]
    if errors:
        lines.append(f"⛔ {len(errors)} error(s) — flashing is BLOCKED:")
        for i in errors:
            lines.append(f"  • [{i.code}] {i.message}")
            if i.fix_hint:
                lines.append(f"      → {i.fix_hint}")
    if warnings:
        lines.append(f"\n⚠ {len(warnings)} warning(s):")
        for i in warnings:
            lines.append(f"  • [{i.code}] {i.message}")
            if i.fix_hint:
                lines.append(f"      → {i.fix_hint}")
    if infos:
        lines.append(f"\nℹ {len(infos)} note(s):")
        for i in infos:
            lines.append(f"  • [{i.code}] {i.message}")
    return "\n".join(lines)
