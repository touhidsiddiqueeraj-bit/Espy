from __future__ import annotations
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QComboBox, QFrame, QPlainTextEdit, QCheckBox,
)
from PyQt6.QtCore import Qt, pyqtSignal

from palette import WARM_PASTEL as C, stylesheet
from constants import (
    PARTITION_SCHEMES, get_scheme_partitions,
    get_default_scheme,
)
from models import InoConfig


def partitions_to_csv(parts: list[dict]) -> str:
    lines = [
        "# EasyESP partition table",
        "# Name,         Type, SubType, Offset,   Size,     Flags",
    ]
    csv_map = {
        "nvs": ("data", "nvs"),
        "otadata": ("data", "ota"),
        "OTA Data": ("data", "ota"),
        "App (OTA 0)": ("app", "ota_0"),
        "app0": ("app", "ota_0"),
        "App (OTA 1)": ("app", "ota_1"),
        "app1": ("app", "ota_1"),
        "App": ("app", "ota_0"),
        "SPIFFS": ("data", "spiffs"),
        "LittleFS": ("data", "spiffs"),
        "Bootloader": ("app", "boot"),
        "Partition Table": ("data", "undefined"),
        "NVS": ("data", "nvs"),
        "easyesp_data": ("data", "nvs"),
    }
    offset_map = {
        "Bootloader": "0x1000",
        "NVS": "0x9000",
        "OTA Data": "0xE000",
        "otadata": "0x4000",
        "App (OTA 0)": "0x10000",
        "app0": "0x6000",
        "App": "0x10000",
    }
    for p in parts:
        name = p["name"]
        t, st = csv_map.get(name, ("data", "nvs"))
        off = p["offset"]
        sz = p["size"]
        sz_hex = _size_to_hex(sz)
        lines.append(f"{name.lower().replace(' ', '_')},{t},{st},{off},{sz_hex},")
    return "\n".join(lines)


def _size_to_hex(size_str: str) -> str:
    size_str = size_str.strip()
    if size_str.endswith("MB"):
        val = float(size_str.replace("MB", "").strip())
        return f"0x{int(val * 1024 * 1024):X}"
    elif size_str.endswith("KB"):
        val = float(size_str.replace("KB", "").strip())
        return f"0x{int(val * 1024):X}"
    elif size_str.endswith("B"):
        val = int(size_str.replace("B", "").strip())
        return f"0x{val:X}"
    return size_str


def csv_to_partitions(csv_text: str) -> list[dict]:
    parts = []
    for line in csv_text.strip().split("\n"):
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        fields = [f.strip() for f in line.split(",")]
        if len(fields) < 5:
            continue
        name, t, st, offset, size = fields[:5]
        size_friendly = _hex_to_friendly(size)
        parts.append({
            "name": name.replace("_", " ").title().replace("Nvs", "NVS").replace("Ota", "OTA").replace("Spiffs", "SPIFFS"),
            "offset": offset,
            "size": size_friendly,
        })
    return parts


def _hex_to_friendly(hex_size: str) -> str:
    try:
        val = int(hex_size, 16)
        if val >= 1024 * 1024:
            return f"{val / (1024 * 1024):.1f} MB"
        elif val >= 1024:
            return f"{val // 1024} KB"
        else:
            return f"{val} B"
    except ValueError:
        return hex_size


def get_max_sketch_size(flash_size: str, parts: list[dict]) -> int:
    total = 0
    for p in parts:
        sz = p["size"]
        try:
            if sz.endswith("MB"):
                total += int(float(sz.replace("MB", "")) * 1024 * 1024)
            elif sz.endswith("KB"):
                total += int(sz.replace("KB", "")) * 1024
            elif p["offset"] == "0x10000":
                continue
        except ValueError:
            pass
    return total


class PartitionEditor(QDialog):
    applied = pyqtSignal(InoConfig)

    FLASH_SIZE_OPTIONS = ["4MB", "8MB", "16MB"]

    def __init__(self, cfg: InoConfig, parent=None):
        super().__init__(parent)
        self.cfg = cfg
        self._manual_mode = False
        self.setWindowTitle("Partition Editor")
        self.setMinimumWidth(640)
        self.setMinimumHeight(560)
        self.setStyleSheet(stylesheet())
        self._build_ui()
        self._sync_from_cfg()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(16)
        layout.setContentsMargins(24, 20, 24, 20)

        title = QLabel("Partition Layout")
        title.setStyleSheet(f"font-size: 20px; font-weight: 700; color: {C['text']};")
        layout.addWidget(title)

        desc = QLabel(
            "Partitions divide the flash memory into sections. "
            "Choose a preset or edit the CSV manually."
        )
        desc.setWordWrap(True)
        desc.setStyleSheet(f"color: {C['text_muted']}; font-size: 14px;")
        layout.addWidget(desc)

        # Flash size row
        fs_row = QHBoxLayout()
        fs_label = QLabel("Flash Size:")
        fs_label.setStyleSheet(f"font-weight: 600; color: {C['text']};")
        self.flash_size_combo = QComboBox()
        self.flash_size_combo.addItems(self.FLASH_SIZE_OPTIONS)
        self.flash_size_combo.currentTextChanged.connect(self._on_flash_size_changed)
        fs_row.addWidget(fs_label)
        fs_row.addWidget(self.flash_size_combo, 1)
        layout.addLayout(fs_row)

        # Scheme row
        scheme_row = QHBoxLayout()
        scheme_label = QLabel("Scheme:")
        scheme_label.setStyleSheet(f"font-weight: 600; color: {C['text']};")
        self.scheme_combo = QComboBox()
        self.scheme_combo.currentIndexChanged.connect(self._on_scheme_changed)
        scheme_row.addWidget(scheme_label)
        scheme_row.addWidget(self.scheme_combo, 1)
        layout.addLayout(scheme_row)

        # Scheme description
        self._scheme_desc = QLabel()
        self._scheme_desc.setWordWrap(True)
        self._scheme_desc.setStyleSheet(f"color: {C['text_muted']}; font-size: 13px; padding: 0 0 6px 0;")
        layout.addWidget(self._scheme_desc)

        # Manual CSV toggle
        toggle_row = QHBoxLayout()
        self._manual_toggle = QCheckBox("Edit partition table directly (CSV)")
        self._manual_toggle.setStyleSheet(
            f"font-size: 14px; color: {C['text_muted']};"
        )
        self._manual_toggle.toggled.connect(self._on_manual_toggled)
        toggle_row.addWidget(self._manual_toggle)
        toggle_row.addStretch()
        layout.addLayout(toggle_row)

        # Partition table view (read-only)
        self._table_label = QLabel()
        self._table_label.setWordWrap(True)
        self._table_label.setStyleSheet(
            f"color: {C['text_muted']}; font-size: 13px; "
            f"font-family: 'Ubuntu Mono', 'Consolas', monospace; "
            f"background: white; border: 1px solid {C['border']}; "
            f"border-radius: 8px; padding: 12px;"
        )
        layout.addWidget(self._table_label)

        # Manual CSV editor (hidden by default)
        self._csv_editor = QPlainTextEdit()
        self._csv_editor.setPlaceholderText(
            "# Name, Type, SubType, Offset, Size, Flags\n"
            "nvs, data, nvs, 0x1000, 0x3000,\n"
            "app0, app, ota_0, 0x6000, 0x1E0000,\n"
        )
        self._csv_editor.setMinimumHeight(160)
        self._csv_editor.textChanged.connect(self._on_csv_edited)
        self._csv_editor.hide()
        layout.addWidget(self._csv_editor)

        # Summary
        self._summary_label = QLabel()
        self._summary_label.setStyleSheet(
            f"color: {C['info']}; font-size: 13px; font-weight: 600;"
        )
        layout.addWidget(self._summary_label)

        layout.addStretch()

        # Buttons
        btn_row = QHBoxLayout()
        btn_row.addStretch()
        cancel = QPushButton("Cancel")
        cancel.setObjectName("secondary")
        cancel.clicked.connect(self.reject)

        apply = QPushButton("Apply")
        apply.setObjectName("primary")
        apply.clicked.connect(self._apply)

        btn_row.addWidget(cancel)
        btn_row.addWidget(apply)
        layout.addLayout(btn_row)

    def _sync_from_cfg(self):
        fs = self.cfg.flash_size_override or self.cfg.flash_size
        if fs in self.FLASH_SIZE_OPTIONS:
            self.flash_size_combo.setCurrentText(fs)
        self._refresh_scheme_combo(fs)
        scheme = self.cfg.partition_scheme
        idx = self.scheme_combo.findData(scheme)
        if idx >= 0:
            self.scheme_combo.setCurrentIndex(idx)
        if self.cfg.partition_csv_override:
            self._manual_toggle.setChecked(True)
            self._csv_editor.setPlainText(self.cfg.partition_csv_override)

    def _refresh_scheme_combo(self, flash_size: str):
        self.scheme_combo.blockSignals(True)
        self.scheme_combo.clear()
        schemes = PARTITION_SCHEMES.get(flash_size, {})
        for key, (label, desc, _) in schemes.items():
            self.scheme_combo.addItem(label, userData=key)
        self.scheme_combo.blockSignals(False)
        if self.scheme_combo.count() > 0:
            self.scheme_combo.setCurrentIndex(0)
        self._on_scheme_changed()

    def _on_flash_size_changed(self, fs: str):
        self._refresh_scheme_combo(fs)

    def _on_scheme_changed(self):
        fs = self.flash_size_combo.currentText()
        key = self.scheme_combo.currentData()
        schemes = PARTITION_SCHEMES.get(fs, {})
        scheme = schemes.get(key)
        if scheme:
            _, desc, parts = scheme
            self._scheme_desc.setText(desc)
            self._show_partitions(parts)
            self._update_summary(parts)
        self._sync_csv_from_scheme()

    def _on_manual_toggled(self, checked: bool):
        self._manual_mode = checked
        self.scheme_combo.setEnabled(not checked)
        self._table_label.setVisible(not checked)
        self._csv_editor.setVisible(checked)
        if checked:
            self._sync_csv_from_scheme()

    def _sync_csv_from_scheme(self):
        fs = self.flash_size_combo.currentText()
        key = self.scheme_combo.currentData()
        parts = get_scheme_partitions(fs, key)
        csv = partitions_to_csv(parts)
        self._csv_editor.setPlainText(csv)

    def _on_csv_edited(self):
        if self._manual_mode:
            try:
                parts = csv_to_partitions(self._csv_editor.toPlainText())
                self._show_partitions(parts)
                self._update_summary(parts)
            except Exception:
                pass

    def _show_partitions(self, parts: list[dict]):
        lines = []
        lines.append(f"{'Name':<20} {'Offset':>10}  {'Size':>8}")
        lines.append("-" * 42)
        for p in parts:
            lines.append(f"{p['name']:<20} {p['offset']:>10}  {p['size']:>8}")
        self._table_label.setText("\n".join(lines))

    def _update_summary(self, parts: list[dict]):
        app_partitions = [p for p in parts if "ota" in p["name"].lower() or p["name"] == "App"]
        total_app = 0
        for p in app_partitions:
            s = p["size"]
            try:
                if s.endswith("MB"):
                    total_app += int(float(s.replace("MB", "")) * 1024 * 1024)
                elif s.endswith("KB"):
                    total_app += int(s.replace("KB", "")) * 1024
            except ValueError:
                pass
        if total_app:
            mb = total_app / (1024 * 1024)
            self._summary_label.setText(
                f"Total app space: {mb:.1f} MB  ·  "
                f"{len(app_partitions)} app partition{'s' if len(app_partitions) > 1 else ''}"
            )

    def _get_current_parts(self) -> list[dict]:
        if self._manual_mode:
            return csv_to_partitions(self._csv_editor.toPlainText())
        else:
            fs = self.flash_size_combo.currentText()
            key = self.scheme_combo.currentData()
            return get_scheme_partitions(fs, key)

    def _apply(self):
        self.cfg.flash_size_override = self.flash_size_combo.currentText()
        if self._manual_mode:
            self.cfg.partition_scheme = self.scheme_combo.currentData()
            self.cfg.partition_csv_override = self._csv_editor.toPlainText()
        else:
            self.cfg.partition_scheme = self.scheme_combo.currentData()
            self.cfg.partition_csv_override = ""
        self.applied.emit(self.cfg)
        self.accept()
