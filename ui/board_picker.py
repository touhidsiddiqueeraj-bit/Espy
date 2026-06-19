from __future__ import annotations
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFrame, QScrollArea, QGridLayout, QDialog,
)
from PyQt6.QtCore import Qt, pyqtSignal, QSize
from PyQt6.QtGui import QPixmap

from palette import WARM_PASTEL as C
from constants import BOARDS
from ui.illustrations import BOARD_ILLUSTRATIONS


class BoardCard(QFrame):
    clicked = pyqtSignal(str)

    def __init__(self, board_name: str, parent=None):
        super().__init__(parent)
        self._board_name = board_name
        self._selected = False
        self.setObjectName("card")
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setFixedSize(200, 220)
        self._build()

    def _build(self):
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setSpacing(6)
        layout.setContentsMargins(10, 10, 10, 10)

        info = BOARDS.get(self._board_name, {})
        chip = info.get("chip", "ESP32")
        flash = info.get("flash_size", "?")
        fn = BOARD_ILLUSTRATIONS.get(self._board_name)
        if fn:
            svg = fn(130)
            lbl = QLabel()
            pm = QPixmap()
            pm.loadFromData(svg.encode())
            lbl.setPixmap(pm)
            lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            lbl.setFixedSize(140, 100)
            layout.addWidget(lbl, alignment=Qt.AlignmentFlag.AlignCenter)

        name = QLabel(self._board_name)
        name.setStyleSheet(f"font-size: 13px; font-weight: 700; color: {C['text']};")
        name.setAlignment(Qt.AlignmentFlag.AlignCenter)
        name.setWordWrap(True)
        layout.addWidget(name)

        chip_label = QLabel(f"{chip} · {flash}")
        chip_label.setStyleSheet(f"font-size: 11px; color: {C['text_muted']};")
        chip_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(chip_label)

    def set_selected(self, sel: bool):
        self._selected = sel
        if sel:
            self.setStyleSheet(
                f"QFrame#card {{ background: {C['card_hover']}; "
                f"border: 2px solid {C['accent']}; border-radius: 14px; }}"
            )
        else:
            self.setStyleSheet(
                f"QFrame#card {{ background: {C['bg']}; "
                f"border: 1px solid {C['border']}; border-radius: 14px; }}"
                f"QFrame#card:hover {{ background: {C['card']}; }}"
            )

    def mousePressEvent(self, e):
        if e.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit(self._board_name)
        super().mousePressEvent(e)

    def enterEvent(self, e):
        if not self._selected:
            self.setStyleSheet(
                f"QFrame#card {{ background: {C['card']}; "
                f"border: 1px solid {C['accent']}; border-radius: 14px; }}"
            )

    def leaveEvent(self, e):
        if not self._selected:
            self.setStyleSheet(
                f"QFrame#card {{ background: {C['bg']}; "
                f"border: 1px solid {C['border']}; border-radius: 14px; }}"
            )


class BoardPicker(QWidget):
    board_selected = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._selected_board: str = ""
        self._cards: list[BoardCard] = []
        self._build()

    def _build(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        title = QLabel("Choose your ESP32 board")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet(
            f"font-size: 20px; font-weight: 700; color: {C['text']}; padding-bottom: 4px;"
        )
        layout.addWidget(title)

        sub = QLabel("Pick the board that matches your hardware. Check the label on the chip.")
        sub.setAlignment(Qt.AlignmentFlag.AlignCenter)
        sub.setWordWrap(True)
        sub.setStyleSheet(f"font-size: 14px; color: {C['text_muted']}; padding-bottom: 8px;")
        layout.addWidget(sub)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff
        )
        scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")

        grid_widget = QWidget()
        grid = QGridLayout(grid_widget)
        grid.setSpacing(12)
        grid.setContentsMargins(4, 4, 4, 4)

        board_names = list(BOARDS.keys())
        cols = min(3, len(board_names))
        for i, name in enumerate(board_names):
            card = BoardCard(name)
            card.clicked.connect(self._on_card_clicked)
            self._cards.append(card)
            grid.addWidget(card, i // cols, i % cols)

        scroll.setWidget(grid_widget)
        layout.addWidget(scroll, 1)

    def _on_card_clicked(self, name: str):
        self._selected_board = name
        for card in self._cards:
            card.set_selected(card._board_name == name)
        self.board_selected.emit(name)

    def selected_board(self) -> str:
        return self._selected_board


class BoardPickerDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Select your ESP32 board")
        self.setFixedSize(700, 500)
        self.setStyleSheet(f"background: {C['bg']};")
        self._selected_board: str = ""
        self._build()

    def _build(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(8)

        # Board picker widget
        self._picker = BoardPicker()
        self._picker.board_selected.connect(self._on_selected)
        layout.addWidget(self._picker, 1)

        # Bottom buttons
        btn_row = QHBoxLayout()
        btn_row.addStretch()

        cancel = QPushButton("Cancel")
        cancel.setObjectName("secondary")
        cancel.clicked.connect(self.reject)
        btn_row.addWidget(cancel)

        self._select_btn = QPushButton("Select")
        self._select_btn.setObjectName("primary")
        self._select_btn.setEnabled(False)
        self._select_btn.clicked.connect(self.accept)
        btn_row.addWidget(self._select_btn)

        layout.addLayout(btn_row)

    def _on_selected(self, name: str):
        self._selected_board = name
        self._select_btn.setEnabled(True)

    def selected_board(self) -> str:
        return self._selected_board
