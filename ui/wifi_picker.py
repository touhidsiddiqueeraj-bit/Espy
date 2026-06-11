from __future__ import annotations
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QLineEdit, QComboBox, QFrame,
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QPixmap

from palette import WARM_PASTEL as C
from ui.animations import PulsingWifi, BouncyMascot


class WifiPicker(QWidget):
    wifi_selected = pyqtSignal(str, str)

    def __init__(self):
        super().__init__()
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setSpacing(14)

        # Animated wifi icon
        self._wifi = PulsingWifi()
        self._wifi.setFixedSize(120, 100)
        layout.addWidget(self._wifi, alignment=Qt.AlignmentFlag.AlignCenter)

        # Mascot
        self._mascot = BouncyMascot()
        self._mascot.set_mood("searching", 70)
        self._mascot.set_bounce_style("searching")
        self._mascot.start_bounce()
        self._mascot.setToolTip("I'm looking for Wi-Fi networks nearby!")
        layout.addWidget(self._mascot, alignment=Qt.AlignmentFlag.AlignCenter)

        title = QLabel("Connect to Wi-Fi")
        title.setStyleSheet(f"font-size: 24px; font-weight: 700; color: {C['text']};")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        self._ssid_combo = QComboBox()
        self._ssid_combo.setEditable(True)
        self._ssid_combo.setPlaceholderText("Select or type your network name")
        self._ssid_combo.setMinimumWidth(300)
        self._ssid_combo.setToolTip("Pick the Wi-Fi network your ESP32 should connect to")
        layout.addWidget(self._ssid_combo)

        self._password = QLineEdit()
        self._password.setEchoMode(QLineEdit.EchoMode.Password)
        self._password.setPlaceholderText("Wi-Fi password")
        self._password.setMinimumWidth(300)
        self._password.setToolTip("Your Wi-Fi password is saved on the ESP32, not your computer")
        layout.addWidget(self._password)

        btn = QPushButton("Connect →")
        btn.setObjectName("primary")
        btn.setMinimumWidth(220)
        btn.clicked.connect(self._emit)
        btn.setToolTip("Save these details to your ESP32")
        layout.addWidget(btn, alignment=Qt.AlignmentFlag.AlignCenter)

        # Expandable hint
        self._hint_btn = QPushButton("Why do I need this?")
        self._hint_btn.setObjectName("ghost")
        self._hint_btn.setToolTip("Click to learn more")
        self._hint_btn.clicked.connect(self._toggle_hint)
        layout.addWidget(self._hint_btn, alignment=Qt.AlignmentFlag.AlignCenter)

        self._hint = QLabel(
            "Your ESP32 connects to your home Wi-Fi so it can receive "
            "wireless updates. The password is stored on the ESP32, "
            "not on your computer."
        )
        self._hint.setWordWrap(True)
        self._hint.setMaximumWidth(360)
        self._hint.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._hint.setStyleSheet(f"color: {C['text_faint']}; font-size: 15px;")
        self._hint.hide()
        layout.addWidget(self._hint, alignment=Qt.AlignmentFlag.AlignCenter)

    def _toggle_hint(self):
        self._hint.setVisible(not self._hint.isVisible())
        self._hint_btn.setText("Hide" if self._hint.isVisible() else "Why do I need this?")
        if self._hint.isVisible():
            self._mascot.set_mood("happy", 70)

    def _emit(self):
        ssid = self._ssid_combo.currentText().strip()
        password = self._password.text()
        if ssid:
            self.wifi_selected.emit(ssid, password)
