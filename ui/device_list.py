from __future__ import annotations
from PyQt6.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QLabel, QCheckBox
from PyQt6.QtCore import Qt, pyqtSignal

from models import Device
from palette import WARM_PASTEL as C
from ui.animations import BouncyMascot, BreathingDot


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
