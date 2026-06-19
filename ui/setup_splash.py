from __future__ import annotations
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QProgressBar
from PyQt6.QtCore import Qt

from palette import WARM_PASTEL as C
from constants import EASY_MODE_TITLE_FONT as T, EASY_MODE_BODY_FONT as B
from ui.animations import BouncyMascot


class SetupSplash(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Espy")
        self.setWindowFlags(Qt.WindowType.Window | Qt.WindowType.FramelessWindowHint)
        self.setFixedSize(420, 320)
        self.setStyleSheet(f"background: {C['bg']}; border: 2px solid {C['border']}; border-radius: 16px;")

        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setSpacing(16)
        layout.setContentsMargins(40, 30, 40, 30)

        self._mascot = BouncyMascot()
        self._mascot.setFixedSize(100, 120)
        self._mascot.set_mood("focused", 100)
        self._mascot.set_bounce_style("idle")
        self._mascot.start_bounce()
        layout.addWidget(self._mascot, alignment=Qt.AlignmentFlag.AlignCenter)

        self._title = QLabel("Setting up Espy...")
        self._title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._title.setStyleSheet(f"font-size: {T}px; font-weight: 700; color: {C['text']};")
        layout.addWidget(self._title)

        self._status = QLabel("Preparing Arduino toolchain")
        self._status.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._status.setWordWrap(True)
        self._status.setStyleSheet(f"font-size: {B}px; color: {C['text_muted']};")
        layout.addWidget(self._status)

        self._bar = QProgressBar()
        self._bar.setMinimum(0)
        self._bar.setMaximum(0)
        self._bar.setFixedWidth(300)
        self._bar.setTextVisible(False)
        self._bar.setStyleSheet(f"""
            QProgressBar {{
                background: {C['card']};
                border: 1px solid {C['border']};
                border-radius: 6px;
                height: 10px;
            }}
            QProgressBar::chunk {{
                background: {C['accent']};
                border-radius: 4px;
            }}
        """)
        layout.addWidget(self._bar, alignment=Qt.AlignmentFlag.AlignCenter)

        self._sub = QLabel("This only happens once.\nMake sure you're connected to the internet.")
        self._sub.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._sub.setWordWrap(True)
        self._sub.setStyleSheet(f"font-size: 12px; color: {C['text_faint']};")
        layout.addWidget(self._sub, alignment=Qt.AlignmentFlag.AlignCenter)

    def set_status(self, msg: str):
        self._status.setText(msg)
        from PyQt6.QtWidgets import QApplication
        QApplication.processEvents()
