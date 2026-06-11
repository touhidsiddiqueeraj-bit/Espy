from __future__ import annotations
from PyQt6.QtWidgets import (
    QFrame, QVBoxLayout, QLabel, QPushButton, QFileDialog,
    QWidget, QStackedLayout,
)
from PyQt6.QtCore import Qt, pyqtSignal, QTimer
from PyQt6.QtGui import QDragEnterEvent, QDropEvent, QPixmap

from palette import WARM_PASTEL as C
from ui.illustrations import drop_zone_illustration
from ui.animations import PulseWidget, BouncyMascot


class DropZone(QFrame):
    file_dropped = pyqtSignal(str)
    file_chosen = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.setObjectName("dropzone")
        self.setAcceptDrops(True)
        self.setMinimumHeight(280)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self._enabled = True

        self._stack = QStackedLayout(self)
        self._stack.setStackingMode(QStackedLayout.StackingMode.StackAll)

        # Layer 0: pulse background (always visible beneath active layer)
        self._pulse = PulseWidget()
        self._pulse.start_pulse()
        self._stack.addWidget(self._pulse)

        # Layer 1: content — single centered layout, no separate arrow widget
        # (the arrow is already drawn inside drop_zone_illustration SVG)
        content = QWidget()
        content.setStyleSheet("background: transparent;")
        content.setVisible(True)
        layout = QVBoxLayout(content)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setSpacing(10)
        layout.setContentsMargins(20, 20, 20, 20)

        self._svg_label = QLabel()
        self._svg_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._svg_label.setFixedSize(160, 160)
        self._svg_label.setStyleSheet("background: transparent;")
        pixmap = QPixmap()
        pixmap.loadFromData(drop_zone_illustration().encode())
        self._svg_label.setPixmap(pixmap)
        layout.addWidget(self._svg_label, alignment=Qt.AlignmentFlag.AlignCenter)

        self._title = QLabel("Drop your .ino file here")
        self._title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._title.setStyleSheet(
            f"font-size: 20px; font-weight: 700; color: {C['text_muted']}; background: transparent;"
        )
        layout.addWidget(self._title)

        self._sub = QLabel("or click anywhere to browse — any Arduino sketch works!")
        self._sub.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._sub.setStyleSheet(f"color: {C['text_faint']}; font-size: 14px; background: transparent;")
        layout.addWidget(self._sub)

        self._browse_btn = QPushButton("Choose file")
        self._browse_btn.setObjectName("secondary")
        self._browse_btn.setFixedWidth(160)
        self._browse_btn.setFixedHeight(36)
        self._browse_btn.clicked.connect(self._browse)
        self._browse_btn.setToolTip("Pick a .ino file from your computer")
        self._browse_btn.setStyleSheet(
            f"QPushButton {{ font-size: 13px; font-weight: 600; "
            f"background: {C['card']}; border: 1.5px solid {C['border']}; "
            f"border-radius: 18px; color: {C['text_muted']}; }}"
            f"QPushButton:hover {{ background: {C['card_hover']}; border-color: {C['card_hover']}; }}"
        )
        layout.addWidget(self._browse_btn, alignment=Qt.AlignmentFlag.AlignCenter)

        self._content = content
        self._stack.addWidget(content)

        # Layer 2: disabled overlay (hidden by default — shown only when no device connected)
        self._disabled_overlay = QWidget()
        self._disabled_overlay.setVisible(False)
        self._disabled_overlay.setStyleSheet(
            f"background: {C['bg']}; border-radius: 24px;"
        )
        dl = QVBoxLayout(self._disabled_overlay)
        dl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        dl.setSpacing(12)
        self._disabled_icon = QLabel("🔌")
        self._disabled_icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._disabled_icon.setStyleSheet("font-size: 36px; background: transparent;")
        dl.addWidget(self._disabled_icon)
        self._disabled_title = QLabel("No ESP32 connected")
        self._disabled_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._disabled_title.setStyleSheet(
            f"font-size: 20px; font-weight: 600; color: {C['text_faint']}; background: transparent;"
        )
        dl.addWidget(self._disabled_title)
        self._disabled_sub = QLabel("Select or set up a device from the sidebar first")
        self._disabled_sub.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._disabled_sub.setWordWrap(True)
        self._disabled_sub.setStyleSheet(
            f"font-size: 15px; color: {C['text_faint']}; background: transparent;"
        )
        dl.addWidget(self._disabled_sub)
        self._stack.addWidget(self._disabled_overlay)

        # Mascot overlay (hidden, shown on dragover)
        self._mascot_overlay = QWidget(self)
        self._mascot_overlay.setVisible(False)
        ml = QVBoxLayout(self._mascot_overlay)
        ml.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._drag_mascot = BouncyMascot()
        self._drag_mascot.set_mood("excited", 80)
        self._drag_mascot.set_bounce_style("excited")
        self._drag_mascot.start_bounce()
        ml.addWidget(self._drag_mascot, alignment=Qt.AlignmentFlag.AlignBottom)

        # Cycle hints
        self._hints = [
            "Drop your .ino file here",
            "Or click anywhere to browse",
            "Any Arduino sketch works!",
        ]
        self._hint_idx = 0
        self._hint_timer = QTimer(self)
        self._hint_timer.timeout.connect(self._cycle_hint)
        self._hint_timer.start(4000)

    def set_enabled(self, enabled: bool):
        self._enabled = enabled
        self._disabled_overlay.setVisible(not enabled)
        self._content.setVisible(enabled)
        self.setAcceptDrops(enabled)
        self.setCursor(Qt.CursorShape.PointingHandCursor if enabled else Qt.CursorShape.ArrowCursor)
        if enabled:
            self._pulse.start_pulse()
        else:
            self._pulse.stop_pulse()

    def mousePressEvent(self, e):
        if self._enabled and e.button() == Qt.MouseButton.LeftButton:
            self._browse()
        super().mousePressEvent(e)

    def _cycle_hint(self):
        self._hint_idx = (self._hint_idx + 1) % len(self._hints)
        self._title.setText(self._hints[self._hint_idx])

    def _browse(self):
        if not self._enabled:
            return
        path, _ = QFileDialog.getOpenFileName(
            self, "Choose an Arduino sketch", "",
            "Arduino Sketch (*.ino);;All Files (*)"
        )
        if path:
            self.file_chosen.emit(path)

    def dragEnterEvent(self, e: QDragEnterEvent):
        if not self._enabled:
            return
        if e.mimeData().hasUrls():
            urls = e.mimeData().urls()
            if any(u.toLocalFile().endswith(".ino") for u in urls):
                e.acceptProposedAction()
                self.setProperty("dragover", "true")
                self.style().unpolish(self)
                self.style().polish(self)
                self._mascot_overlay.setVisible(True)

    def dragLeaveEvent(self, e):
        self.setProperty("dragover", "false")
        self.style().unpolish(self)
        self.style().polish(self)
        self._mascot_overlay.setVisible(False)

    def dropEvent(self, e: QDropEvent):
        if not self._enabled:
            return
        self.setProperty("dragover", "false")
        self.style().unpolish(self)
        self.style().polish(self)
        self._mascot_overlay.setVisible(False)
        for url in e.mimeData().urls():
            path = url.toLocalFile()
            if path.endswith(".ino"):
                self.file_dropped.emit(path)
                return
