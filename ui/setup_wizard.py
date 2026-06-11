from __future__ import annotations
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QStackedWidget, QFrame, QLineEdit,
)
from PyQt6.QtCore import Qt, pyqtSignal, QTimer, QSize
from PyQt6.QtGui import QPixmap

from palette import WARM_PASTEL as C
from constants import EASY_MODE_TITLE_FONT, EASY_MODE_BODY_FONT
from ui.animations import (
    PulsingWifi, BouncyMascot, AnimatedCheckmark, MascotProgressBar,
)
from discovery.usb import usb_probe, autodetect_port
from workers.usb_flash import UsbFlashWorker
from constants import APP_NAME

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
            self._next_btn.setEnabled(False)
            self._validate_wifi()
        elif step == 2:
            self._render_name_step()
            self._next_btn.setEnabled(True)
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
        if not password:
            self._flash_status.setText("A Wi-Fi password is required for security.")
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
        base_fw = Path(base) / "firmware" / "easyesp_base.bin"

        if not base_fw.exists():
            self._flash_status.setText("Base firmware not found. Reinstall EasyESP.")
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
