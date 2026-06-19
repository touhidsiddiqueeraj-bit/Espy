"""Device details dialog — health telemetry + rollback + actions.

Opens when the user right-clicks a device (or selects "Device details…"
from the Device menu). Shows:
  - Name, IP, port, firmware version
  - RSSI signal strength (with color-coded bar)
  - Uptime, free heap, min free heap
  - Chip model, CPU freq, flash size
  - Running partition + next partition
  - Last reset reason
  - "Roll back firmware" button (POST /espy/rollback)
  - "Refresh" button to re-fetch health
"""
from __future__ import annotations
import time
from typing import Optional

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFrame, QGridLayout, QMessageBox, QSizePolicy,
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal

from palette import WARM_PASTEL as C
from models import Device
import device_api
from espy_logging import get_logger

_log = get_logger("ui.device_details")


class _HealthWorker(QThread):
    """Background thread that fetches /espy/health so we don't block the UI."""
    finished_ok    = pyqtSignal(dict)
    finished_error = pyqtSignal(str)

    def __init__(self, device: Device):
        super().__init__()
        self._device = device

    def run(self):
        try:
            data = device_api.fetch_health(self._device)
            self.finished_ok.emit(data)
        except device_api.DeviceAPIError as e:
            self.finished_error.emit(str(e))
        except Exception as e:
            self.finished_error.emit(f"Unexpected error: {e}")


class _RollbackWorker(QThread):
    """Background thread that POSTs /espy/rollback."""
    finished_ok    = pyqtSignal(str)  # message
    finished_error = pyqtSignal(str)  # message

    def __init__(self, device: Device):
        super().__init__()
        self._device = device

    def run(self):
        try:
            result = device_api.request_rollback(self._device)
            self.finished_ok.emit(
                "Rollback command accepted. The device is rebooting into the "
                "previous firmware. It should reappear in the sidebar within "
                "10-15 seconds."
            )
        except device_api.DeviceAPIError as e:
            self.finished_error.emit(str(e))
        except Exception as e:
            self.finished_error.emit(f"Unexpected error: {e}")


class DeviceDetailsDialog(QDialog):
    """Show device health + actions."""

    def __init__(self, device: Device, parent=None):
        super().__init__(parent)
        self._device = device
        self._health_worker: Optional[_HealthWorker] = None
        self._rollback_worker: Optional[_RollbackWorker] = None
        self.setWindowTitle(f"Device details — {device.name}")
        self.setMinimumSize(560, 600)
        self.setStyleSheet(f"background: {C['bg']}; color: {C['text']};")
        self._build_ui()
        # Auto-fetch health on open
        QTimer_singleShot(self, 100, self._refresh_health)

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(14)

        # ── Header ────────────────────────────────────────────
        title = QLabel(self._device.name)
        title.setStyleSheet(f"font-size: 22px; font-weight: 700; color: {C['text']};")
        layout.addWidget(title)
        sub = QLabel(f"{self._device.ip}:{self._device.port}  ·  firmware: {self._device.firmware_version}")
        sub.setStyleSheet(f"color: {C['text_muted']}; font-size: 13px;")
        layout.addWidget(sub)

        # ── Status line ───────────────────────────────────────
        self._status_label = QLabel("Fetching health…")
        self._status_label.setWordWrap(True)
        self._status_label.setStyleSheet(f"color: {C['text_muted']}; font-size: 13px;")
        layout.addWidget(self._status_label)

        # ── Health grid ───────────────────────────────────────
        self._grid_frame = QFrame()
        self._grid_frame.setStyleSheet(
            f"background: {C['card']}; border: 1px solid {C['border']}; border-radius: 10px;"
        )
        self._grid = QGridLayout(self._grid_frame)
        self._grid.setContentsMargins(18, 14, 18, 14)
        self._grid.setVerticalSpacing(10)
        self._grid.setHorizontalSpacing(18)
        layout.addWidget(self._grid_frame)

        # ── Signal strength bar ───────────────────────────────
        self._signal_label = QLabel("Signal strength:")
        self._signal_label.setStyleSheet(f"color: {C['text_muted']}; font-size: 13px;")
        layout.addWidget(self._signal_label)
        from PyQt6.QtWidgets import QProgressBar
        self._signal_bar = QProgressBar()
        self._signal_bar.setRange(0, 100)
        self._signal_bar.setTextVisible(True)
        self._signal_bar.setFormat("%v dBm")
        self._signal_bar.setFixedHeight(20)
        layout.addWidget(self._signal_bar)

        layout.addStretch()

        # ── Action buttons ────────────────────────────────────
        btn_row = QHBoxLayout()
        btn_row.setSpacing(8)
        refresh_btn = QPushButton("↻ Refresh")
        refresh_btn.setObjectName("secondary")
        refresh_btn.clicked.connect(self._refresh_health)
        btn_row.addWidget(refresh_btn)
        btn_row.addStretch()
        rollback_btn = QPushButton("↩ Roll back firmware")
        rollback_btn.setObjectName("danger")
        rollback_btn.setToolTip(
            "Revert to the previous OTA partition.\n\n"
            "Use this if the current firmware is broken.\n"
            "The device will reboot into the previous version."
        )
        rollback_btn.clicked.connect(self._confirm_rollback)
        btn_row.addWidget(rollback_btn)
        close_btn = QPushButton("Close")
        close_btn.setObjectName("ghost")
        close_btn.clicked.connect(self.accept)
        btn_row.addWidget(close_btn)
        layout.addLayout(btn_row)

    def _refresh_health(self):
        """Background-fetch /espy/health and update the UI."""
        if self._health_worker and self._health_worker.isRunning():
            return
        self._status_label.setText("Fetching health…")
        self._status_label.setStyleSheet(f"color: {C['text_muted']}; font-size: 13px;")
        self._health_worker = _HealthWorker(self._device)
        self._health_worker.finished_ok.connect(self._on_health_ok)
        self._health_worker.finished_error.connect(self._on_health_error)
        self._health_worker.start()

    def _on_health_ok(self, data: dict):
        """Populate the grid with health data."""
        # Clear previous grid contents
        self._clear_grid()

        rows = [
            ("Device name",     data.get("device", "?")),
            ("Firmware version", data.get("version", "?")),
            ("Uptime",          _format_uptime(data.get("uptime_ms", 0))),
            ("Free heap",       _format_bytes(data.get("free_heap_bytes", 0))),
            ("Min free heap",   _format_bytes(data.get("min_free_heap_bytes", 0))),
            ("Wi-Fi SSID",      data.get("wifi_ssid", "?")),
            ("IP address",      data.get("ip", "?")),
            ("Chip",            f"{data.get('chip_model', '?')} rev {data.get('chip_revision', '?')}"),
            ("CPU frequency",   f"{data.get('cpu_freq_mhz', '?')} MHz"),
            ("Flash size",      _format_bytes(data.get("flash_size_bytes", 0))),
            ("Sketch size",     _format_bytes(data.get("sketch_size_bytes", 0))),
            ("Free sketch",     _format_bytes(data.get("free_sketch_bytes", 0))),
            ("Running partition", data.get("running_partition", "?")),
            ("Next partition",    data.get("next_partition", "?")),
            ("Last reset",        data.get("last_reset_reason", "?")),
        ]
        for i, (k, v) in enumerate(rows):
            key_lbl = QLabel(k)
            key_lbl.setStyleSheet(f"color: {C['text_muted']}; font-size: 13px; background: transparent;")
            val_lbl = QLabel(str(v))
            val_lbl.setStyleSheet(f"color: {C['text']}; font-size: 13px; font-weight: 600; background: transparent;")
            self._grid.addWidget(key_lbl, i, 0)
            self._grid.addWidget(val_lbl, i, 1)

        # Signal strength
        rssi = data.get("rssi_dbm", -100)
        # Map RSSI (-100..-30) to 0..100
        pct = max(0, min(100, (rssi + 100) * 100 // 70))
        self._signal_bar.setRange(-100, -30)
        self._signal_bar.setValue(int(rssi))
        self._signal_bar.setFormat(f"{rssi} dBm  ({pct}%)")
        color = (C['success'] if rssi > -55
                 else C['warning'] if rssi > -70
                 else C['error'])
        self._signal_bar.setStyleSheet(
            f"QProgressBar::chunk {{ background: {color}; border-radius: 4px; }}"
        )

        self._status_label.setText("✓ Health data fresh.")
        self._status_label.setStyleSheet(f"color: {C['success']}; font-size: 13px;")

    def _on_health_error(self, msg: str):
        self._clear_grid()
        self._status_label.setText(f"⚠ {msg}")
        self._status_label.setStyleSheet(f"color: {C['error']}; font-size: 13px;")
        self._signal_bar.setRange(0, 100)
        self._signal_bar.setValue(0)
        self._signal_bar.setFormat("— dBm")

    def _clear_grid(self):
        while self._grid.count():
            item = self._grid.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

    def _confirm_rollback(self):
        """Ask for confirmation, then POST /espy/rollback."""
        reply = QMessageBox.question(
            self, "Confirm rollback",
            f"Roll back '{self._device.name}' to the previous firmware?\n\n"
            "The device will reboot into the previous OTA partition. "
            "It should reappear in the sidebar within 10-15 seconds.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.Cancel,
            QMessageBox.StandardButton.Cancel,
        )
        if reply != QMessageBox.StandardButton.Yes:
            return

        if self._rollback_worker and self._rollback_worker.isRunning():
            return
        self._status_label.setText("Sending rollback command…")
        self._status_label.setStyleSheet(f"color: {C['text_muted']}; font-size: 13px;")
        self._rollback_worker = _RollbackWorker(self._device)
        self._rollback_worker.finished_ok.connect(self._on_rollback_ok)
        self._rollback_worker.finished_error.connect(self._on_rollback_error)
        self._rollback_worker.start()

    def _on_rollback_ok(self, msg: str):
        self._status_label.setText(f"✓ {msg}")
        self._status_label.setStyleSheet(f"color: {C['success']}; font-size: 13px;")
        QMessageBox.information(
            self, "Rollback initiated",
            msg + "\n\nThe dialog will close. Watch the sidebar for the device to come back online.",
        )
        self.accept()

    def _on_rollback_error(self, msg: str):
        self._status_label.setText(f"⚠ {msg}")
        self._status_label.setStyleSheet(f"color: {C['error']}; font-size: 13px;")
        QMessageBox.critical(self, "Rollback failed", msg)


def _format_bytes(n: int) -> str:
    """Format a byte count human-readably."""
    try:
        n = int(n)
    except (TypeError, ValueError):
        return "?"
    for unit in ("B", "KB", "MB", "GB"):
        if n < 1024:
            return f"{n} {unit}"
        n //= 1024
    return f"{n} TB"


def _format_uptime(ms: int) -> str:
    """Format an uptime in milliseconds as 'Xd Yh Zm Ws'."""
    try:
        ms = int(ms)
    except (TypeError, ValueError):
        return "?"
    s = ms // 1000
    days, s = divmod(s, 86400)
    hours, s = divmod(s, 3600)
    mins, s = divmod(s, 60)
    if days:
        return f"{days}d {hours}h {mins}m"
    if hours:
        return f"{hours}h {mins}m {s}s"
    if mins:
        return f"{mins}m {s}s"
    return f"{s}s"


def QTimer_singleShot(parent, ms: int, callback):
    """Helper to avoid importing QTimer at module level in some places."""
    from PyQt6.QtCore import QTimer
    QTimer.singleShot(ms, callback)
