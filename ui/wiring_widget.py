from __future__ import annotations

from PyQt6.QtWidgets import QWidget, QLabel, QVBoxLayout, QHBoxLayout, QFrame
from PyQt6.QtCore import Qt, QRect
from PyQt6.QtGui import QPainter, QColor, QBrush, QPen, QFont

from palette import WARM_PASTEL as C
from constants import BOARD_PINOUTS

COMPONENT_COLORS: dict[str, str] = {
    "I2C":     "#FF6B6B",
    "SPI":     "#845EC2",
    "OneWire": "#FFC75F",
    "PWM":     "#4B7BEC",
    "Digital": "#4A90D9",
    "Analog":  "#00C9A7",
    "LED":     "#FFD54F",
    "UART":    "#FF9671",
}

class WiringDiagram(QWidget):
    def __init__(self, board_name: str = "", parent=None):
        super().__init__(parent)
        self._board = board_name
        self._pins: list[dict] = []
        self._suggestions: list[dict] = []
        self.setMinimumSize(400, 280)

    def set_data(self, board_name: str, pins: list, suggestions: list):
        self._board = board_name
        self._pins = pins
        self._suggestions = suggestions
        self.update()

    def paintEvent(self, e):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)

        w = self.width()
        h = self.height()
        if w < 50 or h < 50:
            p.end()
            return

        board_w = min(w - 80, 300)
        board_h = min(h - 80, 180)
        bx = (w - board_w) // 2
        by = 20

        # Board outline
        p.setBrush(QBrush(QColor(C['card'])))
        p.setPen(QPen(QColor(C['accent']), 2))
        p.drawRoundedRect(bx, by, board_w, board_h, 10, 10)

        # Board label
        p.setPen(QPen(QColor(C['text'])))
        f = QFont("sans-serif", 9, QFont.Weight.Bold)
        p.setFont(f)
        p.drawText(QRect(bx, by - 16, board_w, 14), Qt.AlignmentFlag.AlignCenter,
                   self._board or "ESP32 Dev Module")

        if not self._pins:
            p.setPen(QPen(QColor(C['text_muted'])))
            f2 = QFont("sans-serif", 11)
            p.setFont(f2)
            p.drawText(QRect(bx, by, board_w, board_h), Qt.AlignmentFlag.AlignCenter,
                       "No pin usage detected\nin this sketch.")
            p.end()
            return

        # Chip center
        chip_w = board_w * 0.55
        chip_h = board_h * 0.35
        cx = bx + (board_w - chip_w) // 2
        cy = by + (board_h - chip_h) // 2
        p.setBrush(QBrush(QColor("#2D3436")))
        p.setPen(Qt.PenStyle.NoPen)
        p.drawRoundedRect(int(cx), int(cy), int(chip_w), int(chip_h), 6, 6)

        p.setPen(QPen(QColor("#636E72")))
        f3 = QFont("sans-serif", 7)
        p.setFont(f3)
        p.drawText(QRect(int(cx), int(cy), int(chip_w), int(chip_h)),
                   Qt.AlignmentFlag.AlignCenter, self._board.split()[-1] if self._board else "ESP32")

        # Pin headers — left and right columns
        all_gpios = sorted(set(p["gpio"] for p in self._pins if p["gpio"] > 0))
        n_pins = len(all_gpios)
        pin_spacing = min(board_h * 0.65 / max(n_pins, 1), 22)
        start_y = by + board_h * 0.17

        pin_colors = {}
        for idx, s in enumerate(self._suggestions):
            color = s.get("color", list(COMPONENT_COLORS.values())[idx % len(COMPONENT_COLORS)])
            for pin_name, _gpio in s.get("pins", []):
                if isinstance(_gpio, int) and _gpio > 0:
                    pin_colors[_gpio] = color

        for i, gpio in enumerate(all_gpios):
            y = start_y + i * pin_spacing
            color_hex = pin_colors.get(gpio, C['accent'])
            color = QColor(color_hex)
            color_dark = color.darker(130)

            side = "left" if i % 2 == 0 else "right"

            if side == "left":
                px = bx + 8
            else:
                px = bx + board_w - 16

            # Pin dot
            p.setBrush(QBrush(color))
            p.setPen(QPen(color_dark, 1))
            p.drawEllipse(int(px), int(y), 10, 10)

            # GPIO label
            f4 = QFont("monospace", 7, QFont.Weight.Bold)
            p.setFont(f4)
            p.setPen(QPen(QColor(C['text'])))
            if side == "left":
                p.drawText(int(px + 14), int(y + 9), f"GPIO{gpio}")
            else:
                text_w = p.fontMetrics().horizontalAdvance(f"GPIO{gpio}")
                p.drawText(int(px - text_w - 6), int(y + 9), f"GPIO{gpio}")

            # Pin function label
            for pin in self._pins:
                if pin["gpio"] == gpio:
                    f5 = QFont("sans-serif", 6)
                    p.setFont(f5)
                    p.setPen(QPen(QColor(C['text_muted'])))
                    name = pin.get("name", "")
                    short_name = name.split("(")[0].strip() if "(" in name else name
                    if len(short_name) > 18:
                        short_name = short_name[:17] + "…"
                    if side == "left":
                        p.drawText(int(px + 14), int(y + 20), short_name)
                    else:
                        text_w2 = p.fontMetrics().horizontalAdvance(short_name)
                        p.drawText(int(px - text_w2 - 6), int(y + 20), short_name)
                    break

        # Legend
        legend_y = by + board_h + 12
        lx = bx
        for s in self._suggestions:
            color_hex = s.get("color", C['accent'])
            color = QColor(color_hex)
            p.setBrush(QBrush(color))
            p.setPen(Qt.PenStyle.NoPen)
            p.drawRect(int(lx), int(legend_y), 10, 10)

            f6 = QFont("sans-serif", 7)
            p.setFont(f6)
            p.setPen(QPen(QColor(C['text'])))
            comp = s.get("component", "")
            if len(comp) > 18:
                comp = comp[:17] + "…"
            p.drawText(int(lx + 14), int(legend_y + 9), comp)
            lx += p.fontMetrics().horizontalAdvance(comp) + 30

        p.end()
