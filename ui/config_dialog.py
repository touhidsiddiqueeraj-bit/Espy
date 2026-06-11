from __future__ import annotations
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QLineEdit, QComboBox, QFrame, QFormLayout, QTextEdit,
    QWidget, QScrollArea,
)
from PyQt6.QtCore import Qt, pyqtSignal, QTimer

from palette import WARM_PASTEL as C, stylesheet
from models import InoConfig
from constants import BOARDS, get_scheme_partitions, PARTITION_SCHEMES
from ui.animations import BouncyMascot, SlideLabel
from ui.illustrations import chip_icon, book_icon, espy_wink, BOARD_ILLUSTRATIONS
from ui.partition_editor import PartitionEditor
from ui.wiring_widget import WiringDiagram


class ConfigDialog(QDialog):
    confirmed = pyqtSignal(InoConfig)

    def __init__(self, cfg: InoConfig, target_device: str = "", parent=None):
        super().__init__(parent)
        self.cfg = cfg
        self._target_device = target_device
        self.setWindowTitle("Check your settings")
        self.setMinimumWidth(580)
        self.setMinimumHeight(420)
        self.setMaximumHeight(900)
        self.resize(660, 560)
        self.setStyleSheet(stylesheet())
        self._build_ui()

    def _build_ui(self):
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(0)

        # Scrollable body
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")

        body = QWidget()
        layout = QVBoxLayout(body)
        layout.setSpacing(16)
        layout.setContentsMargins(28, 24, 28, 16)
        scroll.setWidget(body)
        outer.addWidget(scroll, 1)

        # ── Fixed button row pinned to bottom ──
        btn_container = QWidget()
        btn_container.setStyleSheet(f"border-top: 1px solid {C['border']};")
        btn_outer = QHBoxLayout(btn_container)
        btn_outer.setContentsMargins(28, 12, 28, 16)
        btn_outer.addStretch()
        cancel = QPushButton("Cancel")
        cancel.setObjectName("secondary")
        cancel.clicked.connect(self.reject)
        self._flash_btn = QPushButton("Flash Now →")
        self._flash_btn.setObjectName("primary")
        self._flash_btn.clicked.connect(self._confirm)
        self._flash_btn.setEnabled(bool(self.cfg.wifi_password))
        btn_outer.addWidget(cancel)
        btn_outer.addWidget(self._flash_btn)
        outer.addWidget(btn_container)

        # Header with mascot
        header = QHBoxLayout()
        title = QLabel("Here's what I found in your code:")
        title.setStyleSheet(f"font-size: 19px; font-weight: 700; color: {C['text']};")
        header.addWidget(title)
        header.addStretch()

        mascot = BouncyMascot()
        mascot.set_mood("wink", 54)
        mascot.setFixedSize(54, 64)
        mascot.start_bounce()
        header.addWidget(mascot)
        layout.addLayout(header)

        # Config card — two columns
        card = QFrame()
        card.setObjectName("card")
        card_layout = QHBoxLayout(card)
        card_layout.setContentsMargins(16, 14, 16, 14)
        card_layout.setSpacing(20)

        # ── Left column: illustration + partitions (fixed width wrapper) ──
        left_widget = QWidget()
        left_widget.setFixedWidth(160)
        left_col = QVBoxLayout(left_widget)
        left_col.setContentsMargins(0, 0, 0, 0)
        left_col.setSpacing(6)

        self._board_ill = QLabel()
        self._board_ill.setFixedSize(130, 95)
        self._board_ill.setAlignment(Qt.AlignmentFlag.AlignCenter)
        left_col.addWidget(self._board_ill)

        self._part_table = QLabel()
        self._part_table.setWordWrap(True)
        self._part_table.setStyleSheet(
            f"color: {C['text_muted']}; font-size: 11px; line-height: 1.4; "
            f"font-family: 'Courier New', monospace;"
        )
        self._part_table.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
        left_col.addWidget(self._part_table, 1)

        csv_btn = QPushButton("Edit CSV")
        csv_btn.setObjectName("ghost")
        csv_btn.setFixedHeight(26)
        csv_btn.setStyleSheet(
            f"QPushButton{{ font-size: 11px; padding: 2px 8px; background: {C['card']}; "
            f"border: 1px solid {C['border']}; border-radius: 6px; }}"
            f"QPushButton:hover{{ background: {C['card_hover']}; }}"
        )
        csv_btn.clicked.connect(self._open_partition_editor)
        left_col.addWidget(csv_btn, alignment=Qt.AlignmentFlag.AlignRight)

        card_layout.addWidget(left_widget)

        # ── Right column: settings fields ──
        right_col = QVBoxLayout()
        right_col.setSpacing(8)

        if self._target_device:
            tl = QLabel(f"Target: {self._target_device}")
            tl.setStyleSheet(f"color: {C['accent']}; font-weight: 700; font-size: 14px;")
            right_col.addWidget(tl)

        def _field_row(label_text, widget):
            row = QHBoxLayout()
            lbl = QLabel(label_text)
            lbl.setStyleSheet(f"color: {C['text_muted']}; font-weight: 600; font-size: 13px;")
            lbl.setFixedWidth(72)
            row.addWidget(lbl)
            row.addWidget(widget, 1)
            return row

        # Board
        self.board_combo = QComboBox()
        self.board_combo.addItems(list(BOARDS.keys()))
        idx = self.board_combo.findText(self.cfg.board)
        if idx >= 0:
            self.board_combo.setCurrentIndex(idx)
        self.board_combo.currentTextChanged.connect(self._rebuild_partition_ui)
        right_col.addLayout(_field_row("Board:", self.board_combo))

        # Flash
        self._flash_combo = QComboBox()
        self._flash_combo.addItems(["4MB", "8MB", "16MB"])
        info = BOARDS.get(self.cfg.board, {})
        default_flash = info.get("flash_size", "4MB")
        if self.cfg.flash_size_override:
            default_flash = self.cfg.flash_size_override
        fi = self._flash_combo.findText(default_flash)
        if fi >= 0:
            self._flash_combo.setCurrentIndex(fi)
        self._flash_combo.currentTextChanged.connect(self._rebuild_partition_ui)
        right_col.addLayout(_field_row("Flash:", self._flash_combo))

        # Scheme
        self._scheme_combo = QComboBox()
        self._scheme_combo.currentTextChanged.connect(self._rebuild_partition_ui)
        right_col.addLayout(_field_row("Scheme:", self._scheme_combo))

        right_col.addSpacing(2)

        # Name
        self.name_edit = QLineEdit(self.cfg.device_name or "My ESP32")
        right_col.addLayout(_field_row("Name:", self.name_edit))

        # SSID
        self.ssid_edit = QLineEdit(self.cfg.wifi_ssid)
        self.ssid_edit.setPlaceholderText("Network name")
        right_col.addLayout(_field_row("Wi-Fi:", self.ssid_edit))

        # Password — required field with prominent indicator
        pass_row = QHBoxLayout()
        pass_lbl = QLabel("Password: *")
        pass_lbl.setStyleSheet(
            f"color: {C['text_muted']}; font-weight: 600; font-size: 13px;"
        )
        pass_lbl.setFixedWidth(72)
        pass_row.addWidget(pass_lbl)
        self.pass_edit = QLineEdit(self.cfg.wifi_password)
        self.pass_edit.setEchoMode(QLineEdit.EchoMode.Password)
        self.pass_edit.setPlaceholderText("Required to flash")
        self.pass_edit.textChanged.connect(self._validate_password)
        pass_row.addWidget(self.pass_edit, 1)
        right_col.addLayout(pass_row)

        # Inline password hint — visible only when empty
        self._pass_hint = QLabel("  ⚠  Wi-Fi password is required to flash wirelessly")
        self._pass_hint.setStyleSheet(
            f"color: {C['warning']}; font-size: 11px; padding-left: 76px;"
        )
        self._pass_hint.setVisible(not bool(self.cfg.wifi_password))
        right_col.addWidget(self._pass_hint)

        self._refresh_pass_style()

        right_col.addStretch()
        card_layout.addLayout(right_col, 1)   # stretch=1 so it takes all remaining width

        layout.addWidget(card)

        self._rebuild_partition_ui()

        # Libraries
        if self.cfg.libraries:
            lib_title = QLabel("Libraries needed:")
            lib_title.setStyleSheet(f"font-weight: 600; color: {C['text']}; font-size: 15px;")
            layout.addWidget(lib_title)
            for i, lib in enumerate(self.cfg.libraries):
                status = "✓" if lib.available else "⬇"
                color = C['success'] if lib.available else C['warning']
                lbl = SlideLabel(f"  {status}  {lib.name}")
                lbl.setStyleSheet(f"color: {color}; font-size: 15px;")
                if lib.available:
                    lbl.setToolTip("This library is already installed.")
                else:
                    lbl.setToolTip("I'll install this library before compiling.")
                lbl.animate_in(i * 80)
                layout.addWidget(lbl)

        # OTA conflict auto-fix
        if self.cfg.has_ota_conflict:
            warn = QFrame()
            warn.setObjectName("card")
            warn.setStyleSheet(
                f"QFrame#card {{ background: #FFF8EE; "
                f"border-color: {C['warning']}; }}"
            )
            wl = QVBoxLayout(warn)
            wl.setContentsMargins(14, 10, 14, 10)
            wl.setSpacing(4)
            wt = QLabel("⚠️  I found old OTA code in your sketch.")
            wt.setStyleSheet(f"color: {C['warning']}; font-weight: 600; font-size: 14px;")
            wb = QLabel(
                "EasyESP handles updates wirelessly for you. "
                "I'll remove the ArduinoOTA section automatically."
            )
            wb.setWordWrap(True)
            wb.setStyleSheet(f"color: {C['text_muted']}; font-size: 13px;")
            wl.addWidget(wt)
            wl.addWidget(wb)
            layout.addWidget(warn)

        # ── Wiring diagram ────────────────────────────────────
        if self.cfg.detected_pins or self.cfg.wiring_suggestions:
            wiring_card = QFrame()
            wiring_card.setObjectName("card")
            wc = QVBoxLayout(wiring_card)
            wc.setContentsMargins(16, 14, 16, 14)
            wc.setSpacing(8)

            wiring_title = QLabel("🔌  Wiring — what to connect where")
            wiring_title.setStyleSheet(f"font-weight: 700; font-size: 15px; color: {C['text']};")
            wc.addWidget(wiring_title)

            self._wiring_diagram = WiringDiagram(self.cfg.board)
            self._wiring_diagram.set_data(
                self.cfg.board,
                [{"gpio": p.gpio, "name": p.name, "direction": p.direction}
                 for p in self.cfg.detected_pins],
                [{"component": s.component, "pins": s.pins, "protocol": s.protocol,
                  "library": s.library, "notes": s.notes, "color": s.color}
                 for s in self.cfg.wiring_suggestions],
            )
            self._wiring_diagram.setMinimumHeight(260)
            wc.addWidget(self._wiring_diagram)

            for s in self.cfg.wiring_suggestions:
                row = QHBoxLayout()
                row.setSpacing(8)
                dot = QLabel()
                dot.setFixedSize(10, 10)
                dot.setStyleSheet(
                    f"background: {s.color}; border-radius: 5px; margin-top: 4px;"
                )
                row.addWidget(dot, alignment=Qt.AlignmentFlag.AlignTop)

                text_col = QVBoxLayout()
                text_col.setSpacing(1)
                comp_label = QLabel(s.component)
                comp_label.setStyleSheet(f"font-weight: 600; font-size: 13px; color: {C['text']};")
                text_col.addWidget(comp_label)

                for pin_name, pin_gpio in s.pins:
                    pin_str = f"GPIO{pin_gpio}" if isinstance(pin_gpio, int) else str(pin_gpio)
                    pin_label = QLabel(f"  {pin_name} → {pin_str}")
                    pin_label.setStyleSheet(f"font-size: 12px; color: {C['text_muted']};")
                    text_col.addWidget(pin_label)

                if s.notes:
                    notes_label = QLabel(f"  💡 {s.notes}")
                    notes_label.setWordWrap(True)
                    notes_label.setStyleSheet(f"font-size: 11px; color: {C['text_faint']};")
                    text_col.addWidget(notes_label)

                row.addLayout(text_col, 1)
                wc.addLayout(row)

            layout.addWidget(wiring_card)

        # Warnings
        for w in self.cfg.warnings:
            wl = QLabel(f"  {w}")
            wl.setWordWrap(True)
            wl.setStyleSheet(f"color: {C['warning']}; font-size: 14px;")
            layout.addWidget(wl)

        layout.addStretch(1)

    def _validate_password(self):
        has_pw = bool(self.pass_edit.text())
        self._flash_btn.setEnabled(has_pw)
        self._pass_hint.setVisible(not has_pw)
        self._refresh_pass_style()

    def _refresh_pass_style(self):
        if not self.pass_edit.text():
            self.pass_edit.setStyleSheet(
                f"QLineEdit {{ border: 1.5px solid {C['warning']}; border-radius: 6px; "
                f"padding: 4px 8px; background: #FFFAF5; }}"
                f"QLineEdit:focus {{ border-color: {C['accent']}; background: white; }}"
            )
        else:
            self.pass_edit.setStyleSheet(
                f"QLineEdit {{ border: 1.5px solid {C['border']}; border-radius: 6px; "
                f"padding: 4px 8px; background: white; }}"
                f"QLineEdit:focus {{ border-color: {C['accent']}; }}"
            )

    def _rebuild_partition_ui(self):
        from PyQt6.QtGui import QPixmap

        # Update board illustration from current combo
        board_name = self.board_combo.currentText()
        info = BOARDS.get(board_name, {})
        fn = BOARD_ILLUSTRATIONS.get(board_name)
        if fn:
            pm = QPixmap()
            pm.loadFromData(fn(150).encode())
            self._board_ill.setPixmap(pm)
        else:
            self._board_ill.clear()

        # Sync flash combo to parsed/overridden value, else board default
        board_default = self.cfg.flash_size_override or self.cfg.flash_size or info.get("flash_size", "4MB")
        if self._flash_combo.currentText() != board_default:
            self._flash_combo.blockSignals(True)
            fi = self._flash_combo.findText(board_default)
            if fi >= 0:
                self._flash_combo.setCurrentIndex(fi)
            self._flash_combo.blockSignals(False)

        # Rebuild scheme combo for the selected flash size
        flash = self._flash_combo.currentText()
        self._scheme_combo.blockSignals(True)
        self._scheme_combo.clear()
        schemes = PARTITION_SCHEMES.get(flash, {})
        for key, (label, desc, _parts) in schemes.items():
            self._scheme_combo.addItem(f"{label} — {desc}", key)
        # Restore previously selected scheme if valid, else pick first
        for i in range(self._scheme_combo.count()):
            if self._scheme_combo.itemData(i) == self.cfg.partition_scheme:
                self._scheme_combo.setCurrentIndex(i)
                break
        else:
            if self._scheme_combo.count():
                self._scheme_combo.setCurrentIndex(0)
        self._scheme_combo.blockSignals(False)

        self._update_partition_table()

    def _update_partition_table(self):
        flash = self._flash_combo.currentText()
        scheme_key = self._scheme_combo.currentData() or "default_ota"
        parts = get_scheme_partitions(flash, scheme_key)

        board_name = self.board_combo.currentText()
        info = BOARDS.get(board_name, {})
        chip = info.get("chip", "?")
        sketch = info.get("max_sketch_size", 0)
        sketch_mb = f"{sketch / 1024 / 1024:.1f} MB" if sketch else "?"
        scheme_label = scheme_key.replace("_", " ").title()

        lines = [
            f"Chip: {chip} · {flash} · {scheme_label}",
            "",
        ]
        for p in parts:
            lines.append(f"  {p['name']:<18} {p['offset']:>8}  {p['size']:>6}")
        if self.cfg.partition_csv_override:
            lines.append("")
            lines.append("  ⚡ Custom CSV override active")
        self._part_table.setText("\n".join(lines))

    def _open_partition_editor(self):
        self.cfg.board = self.board_combo.currentText()
        self.cfg.flash_size_override = self._flash_combo.currentText()
        self.cfg.partition_scheme = self._scheme_combo.currentData() or "default_ota"
        editor = PartitionEditor(self.cfg, self)
        editor.applied.connect(self._on_partitions_applied)
        editor.exec()

    def _on_partitions_applied(self, cfg: InoConfig):
        self.cfg = cfg
        # Sync combos to the edited cfg
        fi = self._flash_combo.findText(cfg.flash_size_override or cfg.flash_size)
        if fi >= 0:
            self._flash_combo.setCurrentIndex(fi)
        self._rebuild_partition_ui()

    def _confirm(self):
        self.cfg.board = self.board_combo.currentText()
        self.cfg.flash_size_override = self._flash_combo.currentText()
        self.cfg.partition_scheme = self._scheme_combo.currentData() or "default_ota"
        self.cfg.device_name = self.name_edit.text().strip()
        self.cfg.wifi_ssid = self.ssid_edit.text().strip()
        self.cfg.wifi_password = self.pass_edit.text()
        self.confirmed.emit(self.cfg)
        self.accept()
