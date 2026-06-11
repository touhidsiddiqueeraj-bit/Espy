from __future__ import annotations
import math
import random
from PyQt6.QtWidgets import (
    QWidget, QLabel, QProgressBar, QStackedWidget, QGraphicsOpacityEffect,
)
from PyQt6.QtCore import (
    Qt, QTimer, QPropertyAnimation, QVariantAnimation, QEasingCurve,
    pyqtProperty, QRect, QSize, QPointF,
    QParallelAnimationGroup, QSequentialAnimationGroup, QPauseAnimation,
    QAbstractAnimation,
)
from PyQt6.QtGui import (
    QPainter, QColor, QBrush, QPen, QFont, QPixmap, QLinearGradient,
)

from palette import WARM_PASTEL as C
from ui.illustrations import ESPY_MOODS, wifi_illustration, usb_illustration, plug_illustration, espy_glasses


# ── Fade transition stack ─────────────────────────────────

class FadeStack(QStackedWidget):
    """QStackedWidget with a crossfade between pages."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self._animating = False

    def fade_to(self, index: int, duration: int = 250):
        if self._animating or index == self.currentIndex():
            self.setCurrentIndex(index)
            return
        self._animating = True
        current = self.currentWidget()
        if current:
            eff = QGraphicsOpacityEffect(current)
            current.setGraphicsEffect(eff)
            anim = QPropertyAnimation(eff, b"opacity")
            anim.setDuration(duration // 2)
            anim.setStartValue(1.0)
            anim.setEndValue(0.0)
            anim.finished.connect(lambda: self._finish_fade(index, duration // 2))
            anim.start()
        else:
            self.setCurrentIndex(index)
            self._animating = False

    def _finish_fade(self, index: int, next_duration: int):
        self.setCurrentIndex(index)
        w = self.currentWidget()
        if w:
            eff = QGraphicsOpacityEffect(w)
            w.setGraphicsEffect(eff)
            eff.setOpacity(0.0)
            anim = QPropertyAnimation(eff, b"opacity")
            anim.setDuration(next_duration)
            anim.setStartValue(0.0)
            anim.setEndValue(1.0)
            anim.finished.connect(self._clear_gfx)
            anim.start()
        self._animating = False

    def _clear_gfx(self):
        w = self.currentWidget()
        if w:
            w.setGraphicsEffect(None)


# ── Bouncy mascot (QVariantAnimation, no pyqtProperty) ─────

class BouncyMascot(QLabel):
    """Mascot with mood-based bounce styles."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._current_mood = "idle"
        self._current_size = 140
        self._offset = 0
        self._bounce = QVariantAnimation(self)
        self._bounce.setLoopCount(-1)
        self._bounce.setEasingCurve(QEasingCurve.Type.InOutSine)
        self._bounce.valueChanged.connect(self._on_bounce)
        self._bounce_style = "idle"

    def set_mood(self, mood: str, size: int = 140):
        fn = ESPY_MOODS.get(mood, ESPY_MOODS["idle"])
        pm = QPixmap()
        pm.loadFromData(fn(size).encode())
        self.setPixmap(pm)
        self._current_mood = mood
        self._current_size = size

    def set_bounce_style(self, style: str = "idle"):
        self._bounce_style = style
        pulses = {
            "idle":    (1200,  -6),
            "happy":   (800,  -10),
            "sad":     (1800, -4),
            "excited": (600,  -14),
            "searching": (1000, -8),
        }
        dur, height = pulses.get(style, (1200, -6))
        self._bounce.setDuration(dur)
        self._bounce.setStartValue(0)
        self._bounce.setKeyValueAt(0.5, height)
        self._bounce.setEndValue(0)

    def start_bounce(self):
        if self._bounce.state() != QAbstractAnimation.State.Running:
            self._bounce.start()

    def stop_bounce(self):
        self._bounce.stop()
        self._offset = 0
        self.update()

    def _on_bounce(self, value):
        self._offset = int(value)
        self.update()

    def paintEvent(self, e):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)
        pm = self.pixmap()
        if pm and not pm.isNull():
            r = self.rect()
            x = (r.width() - pm.width()) // 2
            y = (r.height() - pm.height()) // 2 + self._offset
            p.drawPixmap(x, y, pm)
        p.end()


# ── Loading dots ──────────────────────────────────────────

class LoadingDots(QLabel):
    """Three dots that pulse in sequence."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self._phase = 0
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._tick)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setStyleSheet(f"font-size: 32px; color: {C['accent']}; font-weight: 700;")
        self._timer.start(350)

    def _tick(self):
        phases = ["● ○ ○", "○ ● ○", "○ ○ ●"]
        self._phase = (self._phase + 1) % 3
        self.setText(phases[self._phase])

    def start(self):
        self._timer.start(350)

    def stop(self):
        self._timer.stop()
        self.setText("")


# ── Pulse widget (drop zone glow) ─────────────────────────

class PulseWidget(QWidget):
    """Widget that pulses its background opacity."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self._pulse_opacity = 0.3
        self._pulse = QPropertyAnimation(self, b"pulse_opacity")
        self._pulse.setDuration(2000)
        self._pulse.setLoopCount(-1)
        self._pulse.setEasingCurve(QEasingCurve.Type.InOutSine)

    def start_pulse(self):
        self._pulse.setStartValue(0.15)
        self._pulse.setEndValue(0.5)
        self._pulse.start()

    def stop_pulse(self):
        self._pulse.stop()

    def _get_pulse(self) -> float:
        return self._pulse_opacity

    def _set_pulse(self, v: float):
        self._pulse_opacity = v
        self.update()

    pulse_opacity = pyqtProperty(float, _get_pulse, _set_pulse)

    def paintEvent(self, e):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        color = QColor(C['accent'])
        color.setAlphaF(self._pulse_opacity * 0.12)
        p.setBrush(QBrush(color))
        p.setPen(Qt.PenStyle.NoPen)
        p.drawRoundedRect(self.rect().adjusted(2, 2, -2, -2), 24, 24)
        p.end()


# ── Confetti ──────────────────────────────────────────────

class ConfettiWidget(QWidget):
    """Falling confetti particles with sparkle shapes."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self._timer = QTimer(self)
        self._timer.timeout.connect(self.update)
        self._particles: list[dict] = []
        self._running = False

    def start(self, count: int = 60):
        import random
        rng = random.Random()
        self._particles = []
        colors = [C['accent'], C['success'], C['warning'], C['info'], C['accent_hover']]
        shapes = ["rect", "star", "circle"]
        for _ in range(count):
            self._particles.append({
                "x": rng.uniform(0, 1),
                "y": rng.uniform(-0.3, 0),
                "speed": rng.uniform(0.002, 0.01),
                "size": rng.randint(4, 12),
                "color": rng.choice(colors),
                "opacity": rng.uniform(0.4, 0.9),
                "drift": rng.uniform(-0.002, 0.002),
                "shape": rng.choice(shapes),
                "rotation": rng.uniform(0, 360),
                "rot_speed": rng.uniform(-3, 3),
            })
        self._running = True
        self._timer.start(30)

    def stop(self):
        self._running = False
        self._timer.stop()
        self._particles = []
        self.update()

    def paintEvent(self, e):
        if not self._running or not self._particles:
            return
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        w = self.width()
        h = self.height()
        for pt in self._particles:
            pt["y"] += pt["speed"]
            pt["x"] += pt["drift"]
            pt["rotation"] += pt["rot_speed"]
            if pt["y"] > 1.15:
                pt["y"] = -0.08
                pt["x"] = random.random()
            px = int(pt["x"] * w)
            py = int(pt["y"] * h)
            color = QColor(pt["color"])
            color.setAlphaF(pt["opacity"])
            p.setBrush(QBrush(color))
            p.setPen(Qt.PenStyle.NoPen)
            s = pt["size"]
            if pt["shape"] == "star":
                cx, cy = px, py
                r_outer = s // 2
                poly = []
                for i in range(5):
                    angle = math.radians(pt["rotation"] + i * 72 - 90)
                    poly.append((cx + r_outer * math.cos(angle), cy + r_outer * math.sin(angle)))
                    angle2 = math.radians(pt["rotation"] + (i + 0.5) * 72 - 90)
                    poly.append((cx + r_outer * 0.4 * math.cos(angle2), cy + r_outer * 0.4 * math.sin(angle2)))
                if poly:
                    pts = [QPointF(x, y) for x, y in poly]
                    p.drawPolygon(pts)
            elif pt["shape"] == "circle":
                p.drawEllipse(px - s // 4, py - s // 4, s // 2, s // 2)
            else:
                p.drawRoundedRect(px, py, s, s // 2, 2, 2)
        p.end()


# ── Animated checkmark ────────────────────────────────────

class AnimatedCheckmark(QWidget):
    """Draws a circular checkmark then breathes."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self._progress = 0.0
        self._breathing = False
        self._breath_progress = 0.0
        self._anim = QPropertyAnimation(self, b"draw_progress")
        self._anim.setDuration(600)
        self._anim.setEasingCurve(QEasingCurve.Type.OutBack)
        self._breath_anim = QPropertyAnimation(self, b"breath_value")
        self._breath_anim.setDuration(1500)
        self._breath_anim.setLoopCount(-1)
        self._breath_anim.setEasingCurve(QEasingCurve.Type.InOutSine)
        self.setFixedSize(120, 120)

    def start_animate(self):
        self._progress = 0.0
        self._breathing = False
        self._anim.setStartValue(0.0)
        self._anim.setEndValue(1.0)
        self._anim.start()
        self._anim.finished.connect(self._start_breathing)

    def _start_breathing(self):
        self._breathing = True
        self._breath_anim.setStartValue(0.9)
        self._breath_anim.setEndValue(1.1)
        self._breath_anim.start()

    def _get_progress(self) -> float:
        return self._progress

    def _set_progress(self, v: float):
        self._progress = v
        self.update()

    def _get_breath(self) -> float:
        return self._breath_progress

    def _set_breath(self, v: float):
        self._breath_progress = v
        self.update()

    draw_progress = pyqtProperty(float, _get_progress, _set_progress)
    breath_value = pyqtProperty(float, _get_breath, _set_breath)

    def paintEvent(self, e):
        if self._progress <= 0:
            return
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        w = self.width()
        h = self.height()
        cx, cy = w // 2, h // 2
        base_r = min(cx, cy) - 8
        scale = self._breath_progress if self._breathing else 1.0
        r = int(base_r * scale)

        p.setBrush(QBrush(QColor(C['success'])))
        p.setPen(Qt.PenStyle.NoPen)
        p.drawEllipse(cx - r, cy - r, r * 2, r * 2)

        p.setPen(QPen(QColor("white"), 6, Qt.PenStyle.SolidLine,
                      Qt.PenCapStyle.RoundCap, Qt.PenJoinStyle.RoundJoin))
        path = [
            (cx - r * 0.4, cy),
            (cx - r * 0.1, cy + r * 0.35),
            (cx + r * 0.45, cy - r * 0.3),
        ]
        if self._progress < 0.5:
            frac = self._progress * 2
            p1 = path[0]
            p2 = (
                path[0][0] + (path[1][0] - path[0][0]) * frac,
                path[0][1] + (path[1][1] - path[0][1]) * frac,
            )
            p.drawLine(int(p1[0]), int(p1[1]), int(p2[0]), int(p2[1]))
        else:
            frac = (self._progress - 0.5) * 2
            p.drawLine(int(path[0][0]), int(path[0][1]),
                       int(path[1][0]), int(path[1][1]))
            p2 = (
                path[1][0] + (path[2][0] - path[1][0]) * frac,
                path[1][1] + (path[2][1] - path[1][1]) * frac,
            )
            p.drawLine(int(path[1][0]), int(path[1][1]),
                       int(p2[0]), int(p2[1]))
        p.end()


# ── Mascot progress bar ───────────────────────────────────

class MascotProgressBar(QWidget):
    """Progress bar with a mascot that pushes the filled portion."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self._value = 0
        self._anim = QPropertyAnimation(self, b"bar_value")
        self._anim.setDuration(400)
        self._anim.setEasingCurve(QEasingCurve.Type.OutCubic)
        self.setFixedHeight(48)
        self.setMinimumWidth(300)
        self._pixmap_cache: dict[tuple[str, int], QPixmap] = {}

    def _get_value(self) -> int:
        return self._value

    def _set_value(self, v: int):
        self._value = max(0, min(100, v))
        self.update()

    bar_value = pyqtProperty(int, _get_value, _set_value)

    def set_value(self, v: int, animate: bool = True):
        if animate:
            self._anim.setStartValue(self._value)
            self._anim.setEndValue(v)
            self._anim.start()
        else:
            self._value = v
            self.update()

    def paintEvent(self, e):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)

        w = self.width()
        h = self.height()
        bar_h = 16
        bar_y = (h - bar_h) // 2
        margin = 4
        track_w = w - margin * 2
        m = 4
        fill_w = max(m, int(track_w * self._value / 100))
        r = bar_h // 2

        # Track
        p.setBrush(QBrush(QColor(C['border'])))
        p.setPen(Qt.PenStyle.NoPen)
        p.drawRoundedRect(margin, bar_y, track_w, bar_h, r, r)

        # Fill
        grad = QLinearGradient(margin, 0, margin + fill_w, 0)
        grad.setColorAt(0, QColor(C['accent']))
        grad.setColorAt(1, QColor(C['info']))
        p.setBrush(QBrush(grad))
        p.drawRoundedRect(margin, bar_y, fill_w, bar_h, r, r)

        if self._value > 0:
            # Block
            block_x = margin + fill_w - 6
            block_y = bar_y - 8
            block_w = 14
            block_h = bar_h + 16
            bc = QColor(C['accent_hover'])
            bc.setAlphaF(0.4)
            p.setBrush(QBrush(bc))
            p.drawRoundedRect(block_x, block_y, block_w, block_h, 4, 4)

            # Mascot pushing position
            mascot_size = 36
            mx = block_x - mascot_size // 2
            my = block_y - mascot_size + 4
            try:
                mood = "sweat" if 30 < self._value < 80 else ("focused" if self._value < 100 else "excited")
                if self._value >= 100:
                    mood = "happy"
                key = (mood, mascot_size)
                pm = self._pixmap_cache.get(key)
                if pm is None:
                    fn = ESPY_MOODS.get(mood, ESPY_MOODS["idle"])
                    pm = QPixmap()
                    pm.loadFromData(fn(mascot_size).encode())
                    if not pm.isNull():
                        self._pixmap_cache[key] = pm
                if pm is not None and not pm.isNull():
                    p.drawPixmap(int(mx), int(my), pm)
            except Exception:
                pass

        # Percentage text
        p.setPen(QPen(QColor(C['text_muted'])))
        font = QFont("system-ui", 13, QFont.Weight.Bold)
        p.setFont(font)
        p.drawText(self.rect(), Qt.AlignmentFlag.AlignCenter, f"{self._value}%")

        p.end()


# ── Breathing dot (QVariantAnimation, no pyqtProperty) ────

class BreathingDot(QLabel):
    """Pulsing status dot. Green for online, gray for offline."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self._online = True
        self._dot_opacity = 1.0
        self._anim = QVariantAnimation(self)
        self._anim.setLoopCount(-1)
        self._anim.setEasingCurve(QEasingCurve.Type.InOutSine)
        self._anim.valueChanged.connect(self._on_opacity)
        self.setText("●")
        self.setStyleSheet("font-size: 14px; background: transparent;")

    def set_online(self, online: bool):
        self._online = online
        color = C['success'] if online else C['text_faint']
        self.setStyleSheet(f"font-size: 14px; color: {color}; background: transparent;")
        self._anim.stop()
        if online:
            self._anim.setDuration(1200)
            self._anim.setStartValue(0.5)
            self._anim.setEndValue(1.0)
        else:
            self._anim.setDuration(2500)
            self._anim.setStartValue(0.3)
            self._anim.setEndValue(0.6)
        self._anim.start()

    def stop(self):
        self._anim.stop()

    def _on_opacity(self, v):
        self._dot_opacity = v
        base = C['success'] if self._online else C['text_faint']
        c = QColor(base)
        c.setAlphaF(v)
        name = c.name(QColor.NameFormat.HexArgb)
        self.setStyleSheet(f"font-size: 14px; color: {name}; background: transparent;")


# ── Animated arrow (QVariantAnimation, no pyqtProperty) ───

class AnimatedArrow(QWidget):
    """Bouncing pointing arrow."""
    def __init__(self, direction: str = "down", parent=None):
        super().__init__(parent)
        self._direction = direction
        self._arrow_off = 0
        self._bounce = QVariantAnimation(self)
        self._bounce.setDuration(1000)
        self._bounce.setLoopCount(-1)
        self._bounce.setEasingCurve(QEasingCurve.Type.InOutSine)
        self._bounce.setStartValue(0)
        self._bounce.setEndValue(8)
        self._bounce.valueChanged.connect(self._on_bounce)
        self._bounce.start()
        self.setFixedSize(40, 40)

    def _on_bounce(self, v):
        self._arrow_off = int(v)
        self.update()

    def paintEvent(self, e):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        color = QColor(C['accent'])
        color.setAlphaF(0.7)
        p.setPen(QPen(color, 3, Qt.PenStyle.SolidLine,
                       Qt.PenCapStyle.RoundCap, Qt.PenJoinStyle.RoundJoin))
        offset = self._arrow_off
        cx, cy = self.width() // 2, self.height() // 2 + offset
        s = 12
        if self._direction == "down":
            p.drawLine(cx, cy - s, cx, cy + s)
            p.drawLine(cx - s // 2, cy + s // 2, cx, cy + s)
            p.drawLine(cx + s // 2, cy + s // 2, cx, cy + s)
        elif self._direction == "up":
            p.drawLine(cx, cy + s, cx, cy - s)
            p.drawLine(cx - s // 2, cy - s // 2, cx, cy - s)
            p.drawLine(cx + s // 2, cy - s // 2, cx, cy - s)
        elif self._direction == "right":
            p.drawLine(cx - s, cy, cx + s, cy)
            p.drawLine(cx + s // 2, cy - s // 2, cx + s, cy)
            p.drawLine(cx + s // 2, cy + s // 2, cx + s, cy)
        p.end()


# ── Floating USB (QVariantAnimation, no pyqtProperty) ─────

class FloatingUSB(QLabel):
    """USB icon that gently floats up and down."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        pm = QPixmap()
        pm.loadFromData(usb_illustration(160).encode())
        self.setPixmap(pm)
        self._float_off = 0
        self._float = QVariantAnimation(self)
        self._float.setDuration(2500)
        self._float.setLoopCount(-1)
        self._float.setEasingCurve(QEasingCurve.Type.InOutSine)
        self._float.setStartValue(0)
        self._float.setEndValue(-12)
        self._float.valueChanged.connect(self._on_float)
        self._float.start()

    def _on_float(self, v):
        self._float_off = int(v)
        self.update()

    def paintEvent(self, e):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)
        pm = self.pixmap()
        if pm and not pm.isNull():
            off = self._float_off
            r = self.rect()
            x = (r.width() - pm.width()) // 2
            y = (r.height() - pm.height()) // 2 + off
            p.drawPixmap(x, y, pm)
        p.end()


# ── Plug Animation (composite laptop + USB + ESP) ────────

class PlugAnimation(QLabel):
    """Composite illustration: laptop port ← USB cable → ESP32 board.
    Shows the physical connection at realistic proportions with a pulsing glow."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setMinimumSize(240, 160)
        self._update_pixmap(240)
        self._breath = QVariantAnimation(self)
        self._breath.setDuration(2000)
        self._breath.setLoopCount(-1)
        self._breath.setEasingCurve(QEasingCurve.Type.InOutSine)
        self._breath.setStartValue(0.92)
        self._breath.setEndValue(1.08)
        self._breath.valueChanged.connect(self._on_breath)
        self._breath.start()

    def _update_pixmap(self, base_size: int):
        pm = QPixmap()
        pm.loadFromData(plug_illustration(base_size).encode())
        self._pixmap = pm
        if not pm.isNull():
            self.setFixedSize(pm.width(), pm.height())

    def _on_breath(self, v):
        pass  # SVG animation handles independent pulsing

    def paintEvent(self, e):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)
        if self._pixmap and not self._pixmap.isNull():
            pm = self._pixmap
            r = self.rect()
            x = (r.width() - pm.width()) // 2
            y = (r.height() - pm.height()) // 2
            p.drawPixmap(x, y, pm)
        p.end()


# ── Pulsing Wi-Fi ─────────────────────────────────────────

class PulsingWifi(QLabel):
    """Wi-Fi icon with pulsing signal arcs."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._wifi_pulse = 0.5
        self._pulse = QVariantAnimation(self)
        self._pulse.setDuration(2000)
        self._pulse.setLoopCount(-1)
        self._pulse.setEasingCurve(QEasingCurve.Type.InOutSine)
        self._pulse.setStartValue(0.3)
        self._pulse.setEndValue(1.0)
        self._pulse.valueChanged.connect(self._on_wifi_pulse)
        self._pulse.start()

    def _on_wifi_pulse(self, v):
        self._wifi_pulse = v
        self.update()

    def paintEvent(self, e):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        w = self.width()
        h = self.height()
        cx, cy = w // 2, h // 2 + 12
        base = min(w, h) * 0.08
        p.setPen(Qt.PenStyle.NoPen)
        for i in range(3):
            radius = base * (4 - i) * 1.2
            alpha = self._wifi_pulse * (0.3 + 0.25 * (2 - i) / 2)
            color = QColor(C['accent'])
            color.setAlphaF(max(0.05, alpha))
            p.setBrush(QBrush(color))
            p.drawChord(int(cx - radius), int(cy - radius * 1.5),
                        int(radius * 2), int(radius * 3),
                        45 * 16, 90 * 16)
        dot_color = QColor(C['accent'])
        dot_color.setAlphaF(self._wifi_pulse)
        p.setBrush(QBrush(dot_color))
        p.drawEllipse(cx - 5, cy - 5 + int(base * 1.5), 10, 10)
        p.end()


# ── Slide label (QVariantAnimation, no pyqtProperty) ──────

class SlideLabel(QLabel):
    """Label that slides in vertically."""
    def __init__(self, text: str, parent=None):
        super().__init__(text, parent)
        self._slide_offset = 20
        self._slide = QVariantAnimation(self)
        self._slide.setDuration(400)
        self._slide.setEasingCurve(QEasingCurve.Type.OutCubic)
        self._slide.valueChanged.connect(self._on_slide)
        self.setStyleSheet(f"color: {C['success']}; font-size: 16px;")

    def animate_in(self, delay: int = 0):
        from PyQt6.QtCore import QTimer as QTimer2
        QTimer2.singleShot(delay, self._do_slide)

    def _do_slide(self):
        self._slide.setStartValue(20)
        self._slide.setEndValue(0)
        self._slide.start()

    def _on_slide(self, v):
        self._slide_offset = int(v)
        self.setContentsMargins(0, self._slide_offset, 0, 0)
        self.update()


# ── Blinking LED (for blink example preview) ──────────────

class BlinkingLED(QWidget):
    """A small LED that blinks between on (yellow) and off (dim gray)."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self._led_on = False
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._toggle)
        self._timer.start(500)
        self.setFixedSize(32, 32)

    def _toggle(self):
        self._led_on = not self._led_on
        self.update()

    def start(self):
        self._timer.start(500)

    def stop(self):
        self._timer.stop()

    def paintEvent(self, e):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        cx, cy = self.width() // 2, self.height() // 2
        r = min(cx, cy) - 2

        if self._led_on:
            color = QColor(255, 220, 50)
            glow = QColor(255, 220, 50, 60)
        else:
            color = QColor(80, 80, 80)
            glow = QColor(80, 80, 80, 20)

        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(QBrush(glow))
        p.drawEllipse(cx - r - 3, cy - r - 3, (r + 3) * 2, (r + 3) * 2)

        p.setBrush(QBrush(color))
        p.drawEllipse(cx - r, cy - r, r * 2, r * 2)
        p.end()


# ── Progress pulse (QVariantAnimation, no pyqtProperty) ───

class ProgressPulse(QProgressBar):
    """Progress bar with subtle glow."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self._glow = QVariantAnimation(self)
        self._glow.setDuration(1500)
        self._glow.setLoopCount(-1)
        self._glow.setEasingCurve(QEasingCurve.Type.InOutSine)
        self._glow.valueChanged.connect(self._on_glow)
        self._glow_val = 0.6

    def start_glow(self):
        self._glow.setStartValue(0.6)
        self._glow.setEndValue(1.0)
        self._glow.start()

    def stop_glow(self):
        self._glow.stop()

    def _on_glow(self, v):
        self._glow_val = v
        qss = f"""
            QProgressBar {{
                background: {C['border']};
                border: none; border-radius: 10px; height: 16px;
            }}
            QProgressBar::chunk {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 {C['accent']}, stop:1 {C['info']});
                border-radius: 10px;
            }}
        """
        self.setStyleSheet(qss)
