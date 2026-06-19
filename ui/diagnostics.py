"""Network + device diagnostics dialogs.

Contains:
  - NetworkDiagnosticsDialog: runs live checks to help diagnose
    "why isn't my device showing up?"
  - ManualDeviceEntryDialog: escape hatch for hostile networks —
    type IP:port and probe directly
  - SendHeartbeatDialog: broadcasts a fake heartbeat for UI testing
    without real hardware
  - CrashLogDecoderDialog: paste an ESP32 panic backtrace, get
    function names via addr2line on the last build's ELF
"""
from __future__ import annotations
import json
import os
import re
import socket
import subprocess
import sys
import threading
import time
import urllib.request
from pathlib import Path
from typing import Optional

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QLineEdit, QTextEdit, QComboBox, QProgressBar, QFrame,
    QMessageBox, QSizePolicy, QGroupBox, QFormLayout,
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QTimer

from palette import WARM_PASTEL as C
from constants import HEARTBEAT_PORT, OTA_PORT, APP_VERSION, BOARDS
from espy_logging import get_logger

_log = get_logger("ui.diagnostics")


# ─────────────────────────────────────────────────────────────
#  Shared network probe helpers
# ─────────────────────────────────────────────────────────────

def _local_ip() -> str:
    """Best-effort local IP address (used to determine subnet)."""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except OSError:
        return "127.0.0.1"


def _probe_alive(ip: str, port: int = OTA_PORT, timeout: float = 1.5) -> tuple[bool, str]:
    """TCP-connect to ip:port. Returns (alive, message)."""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        result = sock.connect_ex((ip, port))
        sock.close()
        if result == 0:
            return True, f"Connected to {ip}:{port}"
        return False, f"Connection refused on port {port} (errno {result})"
    except OSError as e:
        return False, f"Network error: {e}"


def _probe_heartbeat_endpoint(ip: str, port: int = OTA_PORT, timeout: float = 2.0) -> tuple[bool, dict | None, str]:
    """GET /espy/alive — returns (ok, payload, message)."""
    try:
        req = urllib.request.Request(
            f"http://{ip}:{port}/espy/alive",
            method="GET",
        )
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            return True, data, f"OK — {data}"
    except Exception as e:
        return False, None, f"HTTP probe failed: {e}"


# ─────────────────────────────────────────────────────────────
#  Network diagnostics
# ─────────────────────────────────────────────────────────────

class NetworkDiagnosticsDialog(QDialog):
    """Run a battery of network checks and show the results.

    Turns the "why isn't my device showing up?" mystery into a
    5-second answer: am I on the right subnet? Is the port open?
    Is the device even alive? Is the firewall blocking broadcasts?
    """

    def __init__(self, parent=None, known_devices: list[dict] | None = None):
        super().__init__(parent)
        self.setWindowTitle("Network Diagnostics")
        self.setMinimumSize(640, 560)
        self.setStyleSheet(f"background: {C['bg']}; color: {C['text']};")
        self._known = known_devices or []
        self._build_ui()
        # Run checks automatically on open
        QTimer.singleShot(100, self._run_all_checks)

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(12)

        title = QLabel("Network Diagnostics")
        title.setStyleSheet(f"font-size: 20px; font-weight: 700; color: {C['text']};")
        layout.addWidget(title)

        sub = QLabel(
            "Running live checks to figure out why devices aren't appearing. "
            "Each line shows what was tested and the result."
        )
        sub.setWordWrap(True)
        sub.setStyleSheet(f"color: {C['text_muted']}; font-size: 13px;")
        layout.addWidget(sub)

        # Results panel
        self._results = QTextEdit()
        self._results.setReadOnly(True)
        self._results.setStyleSheet(
            f"background: {C['card']}; color: {C['text']}; "
            f"border: 1px solid {C['border']}; border-radius: 8px; "
            f"padding: 12px; font-family: 'Consolas', monospace; font-size: 13px;"
        )
        layout.addWidget(self._results, 1)

        # Progress
        self._progress = QProgressBar()
        self._progress.setRange(0, 5)
        self._progress.setValue(0)
        layout.addWidget(self._progress)

        # Buttons
        btn_row = QHBoxLayout()
        btn_row.addStretch()
        rerun_btn = QPushButton("Re-run checks")
        rerun_btn.setObjectName("primary")
        rerun_btn.clicked.connect(self._run_all_checks)
        btn_row.addWidget(rerun_btn)
        close_btn = QPushButton("Close")
        close_btn.setObjectName("secondary")
        close_btn.clicked.connect(self.accept)
        btn_row.addWidget(close_btn)
        layout.addLayout(btn_row)

    def _append(self, status: str, msg: str):
        """Append one line to the results panel. status: ok/warn/err."""
        icons = {"ok": "✓", "warn": "⚠", "err": "✗", "info": "•"}
        colors = {
            "ok":   C['success'],
            "warn": C['warning'],
            "err":  C['error'],
            "info": C['text_muted'],
        }
        icon = icons.get(status, "•")
        color = colors.get(status, C['text'])
        # Plain text — colors don't render in QTextEdit without HTML
        self._results.append(f"{icon}  {msg}")
        # Also log to file
        if status == "err":
            _log.error("diagnostics: %s", msg)
        elif status == "warn":
            _log.warning("diagnostics: %s", msg)
        else:
            _log.info("diagnostics: %s", msg)
        self._results.verticalScrollBar().setValue(
            self._results.verticalScrollBar().maximum()
        )
        QApplication_processEvents_safe()

    def _set_progress(self, n: int):
        self._progress.setValue(n)
        QApplication_processEvents_safe()

    def _run_all_checks(self):
        self._results.clear()
        self._set_progress(0)
        self._append("info", "Starting diagnostics…")

        # 1. Local IP / subnet
        local = _local_ip()
        self._append("info", f"Your IP: {local}")
        if local.startswith("127."):
            self._append("err", "  → You appear to be on loopback. Connect to Wi-Fi/Ethernet first.")
        else:
            self._append("ok", f"  → Local network interface OK")
        self._set_progress(1)

        # 2. UDP port 7777 bind check
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            s.bind(("", HEARTBEAT_PORT))
            s.close()
            self._append("ok", f"UDP port {HEARTBEAT_PORT} is available for listening")
        except OSError as e:
            self._append("err", f"Cannot bind UDP port {HEARTBEAT_PORT}: {e}")
            self._append("warn", "  → Another Espy instance may be running, or the firewall is blocking it.")
        self._set_progress(2)

        # 3. Probe each known device
        if not self._known:
            self._append("info", "No known devices to probe yet.")
        else:
            for dev in self._known:
                ip = dev.get("ip") or dev.get("last_known_ip", "")
                port = dev.get("port", OTA_PORT)
                name = dev.get("name", "Unknown")
                if not ip:
                    continue
                ok, msg = _probe_alive(ip, port, timeout=2)
                if ok:
                    self._append("ok", f"Device '{name}' @ {ip}:{port} is reachable")
                    # Also try the HTTP heartbeat endpoint
                    http_ok, payload, http_msg = _probe_heartbeat_endpoint(ip, port)
                    if http_ok:
                        self._append("ok", f"  → /espy/alive responded: {payload}")
                    else:
                        self._append("warn", f"  → /espy/alive failed: {http_msg}")
                else:
                    self._append("err", f"Device '{name}' @ {ip}:{port} unreachable: {msg}")
        self._set_progress(3)

        # 4. Subnet sanity — if any known device's IP isn't on our subnet, warn
        if local and not local.startswith("127.") and self._known:
            my_parts = local.split(".")
            for dev in self._known:
                ip = dev.get("ip") or dev.get("last_known_ip", "")
                if not ip:
                    continue
                parts = ip.split(".")
                if parts[0:3] != my_parts[0:3]:
                    self._append("warn",
                        f"Device {ip} is on a different subnet than you ({local}). "
                        "UDP broadcasts don't cross routers — that's likely why discovery isn't finding it.")
                    break
            else:
                self._append("ok", "All known devices are on your subnet")
        self._set_progress(4)

        # 5. Firewall hint
        self._append("info", "Firewall hint: ensure Windows Firewall allows UDP inbound on port "
                              f"{HEARTBEAT_PORT} for python.exe / Espy.exe.")
        self._set_progress(5)
        self._append("info", "Diagnostics complete. See espy_debug.log for full details.")


def QApplication_processEvents_safe():
    """Process Qt events without circular-importing QApplication."""
    from PyQt6.QtWidgets import QApplication
    QApplication.processEvents()


# ─────────────────────────────────────────────────────────────
#  Manual device entry
# ─────────────────────────────────────────────────────────────

class ManualDeviceEntryDialog(QDialog):
    """Escape hatch for hostile networks — type IP:port, probe directly.

    If discovery is failing (corporate Wi-Fi, AP isolation, VPN),
    users can manually enter a device's IP and port. We probe it
    immediately and return the result on accept.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Add Device Manually")
        self.setMinimumWidth(500)
        self.setStyleSheet(f"background: {C['bg']}; color: {C['text']};")
        self.result_device: Optional[tuple[str, str, int]] = None  # (name, ip, port)
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(12)

        title = QLabel("Add Device Manually")
        title.setStyleSheet(f"font-size: 20px; font-weight: 700; color: {C['text']};")
        layout.addWidget(title)

        sub = QLabel(
            "If discovery isn't finding your device (corporate Wi-Fi, AP isolation, "
            "different subnet), enter its IP address and OTA port here. "
            "Espy will probe it directly."
        )
        sub.setWordWrap(True)
        sub.setStyleSheet(f"color: {C['text_muted']}; font-size: 13px;")
        layout.addWidget(sub)

        form = QFormLayout()
        form.setSpacing(10)
        self._ip_edit = QLineEdit()
        self._ip_edit.setPlaceholderText("e.g. 192.168.1.42")
        self._port_edit = QLineEdit(str(OTA_PORT))
        self._port_edit.setPlaceholderText(str(OTA_PORT))
        self._name_edit = QLineEdit()
        self._name_edit.setPlaceholderText("e.g. Kitchen Light (optional)")
        form.addRow("IP address", self._ip_edit)
        form.addRow("OTA port", self._port_edit)
        form.addRow("Device name", self._name_edit)
        layout.addLayout(form)

        self._probe_result = QLabel("")
        self._probe_result.setWordWrap(True)
        self._probe_result.setStyleSheet(f"color: {C['text_muted']}; font-size: 12px;")
        layout.addWidget(self._probe_result)

        btn_row = QHBoxLayout()
        btn_row.addStretch()
        probe_btn = QPushButton("Probe")
        probe_btn.setObjectName("secondary")
        probe_btn.clicked.connect(self._probe)
        btn_row.addWidget(probe_btn)
        add_btn = QPushButton("Add device")
        add_btn.setObjectName("primary")
        add_btn.clicked.connect(self._accept)
        btn_row.addWidget(add_btn)
        cancel_btn = QPushButton("Cancel")
        cancel_btn.setObjectName("ghost")
        cancel_btn.clicked.connect(self.reject)
        btn_row.addWidget(cancel_btn)
        layout.addLayout(btn_row)

    def _probe(self):
        ip = self._ip_edit.text().strip()
        port_text = self._port_edit.text().strip() or str(OTA_PORT)
        if not ip:
            self._probe_result.setText("Enter an IP address first.")
            self._probe_result.setStyleSheet(f"color: {C['error']}; font-size: 12px;")
            return
        try:
            port = int(port_text)
        except ValueError:
            self._probe_result.setText(f"Port must be a number, got {port_text!r}.")
            self._probe_result.setStyleSheet(f"color: {C['error']}; font-size: 12px;")
            return

        self._probe_result.setText("Probing…")
        self._probe_result.setStyleSheet(f"color: {C['text_muted']}; font-size: 12px;")
        QApplication_processEvents_safe()

        ok, msg = _probe_alive(ip, port, timeout=2.5)
        if ok:
            # Also try to fetch the device name from /espy/alive
            http_ok, payload, _ = _probe_heartbeat_endpoint(ip, port, timeout=2.5)
            if http_ok and payload:
                name = payload.get("device", "")
                if name and not self._name_edit.text().strip():
                    self._name_edit.setText(name)
            self._probe_result.setText(f"✓ Reachable — {msg}")
            self._probe_result.setStyleSheet(f"color: {C['success']}; font-size: 12px;")
        else:
            self._probe_result.setText(f"✗ {msg}")
            self._probe_result.setStyleSheet(f"color: {C['error']}; font-size: 12px;")

    def _accept(self):
        ip = self._ip_edit.text().strip()
        port_text = self._port_edit.text().strip() or str(OTA_PORT)
        name = self._name_edit.text().strip() or f"Device at {ip}"
        if not ip:
            QMessageBox.warning(self, "Missing IP", "Please enter the device's IP address.")
            return
        try:
            port = int(port_text)
        except ValueError:
            QMessageBox.warning(self, "Bad port", f"Port must be a number, got {port_text!r}.")
            return
        self.result_device = (name, ip, port)
        self.accept()


# ─────────────────────────────────────────────────────────────
#  Send-heartbeat debug button
# ─────────────────────────────────────────────────────────────

class SendHeartbeatDialog(QDialog):
    """Broadcast a fake ESP32 heartbeat for UI testing without hardware.

    Useful for: developing UI changes, reproducing discovery bugs,
    demoing the app, testing the device-list rendering.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Send Test Heartbeat")
        self.setMinimumWidth(460)
        self.setStyleSheet(f"background: {C['bg']}; color: {C['text']};")
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(12)

        title = QLabel("Send Test Heartbeat")
        title.setStyleSheet(f"font-size: 20px; font-weight: 700; color: {C['text']};")
        layout.addWidget(title)

        sub = QLabel(
            "Broadcasts a fake ESP32 heartbeat on UDP port "
            f"{HEARTBEAT_PORT}. Useful for testing the UI without real hardware."
        )
        sub.setWordWrap(True)
        sub.setStyleSheet(f"color: {C['text_muted']}; font-size: 13px;")
        layout.addWidget(sub)

        form = QFormLayout()
        form.setSpacing(10)
        self._name_edit = QLineEdit("Test Device")
        self._port_edit = QLineEdit(str(OTA_PORT))
        self._count_spin = QLineEdit("3")
        self._count_spin.setToolTip("How many heartbeats to send (1 every second)")
        form.addRow("Device name", self._name_edit)
        form.addRow("OTA port", self._port_edit)
        form.addRow("Heartbeats to send", self._count_spin)
        layout.addLayout(form)

        self._status = QLabel("")
        self._status.setWordWrap(True)
        self._status.setStyleSheet(f"color: {C['text_muted']}; font-size: 12px;")
        layout.addWidget(self._status)

        btn_row = QHBoxLayout()
        btn_row.addStretch()
        send_btn = QPushButton("Send")
        send_btn.setObjectName("primary")
        send_btn.clicked.connect(self._send)
        btn_row.addWidget(send_btn)
        close_btn = QPushButton("Close")
        close_btn.setObjectName("ghost")
        close_btn.clicked.connect(self.accept)
        btn_row.addWidget(close_btn)
        layout.addLayout(btn_row)

    def _send(self):
        name = self._name_edit.text().strip() or "Test Device"
        try:
            port = int(self._port_edit.text().strip() or str(OTA_PORT))
        except ValueError:
            port = OTA_PORT
        try:
            count = max(1, min(20, int(self._count_spin.text().strip() or "1")))
        except ValueError:
            count = 3

        # Send `count` heartbeats in a background thread (1 per second)
        def worker():
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
            payload = json.dumps({
                "device": name,
                "ota_port": port,
                "version": "test_v1.0",
            }).encode("utf-8")
            for i in range(count):
                try:
                    sock.sendto(payload, ("255.255.255.255", HEARTBEAT_PORT))
                    _log.info("Sent test heartbeat %d/%d for %r", i + 1, count, name)
                    # Update status from main thread
                    QTimer.singleShot(0, lambda i=i, c=count: self._status.setText(
                        f"Sent {i+1}/{c} heartbeats for '{name}'…"
                    ))
                except OSError as e:
                    _log.error("Failed to send test heartbeat: %s", e)
                    QTimer.singleShot(0, lambda e=e: self._status.setText(
                        f"✗ Failed: {e}"
                    ))
                    break
                time.sleep(1.0)
            sock.close()
            QTimer.singleShot(0, lambda: self._status.setText(
                f"✓ Sent {count} heartbeat(s). The device should appear in the sidebar."
            ))

        threading.Thread(target=worker, daemon=True).start()
        self._status.setText("Sending…")


# ─────────────────────────────────────────────────────────────
#  Crash log decoder
# ─────────────────────────────────────────────────────────────

class CrashLogDecoderDialog(QDialog):
    """Decode an ESP32 panic backtrace into function names.

    ESP32 panics produce stack traces with raw addresses like:
        0x400D1234 0x400D0F22 0x400D2A1B
    Paste them here, point at the .elf file from the last build,
    and we'll shell out to addr2line to resolve them.
    """

    def __init__(self, parent=None, elf_path: str = "", last_build_dir: str = ""):
        super().__init__(parent)
        self.setWindowTitle("Crash Log Decoder")
        self.setMinimumSize(700, 560)
        self.setStyleSheet(f"background: {C['bg']}; color: {C['text']};")
        self._elf_path = elf_path
        self._last_build_dir = last_build_dir
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(12)

        title = QLabel("Crash Log Decoder")
        title.setStyleSheet(f"font-size: 20px; font-weight: 700; color: {C['text']};")
        layout.addWidget(title)

        sub = QLabel(
            "Paste an ESP32 panic backtrace (the long string of 0x addresses), "
            "point at the .elf file from your last build, and Espy will resolve "
            "each address to a function name + line number using addr2line."
        )
        sub.setWordWrap(True)
        sub.setStyleSheet(f"color: {C['text_muted']}; font-size: 13px;")
        layout.addWidget(sub)

        # ELF file picker
        elf_row = QHBoxLayout()
        elf_lbl = QLabel("ELF file:")
        elf_lbl.setStyleSheet(f"color: {C['text_muted']};")
        elf_row.addWidget(elf_lbl)
        self._elf_edit = QLineEdit(self._elf_path)
        self._elf_edit.setPlaceholderText("/path/to/sketch.ino.elf")
        elf_row.addWidget(self._elf_edit, 1)
        browse_btn = QPushButton("Browse…")
        browse_btn.setObjectName("secondary")
        browse_btn.clicked.connect(self._browse_elf)
        elf_row.addWidget(browse_btn)
        layout.addLayout(elf_row)

        # Auto-find button (looks in standard Arduino build dirs)
        if self._last_build_dir:
            auto_btn = QPushButton(f"Try last build: {Path(self._last_build_dir).name}")
            auto_btn.setObjectName("ghost")
            auto_btn.clicked.connect(lambda: self._auto_find_elf(self._last_build_dir))
            layout.addWidget(auto_btn)

        # Backtrace input
        layout.addWidget(QLabel("Paste backtrace:"))
        self._input = QTextEdit()
        self._input.setPlaceholderText(
            "Example:\n"
            "0x400D1234 0x400D0F22 0x400D2A1B\n"
            "or: Guru Meditation Error: Core 0 panic'ed (LoadProhibited). "
            "Exception was unhandled.\nA0      0x800d3c4d  ..."
        )
        self._input.setStyleSheet(
            f"background: {C['card']}; color: {C['text']}; "
            f"border: 1px solid {C['border']}; border-radius: 8px; "
            f"padding: 8px; font-family: 'Consolas', monospace; font-size: 12px;"
        )
        layout.addWidget(self._input, 1)

        # Output
        layout.addWidget(QLabel("Decoded:"))
        self._output = QTextEdit()
        self._output.setReadOnly(True)
        self._output.setStyleSheet(
            f"background: {C['card']}; color: {C['text']}; "
            f"border: 1px solid {C['border']}; border-radius: 8px; "
            f"padding: 8px; font-family: 'Consolas', monospace; font-size: 12px;"
        )
        layout.addWidget(self._output, 1)

        # Buttons
        btn_row = QHBoxLayout()
        btn_row.addStretch()
        decode_btn = QPushButton("Decode")
        decode_btn.setObjectName("primary")
        decode_btn.clicked.connect(self._decode)
        btn_row.addWidget(decode_btn)
        close_btn = QPushButton("Close")
        close_btn.setObjectName("ghost")
        close_btn.clicked.connect(self.accept)
        btn_row.addWidget(close_btn)
        layout.addLayout(btn_row)

    def _browse_elf(self):
        from PyQt6.QtWidgets import QFileDialog
        path, _ = QFileDialog.getOpenFileName(
            self, "Choose ELF file", "",
            "ELF files (*.elf);;All Files (*)"
        )
        if path:
            self._elf_edit.setText(path)

    def _auto_find_elf(self, build_dir: str):
        """Look for *.ino.elf in the standard Arduino build directory."""
        # Arduino CLI puts build artifacts under:
        #   /tmp/arduino/sketches/<HASH>/<SKETCH>.ino.elf
        # On Windows: %TEMP%\arduino\sketches\<HASH>\<SKETCH>.ino.elf
        candidates = []
        try:
            base = Path(build_dir)
            if base.is_dir():
                candidates = list(base.rglob("*.ino.elf")) + list(base.rglob("*.elf"))
        except Exception:
            pass

        # Also check standard temp locations
        for tmp in [Path("/tmp"), Path(os.environ.get("TEMP", "/tmp")),
                    Path(os.environ.get("TMP", "/tmp"))]:
            try:
                if tmp.is_dir():
                    candidates.extend(tmp.rglob("arduino/sketches/*/*.ino.elf"))
            except Exception:
                pass

        if not candidates:
            self._output.setText("No .elf files found in standard build directories.")
            return

        # Pick the most recently modified
        candidates.sort(key=lambda p: p.stat().st_mtime, reverse=True)
        self._elf_edit.setText(str(candidates[0]))
        self._output.setText(f"Using most recent build:\n  {candidates[0]}\n\nClick Decode to resolve addresses.")

    def _extract_addresses(self, text: str) -> list[str]:
        """Pull all 0x[0-9a-fA-F]{8} addresses out of arbitrary text."""
        return re.findall(r"0x[0-9a-fA-F]{8}", text)

    def _find_addr2line(self) -> Optional[str]:
        """Locate addr2line — either in Arduino's bundled toolchain or PATH."""
        # 1. PATH (Linux/macOS)
        for name in ("addr2line", "xtensa-esp32-elf-addr2line"):
            path = _which(name)
            if path:
                return path
        # 2. Arduino's bundled toolchain (Windows)
        candidates = [
            Path.home() / "AppData/Local/Arduino15/packages/esp32/tools/xtensa-esp32-elf-gcc",
        ]
        for base in candidates:
            if base.is_dir():
                for exe in base.rglob("*/addr2line.exe"):
                    return str(exe)
        return None

    def _decode(self):
        elf = self._elf_edit.text().strip()
        addrs = self._extract_addresses(self._input.toPlainText())
        if not elf:
            self._output.setText("✗ Please choose an ELF file.")
            return
        if not os.path.isfile(elf):
            self._output.setText(f"✗ ELF file not found: {elf}")
            return
        if not addrs:
            self._output.setText("✗ No addresses (0x…) found in the backtrace text.")
            return

        addr2line = self._find_addr2line()
        if not addr2line:
            self._output.setText(
                "✗ addr2line not found.\n"
                "Install the ESP32 Arduino core (Tools → Board → Boards Manager → esp32), "
                "or install binutils on Linux/macOS."
            )
            return

        self._output.setText(f"Resolving {len(addrs)} address(es) using {addr2line}…")
        QApplication_processEvents_safe()

        try:
            cmd = [addr2line, "-f", "-p", "-C", "-e", elf] + addrs
            result = subprocess.run(
                cmd, capture_output=True, text=True, timeout=30,
            )
            if result.returncode != 0:
                self._output.setText(
                    f"✗ addr2line failed (exit {result.returncode}):\n{result.stderr}"
                )
                return
            lines = result.stdout.strip().splitlines()
            out_lines = ["Address          Function / File:Line", "─" * 60]
            for addr, line in zip(addrs, lines):
                out_lines.append(f"{addr}  {line}")
            self._output.setText("\n".join(out_lines))
        except subprocess.TimeoutExpired:
            self._output.setText("✗ addr2line timed out after 30 seconds.")
        except Exception as e:
            self._output.setText(f"✗ Error running addr2line: {e}")


def _which(name: str) -> Optional[str]:
    """Cross-platform which()."""
    from shutil import which
    return which(name)
