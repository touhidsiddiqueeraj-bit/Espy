from __future__ import annotations
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QProgressBar, QApplication,
)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from PyQt6.QtGui import QPixmap

from palette import WARM_PASTEL as C
from constants import EASY_MODE_TITLE_FONT as T, EASY_MODE_BODY_FONT as B
from ui.animations import (
    BouncyMascot, LoadingDots, ConfettiWidget, AnimatedCheckmark,
    MascotProgressBar,
)


class StepDot(QLabel):
    def __init__(self, label: str, parent=None):
        super().__init__(parent)
        self.setText("○")
        self._label = label
        self.set_active(False)

    def set_active(self, active: bool):
        self.setText("●" if active else "○")
        color = C['accent'] if active else C['text_faint']
        self.setStyleSheet(f"font-size: 24px; color: {color};")

    def set_done(self):
        self.setText("✓")
        self.setStyleSheet(f"font-size: 24px; color: {C['success']};")


class ProgressScene(QWidget):
    save_binary_requested = pyqtSignal(str)
    flash_now_requested = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self._mascot = BouncyMascot()
        self._title = QLabel()
        self._status = QLabel()
        self._bar = MascotProgressBar()
        self._back_btn = QPushButton("← Back")
        self._error_detail_btn = QPushButton("Copy for AI assistant")
        self._save_btn = QPushButton("Save Binary")
        self._flash_btn = QPushButton("Flash Now")
        self._step_dots: list[StepDot] = []
        self._confetti = ConfettiWidget()
        self._loading_dots = LoadingDots()
        self._checkmark = AnimatedCheckmark()
        self._bin_path: str = ""
        self._last_friendly: str = ""
        self._last_raw: str = ""
        self._error_cfg: object = None
        self._build_ui()
        self._state = "idle"

    def _build_ui(self):
        self.setStyleSheet(f"background: {C['bg']};")
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setContentsMargins(50, 40, 50, 40)
        layout.setSpacing(14)

        # Confetti (added at bottom)
        self._confetti.setVisible(False)

        # Mascot
        self._mascot.setFixedSize(160, 180)
        self._mascot.set_mood("idle", 160)
        layout.addWidget(self._mascot, alignment=Qt.AlignmentFlag.AlignCenter)

        # Loading dots
        self._loading_dots.setVisible(False)
        layout.addWidget(self._loading_dots, alignment=Qt.AlignmentFlag.AlignCenter)

        # Checkmark
        self._checkmark.setFixedSize(120, 120)
        self._checkmark.setVisible(False)
        layout.addWidget(self._checkmark, alignment=Qt.AlignmentFlag.AlignCenter)

        # Title
        self._title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._title.setStyleSheet(f"font-size: {T}px; font-weight: 700; color: {C['text']};")
        layout.addWidget(self._title)

        # Step dots
        steps_layout = QHBoxLayout()
        steps_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        steps_layout.setSpacing(6)
        for step_name in ["Compile", "Upload", "Verify", "Done"]:
            dot = StepDot("")
            steps_layout.addWidget(dot)
            if step_name != "Done":
                arrow = QLabel("→")
                arrow.setStyleSheet(f"color: {C['text_faint']}; font-size: 18px;")
                steps_layout.addWidget(arrow)
            self._step_dots.append(dot)
        layout.addLayout(steps_layout)

        step_label_layout = QHBoxLayout()
        step_label_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        step_label_layout.setSpacing(28)
        for step_name in ["Compile", "Upload", "Verify", "Done"]:
            lbl = QLabel(step_name)
            lbl.setStyleSheet(f"color: {C['text_faint']}; font-size: 14px;")
            lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            step_label_layout.addWidget(lbl)
        layout.addLayout(step_label_layout)

        layout.addStretch(1)

        # Status
        self._status.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._status.setStyleSheet(f"color: {C['text_muted']}; font-size: {B}px;")
        layout.addWidget(self._status)

        # Mascot progress bar
        self._bar.setFixedWidth(380)
        layout.addWidget(self._bar, alignment=Qt.AlignmentFlag.AlignCenter)

        # Error button
        self._error_detail_btn.setObjectName("ghost")
        self._error_detail_btn.hide()
        self._error_detail_btn.clicked.connect(self._copy_error)
        layout.addWidget(self._error_detail_btn, alignment=Qt.AlignmentFlag.AlignCenter)

        # Save / Flash action row (hidden until compilation ready)
        action_row = QHBoxLayout()
        action_row.setAlignment(Qt.AlignmentFlag.AlignCenter)
        action_row.setSpacing(16)

        self._save_btn.setObjectName("secondary")
        self._save_btn.clicked.connect(self._on_save)
        self._save_btn.hide()
        action_row.addWidget(self._save_btn)

        self._flash_btn.setObjectName("primary")
        self._flash_btn.clicked.connect(self._on_flash)
        self._flash_btn.hide()
        action_row.addWidget(self._flash_btn)

        layout.addLayout(action_row)

        # Back button
        self._back_btn.setObjectName("secondary")
        self._back_btn.hide()
        self._back_btn.clicked.connect(self._go_back)
        layout.addWidget(self._back_btn, alignment=Qt.AlignmentFlag.AlignCenter)

        # Confetti overlay
        layout.addWidget(self._confetti, 1)

    def start_compile(self, board: str = ""):
        self._state = "compile"
        self._checkmark.setVisible(False)
        self._loading_dots.setVisible(True)
        self._loading_dots.start()
        self._mascot.set_mood("focused", 160)
        self._mascot.set_bounce_style("idle")
        self._mascot.start_bounce()
        self._title.setText("Cooking your code...")
        self._status.setText(f"Building for {board}" if board else "Compiling...")
        self._bar.set_value(0)
        self._back_btn.hide()
        self._error_detail_btn.hide()
        self._confetti.setVisible(False)
        self._confetti.stop()
        self._update_steps(0)

    def start_ota(self):
        self._state = "upload"
        self._mascot.set_mood("sweat", 160)
        self._title.setText("Sending to your ESP32...")
        self._status.setText("Connecting...")
        self._bar.set_value(5)
        self._update_steps(1)
        self._loading_dots.setVisible(True)
        self._loading_dots.start()

    def set_status(self, msg: str):
        self._status.setText(msg)

    def set_progress(self, pct: int, msg: str):
        self._bar.set_value(pct)
        self._status.setText(msg)
        if pct < 90:
            self._update_steps(1)
        elif pct < 100:
            self._update_steps(2)

    def show_success(self, device_name: str):
        self._state = "done"
        self._loading_dots.stop()
        self._loading_dots.setVisible(False)
        self._mascot.stop_bounce()
        self._mascot.set_mood("excited", 160)
        self._mascot.set_bounce_style("excited")
        self._mascot.start_bounce()
        self._checkmark.setVisible(True)
        QTimer.singleShot(200, self._checkmark.start_animate)

        self._title.setText("It works! 🎉")
        self._status.setText(f"{device_name} is running your code.")
        self._bar.set_value(100)
        self._update_steps(3)

        self._confetti.setVisible(True)
        self._confetti.start(80)
        QTimer.singleShot(5000, self._confetti.stop)

        self._back_btn.setText("← Flash another")
        self._back_btn.show()

    def show_compilation_ready(self, bin_path: str, has_device: bool):
        self._state = "ready"
        self._bin_path = bin_path
        self._loading_dots.stop()
        self._loading_dots.setVisible(False)
        self._checkmark.setVisible(False)
        self._mascot.set_mood("wink", 160)
        self._mascot.set_bounce_style("idle")
        self._mascot.start_bounce()
        self._title.setText("Compilation ready!")
        self._status.setText("Connect an ESP32 and click Flash Now, or save the binary for later.")
        self._bar.set_value(100)
        self._update_steps(1)
        self._step_dots[0].set_done()

        self._save_btn.show()
        self._flash_btn.show()
        self._flash_btn.setEnabled(has_device)
        self._flash_btn.setText("Flash Now" if has_device else "Flash Now (no device)")
        self._back_btn.setText("← Back")
        self._back_btn.show()

    def show_error(self, friendly: str, raw: str):
        self._state = "error"
        self._last_friendly = friendly
        self._last_raw = raw
        self._loading_dots.stop()
        self._loading_dots.setVisible(False)
        self._mascot.set_mood("surprise", 160)
        self._checkmark.setVisible(False)
        self._title.setText("Something went wrong")
        self._status.setText(friendly)
        self._error_detail_btn.show()
        self._back_btn.setText("← Try again")
        self._back_btn.show()

    def set_error_context(self, cfg):
        self._error_cfg = cfg

    def set_flash_enabled(self, enabled: bool):
        self._flash_btn.setEnabled(enabled)
        self._flash_btn.setText("Flash Now" if enabled else "Flash Now (no device)")

    def _on_save(self):
        if self._bin_path:
            self.save_binary_requested.emit(self._bin_path)

    def _on_flash(self):
        if self._bin_path:
            self.flash_now_requested.emit(self._bin_path)

    def _update_steps(self, active_index: int):
        for i, dot in enumerate(self._step_dots):
            if i < active_index:
                dot.set_done()
            elif i == active_index:
                dot.set_active(True)
            else:
                dot.set_active(False)

    def _copy_error(self):
        parts = []
        cfg = self._error_cfg
        if cfg:
            parts.append(f"Board: {cfg.board}")
            parts.append(f"Flash: {cfg.flash_size_override or cfg.flash_size}")
            parts.append(f"Partition: {cfg.partition_scheme}")
            if cfg.device_name:
                parts.append(f"Device: {cfg.device_name}")
            if cfg.wifi_ssid:
                parts.append(f"Wi-Fi: {cfg.wifi_ssid}")
            parts.append("")
        parts.append(self._last_friendly or "")
        if self._last_raw:
            parts.append("")
            parts.append("--- Build output ---")
            parts.append(self._last_raw.strip()[:2000])
        QApplication.clipboard().setText("\n".join(parts))
        self._error_detail_btn.setText("✓ Copied!")

    def _go_back(self):
        parent = self.parentWidget()
        if parent and hasattr(parent, "setCurrentIndex"):
            parent.setCurrentIndex(0)
