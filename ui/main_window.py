from __future__ import annotations
import sys
from typing import Optional
from pathlib import Path

from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QComboBox, QStackedWidget,
    QListWidget, QListWidgetItem, QFrame, QSizePolicy,
    QMessageBox, QProgressBar, QPlainTextEdit,
)
from PyQt6.QtCore import Qt, QSize, QTimer, pyqtSignal
from PyQt6.QtGui import QPixmap, QIcon, QMouseEvent, QFont


class ClickableLabel(QLabel):
    clicked = pyqtSignal()
    def mouseReleaseEvent(self, e: QMouseEvent):
        if e.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit()
        super().mouseReleaseEvent(e)

from palette import WARM_PASTEL as C, stylesheet
from constants import APP_NAME, APP_VERSION, MODE_PREF_FILE, BOARDS
from models import Device, InoConfig
from parser import parse_ino
from discovery.engine import DiscoveryEngine
from ui.drop_zone import DropZone
from ui.device_list import DeviceItemWidget
from ui.config_dialog import ConfigDialog
from ui.progress_scene import ProgressScene
from ui.setup_wizard import SetupWizard
from ui.easy_overlay import EasyOverlay
from ui.serial_logger import SerialLogger
from ui.illustrations import espy_icon_24, espy_svg_tag
from ui.board_picker import BoardPickerDialog
from ui.animations import BouncyMascot, BreathingDot, BlinkingLED
from examples import get_blink_code, get_led_pin
from workers.compiler import CompilerWorker
from workers.ota import OtaWorker


class MainWindow(QMainWindow):
    mode_changed = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.setWindowTitle(f"Espy — Flash your ESP32 in one click")
        self.setMinimumSize(900, 700)
        self.resize(1024, 740)
        self.setStyleSheet(stylesheet())

        self._devices: dict[str, Device] = {}
        self._selected_device: Optional[Device] = None
        self._pending_bin: Optional[str] = None
        self._pending_cfg: Optional[InoConfig] = None
        self._compiler: Optional[CompilerWorker] = None
        self._ota: Optional[OtaWorker] = None
        self._batch_ino_path: str = ""
        self._batch_queue: list[Device] = []
        self._batch_index: int = 0
        self._example_tmp_path: str = ""

        self._easy_mode = True

        self._manual_board = "ESP32 Dev Module"
        self._build_ui()
        self._start_discovery()

    def _build_ui(self):
        root = QWidget()
        root_layout = QHBoxLayout(root)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)
        self.setCentralWidget(root)

        # Sidebar
        self._sidebar = self._make_sidebar()
        root_layout.addWidget(self._sidebar)

        # Divider
        div = QFrame()
        div.setFrameShape(QFrame.Shape.VLine)
        div.setStyleSheet(f"color: {C['border']};")
        root_layout.addWidget(div)

        # Main content
        self._stack = QStackedWidget()
        main_page = self._make_main_page()
        self._stack.addWidget(main_page)      # 0
        QTimer.singleShot(0, self._update_example_code)
        self._stack.addWidget(self._make_flash_page())     # 1
        self._serial_logger = SerialLogger()
        self._serial_logger.closed.connect(lambda: self._stack.setCurrentIndex(0))
        self._stack.addWidget(self._serial_logger)         # 2
        root_layout.addWidget(self._stack, 1)

        # Easy Mode overlay
        self._easy_overlay = EasyOverlay()
        self._easy_overlay.setVisible(False)
        self._easy_overlay.switch_to_advanced.connect(self._switch_to_advanced)
        self._easy_overlay.file_selected.connect(self._on_ino_received)
        self._easy_overlay.start_setup.connect(self._show_setup_wizard)
        self._easy_overlay.plug_connected.connect(self._on_plug_connected)
        self._easy_overlay.device_selected.connect(self._on_easy_device_selected)
        root_layout.addWidget(self._easy_overlay)

        if self._easy_mode:
            self._show_easy_mode()
            QTimer.singleShot(100, self._check_mode_pref)

    def _check_mode_pref(self):
        if MODE_PREF_FILE.exists():
            pref = MODE_PREF_FILE.read_text().strip()
            if pref == "advanced":
                self._switch_to_advanced()

    def _make_sidebar(self):
        sidebar = QWidget()
        sidebar.setObjectName("sidebar")
        sidebar.setFixedWidth(250)

        layout = QVBoxLayout(sidebar)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Logo area with mascot
        logo_area = QWidget()
        logo_area.setFixedHeight(70)
        logo_area.setStyleSheet(f"border-bottom: 1px solid {C['border']};")
        ll = QHBoxLayout(logo_area)
        ll.setContentsMargins(16, 0, 16, 0)

        self._logo_mascot = BouncyMascot()
        self._logo_mascot.set_mood("happy", 28)
        self._logo_mascot.setFixedSize(28, 34)
        self._logo_mascot.start_bounce()
        ll.addWidget(self._logo_mascot)

        logo_txt = QLabel("Espy")
        logo_txt.setStyleSheet(
            f"font-size: 19px; font-weight: 800; color: {C['accent']};"
            f"background: transparent;"
        )
        ll.addWidget(logo_txt)
        layout.addWidget(logo_area)

        # Section header
        dev_header = QLabel("  MY DEVICES")
        dev_header.setObjectName("section_title")
        layout.addWidget(dev_header)

        # Device list
        self._device_list = QListWidget()
        self._device_list.setStyleSheet(
            f"QListWidget {{ background: transparent; border: none; }}"
            f"QListWidget::item:selected {{ background: {C['card']}; }}"
            f"QListWidget::item:hover {{ background: {C['card_hover']}; }}"
        )
        self._device_list.itemClicked.connect(self._on_device_selected)
        layout.addWidget(self._device_list, 1)

        # Batch flash bar
        self._batch_bar = QProgressBar()
        self._batch_bar.setMinimum(0)
        self._batch_bar.setMaximum(100)
        self._batch_bar.setTextVisible(True)
        self._batch_bar.hide()
        layout.addWidget(self._batch_bar)

        # Bottom buttons
        btn_area = QWidget()
        btn_area.setStyleSheet(f"border-top: 1px solid {C['border']};")
        bl = QVBoxLayout(btn_area)
        bl.setContentsMargins(12, 12, 12, 12)
        bl.setSpacing(8)

        self._batch_btn = QPushButton("Flash Selected (0)")
        self._batch_btn.setObjectName("primary")
        self._batch_btn.setEnabled(False)
        self._batch_btn.clicked.connect(self._start_batch_flash)
        self._batch_btn.setToolTip("Flash code to all selected devices (one at a time)")
        self._batch_btn.hide()
        bl.addWidget(self._batch_btn)

        self._serial_btn = QPushButton("Serial Monitor")
        self._serial_btn.setObjectName("secondary")
        self._serial_btn.clicked.connect(self._show_serial_logger)
        self._serial_btn.setToolTip("Open serial monitor (USB or Wi-Fi)")
        bl.addWidget(self._serial_btn)

        add_btn = QPushButton("+ Add device")
        add_btn.setObjectName("secondary")
        add_btn.clicked.connect(self._show_setup_wizard)
        add_btn.setToolTip("Set up a new ESP32 via USB")
        bl.addWidget(add_btn)

        # Mascot icon replaces 🌻
        mode_btn = QPushButton("  Easy Mode")
        mode_btn.setObjectName("ghost")
        mode_btn.setIcon(QIcon())
        mode_btn.clicked.connect(self._toggle_mode)
        mode_btn.setToolTip("Switch between Easy and Advanced modes")
        bl.addWidget(mode_btn)

        layout.addWidget(btn_area)
        return sidebar

    def _make_main_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(32, 28, 32, 28)
        layout.setSpacing(16)

        # ── Device status banner ─────────────────────────────
        self._status_banner = QFrame()
        self._status_banner.setObjectName("card")
        self._status_banner.setStyleSheet(
            f"QFrame#card {{ background: {C['card']}; border-color: {C['border']}; }}"
        )
        banner_layout = QHBoxLayout(self._status_banner)
        banner_layout.setContentsMargins(16, 12, 16, 12)
        banner_layout.setSpacing(10)

        self._status_dot = BreathingDot()
        self._status_dot.set_online(False)
        banner_layout.addWidget(self._status_dot)

        self._status_text = QLabel("Looking for devices on your network...")
        self._status_text.setStyleSheet(f"color: {C['text_muted']}; font-size: 15px; background: transparent;")
        banner_layout.addWidget(self._status_text, 1)

        self._setup_btn = QPushButton("  Set up new ESP32 →")
        self._setup_btn.setObjectName("secondary")
        self._setup_btn.setFixedWidth(220)
        self._setup_btn.clicked.connect(self._show_setup_wizard)
        self._setup_btn.hide()
        banner_layout.addWidget(self._setup_btn)
        layout.addWidget(self._status_banner)

        # ── Header row with board pill button ──────────
        header = QHBoxLayout()
        header.setSpacing(10)
        title = QLabel("Drop your code here")
        title.setStyleSheet(f"font-size: 22px; font-weight: 700; color: {C['text']};")
        header.addWidget(title)
        header.addStretch()

        # Unified board pill button — whole area is clickable
        self._board_pill = QPushButton()
        self._board_pill.setCursor(Qt.CursorShape.PointingHandCursor)
        self._board_pill.setToolTip("Click to change board or partition settings")
        self._board_pill.setFixedHeight(36)
        self._board_pill.setStyleSheet(
            f"QPushButton {{"
            f"  font-size: 13px; font-weight: 600; color: {C['accent']};"
            f"  background: {C['card']}; border: 1px solid {C['border']};"
            f"  border-radius: 18px; padding: 0 16px;"
            f"}}"
            f"QPushButton:hover {{"
            f"  background: {C['card_hover']}; border-color: {C['accent']};"
            f"}}"
            f"QPushButton:pressed {{"
            f"  background: {C['card_hover']};"
            f"}}"
        )
        self._board_pill.clicked.connect(self._open_board_picker)
        # Store board name separately so label can include chip/flash info
        self._manual_board = "ESP32 Dev Module"
        header.addWidget(self._board_pill)

        # Small "Edit partitions" link button
        self._part_btn = QPushButton("⚙ Partitions")
        self._part_btn.setObjectName("ghost")
        self._part_btn.setFixedHeight(36)
        self._part_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self._part_btn.setToolTip("Change flash size, partition scheme, or edit partition table")
        self._part_btn.setStyleSheet(
            f"QPushButton {{"
            f"  font-size: 12px; color: {C['text_muted']};"
            f"  background: transparent; border: 1px solid {C['border']};"
            f"  border-radius: 18px; padding: 0 14px;"
            f"}}"
            f"QPushButton:hover {{"
            f"  background: {C['card']}; color: {C['text']}; border-color: {C['accent']};"
            f"}}"
        )
        self._part_btn.clicked.connect(self._open_partition_settings)
        header.addWidget(self._part_btn)
        layout.addLayout(header)

        # ── Example code card (compact hint bar) ─────────────
        self._example_card = QFrame()
        self._example_card.setObjectName("card")
        self._example_card.setStyleSheet(
            f"QFrame#card {{ background: {C['card']}; border: 1px solid {C['border']}; border-radius: 12px; }}"
        )
        self._example_card.hide()
        ec = QHBoxLayout(self._example_card)
        ec.setContentsMargins(16, 8, 16, 8)
        ec.setSpacing(8)

        self._example_led = BlinkingLED()
        ec.addWidget(self._example_led)

        ec_title = QLabel("Blink")
        ec_title.setStyleSheet(f"font-size: 14px; font-weight: 700; color: {C['text']};")
        ec.addWidget(ec_title)

        board_hint = QLabel()
        board_hint.setStyleSheet(f"font-size: 12px; color: {C['text_muted']}; background: transparent;")
        self._example_board_hint = board_hint
        ec.addWidget(board_hint)
        ec.addStretch()

        self._flash_example_btn = QPushButton("⚡ Flash")
        self._flash_example_btn.setObjectName("primary")
        self._flash_example_btn.setFixedHeight(28)
        self._flash_example_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self._flash_example_btn.clicked.connect(self._flash_example_code)
        ec.addWidget(self._flash_example_btn)

        self._save_example_btn = QPushButton("💾 Save")
        self._save_example_btn.setObjectName("ghost")
        self._save_example_btn.setFixedHeight(28)
        self._save_example_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self._save_example_btn.clicked.connect(self._save_example_ino)
        ec.addWidget(self._save_example_btn)

        layout.addWidget(self._example_card)

        # Keep a hidden QLabel so existing code that reads self._board_label.text() still works
        self._board_label = QLabel("ESP32 Dev Module")
        self._board_label.hide()

        # ── Code input mode toggle ────────────────────────────
        mode_row = QHBoxLayout()
        mode_row.setSpacing(4)

        self._drop_mode_btn = QPushButton("📁  Drop file")
        self._drop_mode_btn.setObjectName("ghost")
        self._drop_mode_btn.setFixedHeight(28)
        self._drop_mode_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self._drop_mode_btn.setStyleSheet(
            f"QPushButton {{ font-size: 12px; font-weight: 700; color: {C['accent']}; "
            f"background: {C['card']}; border: 1px solid {C['accent']}; "
            f"border-radius: 14px; padding: 0 12px; }}"
            f"QPushButton:hover {{ background: {C['card_hover']}; }}"
        )
        self._drop_mode_btn.clicked.connect(lambda: self._switch_input_mode(0))
        mode_row.addWidget(self._drop_mode_btn)

        self._write_mode_btn = QPushButton("✏️  Write code")
        self._write_mode_btn.setObjectName("ghost")
        self._write_mode_btn.setFixedHeight(28)
        self._write_mode_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self._write_mode_btn.setStyleSheet(
            f"QPushButton {{ font-size: 12px; font-weight: 600; color: {C['text_muted']}; "
            f"background: transparent; border: 1px solid {C['border']}; "
            f"border-radius: 14px; padding: 0 12px; }}"
            f"QPushButton:hover {{ color: {C['accent']}; border-color: {C['accent']}; }}"
        )
        self._write_mode_btn.clicked.connect(lambda: self._switch_input_mode(1))
        mode_row.addWidget(self._write_mode_btn)

        mode_row.addStretch()
        layout.addLayout(mode_row)

        # ── Input stacked widget: DropZone / Code editor ─────
        self._input_stack = QStackedWidget()

        self._drop_zone = DropZone()
        self._drop_zone.file_dropped.connect(self._on_ino_received)
        self._drop_zone.file_chosen.connect(self._on_ino_received)
        self._drop_zone.set_enabled(False)
        self._input_stack.addWidget(self._drop_zone)

        editor_page = QWidget()
        editor_layout = QVBoxLayout(editor_page)
        editor_layout.setContentsMargins(0, 0, 0, 0)
        editor_layout.setSpacing(8)

        self._code_editor = QPlainTextEdit()
        self._code_editor.setPlaceholderText(
            "// Paste or write your Arduino sketch here...\n\n"
            "void setup() {\n"
            "  Serial.begin(115200);\n"
            "}\n\n"
            "void loop() {\n"
            "  Serial.println(\"Hello, ESP32!\");\n"
            "  delay(1000);\n"
            "}"
        )
        self._code_editor.setStyleSheet(
            f"QPlainTextEdit {{"
            f"  font-family: 'Ubuntu Mono', 'Consolas', monospace;"
            f"  font-size: 14px;"
            f"  color: {C['text']};"
            f"  background: {C['bg']};"
            f"  border: 2px solid {C['border']};"
            f"  border-radius: 12px;"
            f"  padding: 12px;"
            f"  selection-background-color: {C['card']};"
            f"}}"
            f"QPlainTextEdit:focus {{"
            f"  border-color: {C['accent']};"
            f"}}"
        )
        editor_layout.addWidget(self._code_editor, 1)

        editor_btn_row = QHBoxLayout()
        editor_btn_row.setSpacing(8)

        self._compile_btn = QPushButton("⚡ Compile & Flash")
        self._compile_btn.setObjectName("primary")
        self._compile_btn.setFixedHeight(40)
        self._compile_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self._compile_btn.setEnabled(False)
        self._compile_btn.clicked.connect(self._on_compile_editor)
        editor_btn_row.addWidget(self._compile_btn)

        self._save_code_btn = QPushButton("💾 Save .ino")
        self._save_code_btn.setObjectName("secondary")
        self._save_code_btn.setFixedHeight(40)
        self._save_code_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self._save_code_btn.clicked.connect(self._on_save_editor_code)
        editor_btn_row.addWidget(self._save_code_btn)

        editor_btn_row.addStretch()
        editor_layout.addLayout(editor_btn_row)

        self._input_stack.addWidget(editor_page)
        layout.addWidget(self._input_stack, 1)

        self._status_card = QFrame()
        self._status_card.setObjectName("card")
        self._status_card.hide()
        sc = QVBoxLayout(self._status_card)
        sc.setContentsMargins(20, 16, 20, 16)
        sc.setSpacing(10)

        self._status_label = QLabel("")
        self._status_label.setStyleSheet(f"color: {C['text_muted']}; font-size: 16px;")
        self._progress_bar = QProgressBar()
        self._progress_bar.setRange(0, 100)
        self._progress_bar.setValue(0)
        self._progress_bar.setFixedHeight(16)
        self._progress_bar.setTextVisible(False)

        sc.addWidget(self._status_label)
        sc.addWidget(self._progress_bar)
        layout.addWidget(self._status_card)

        tip = QLabel(
            "Tip: Add // DEVICE_NAME: Kitchen Light at the top of your sketch "
            "for automatic naming when using your AI assistant."
        )
        tip.setWordWrap(True)
        tip.setStyleSheet(f"color: {C['text_faint']}; font-size: 15px; padding-top: 6px;")
        layout.addWidget(tip)

        return page

    def _make_flash_page(self):
        self._flash_scene = ProgressScene()
        self._flash_scene.save_binary_requested.connect(self._on_save_binary)
        self._flash_scene.flash_now_requested.connect(self._on_flash_now)
        return self._flash_scene

    def _start_discovery(self):
        self._discovery = DiscoveryEngine()
        self._discovery.found.connect(self._on_device_found)
        self._discovery.lost.connect(self._on_device_lost)
        self._discovery.phase_changed.connect(self._on_discovery_phase)
        self._discovery.start()

    def _on_device_found(self, name: str, ip: str, port: int):
        if name in self._devices:
            self._devices[name].ip = ip
            self._devices[name].last_seen = __import__("time").time()
        else:
            self._devices[name] = Device(name, ip, port)
        self._refresh_device_ui()
        self._update_device_status()
        self._easy_overlay.set_devices(list(self._devices.values()))
        self._easy_overlay.set_mascot_mood("happy")
        if self._pending_bin:
            self._flash_scene.set_flash_enabled(True)

    def _on_device_lost(self, name: str):
        if name in self._devices:
            del self._devices[name]
            self._refresh_device_ui()
        if self._selected_device and self._selected_device.name == name:
            self._selected_device = next(iter(self._devices.values())) if self._devices else None
        self._update_device_status()
        if not self._devices:
            self._easy_overlay.set_mascot_mood("sad")
        self._easy_overlay.set_devices(list(self._devices.values()))

    def _on_discovery_phase(self, msg: str):
        self._easy_overlay.set_status(msg)
        if not self._devices:
            self._status_text.setText(msg)

    def _update_partition_card(self):
        board = self._board_label.text() if hasattr(self, '_board_label') else "ESP32 Dev Module"
        info = BOARDS.get(board, {})
        flash = info.get("flash_size", "4MB")
        chip = info.get("chip", "ESP32")
        # Update the unified pill button text
        if hasattr(self, '_board_pill'):
            self._board_pill.setText(f"  {board}  ·  {chip} · {flash}  ▾")

    def _on_board_changed(self):
        self._manual_board = self._board_label.text()
        self._update_partition_card()
        self._update_example_code()

    def _update_example_code(self):
        board = self._board_label.text()
        if board not in BOARDS:
            self._example_card.hide()
            return
        pin = str(get_led_pin(board))
        info = BOARDS.get(board, {})
        chip = info.get("chip", "ESP32")
        flash = info.get("flash_size", "4MB")
        self._example_board_hint.setText(f"💡 Blink — GPIO {pin}  ·  {chip}  ·  {flash}")
        self._example_card.show()

    def _flash_example_code(self):
        board = self._board_label.text()
        if board not in BOARDS:
            return
        code = get_blink_code(board)
        import tempfile, os
        tmp = tempfile.NamedTemporaryFile(mode="w", suffix=".ino", delete=False, prefix="blink_")
        tmp.write(code)
        tmp_path = tmp.name
        tmp.close()
        self._example_tmp_path = tmp_path
        cfg = parse_ino(tmp_path)
        if not cfg.board or cfg.board not in BOARDS:
            cfg.board = board
            cfg.flash_size = BOARDS.get(board, {}).get("flash_size", "4MB")
        self._start_compile(tmp_path, cfg)

    def _save_example_ino(self):
        from PyQt6.QtWidgets import QFileDialog
        board = self._board_label.text()
        code = get_blink_code(board)
        path, _ = QFileDialog.getSaveFileName(
            self, "Save Blink Example", f"blink_{board.replace(' ', '_')}.ino",
            "Arduino files (*.ino);;All files (*)"
        )
        if path:
            with open(path, "w") as f:
                f.write(code)

    def _open_board_picker(self):
        dlg = BoardPickerDialog(self)
        if dlg.exec():
            board = dlg.selected_board()
            if board:
                self._board_label.setText(board)
                self._manual_board = board
                self._on_board_changed()

    def _open_partition_settings(self):
        from ui.partition_editor import PartitionEditor
        from models import InoConfig
        cfg = InoConfig()
        cfg.board = self._board_label.text()
        cfg.flash_size = BOARDS.get(cfg.board, {}).get("flash_size", "4MB")
        editor = PartitionEditor(cfg, self)
        editor.applied.connect(self._on_partition_settings_applied)
        editor.exec()

    def _on_partition_settings_applied(self, cfg):
        self._update_partition_card()

    def _refresh_device_ui(self):
        self._device_list.clear()
        multi = len(self._devices) > 1
        self._batch_btn.setVisible(multi)
        for name, device in self._devices.items():
            item = QListWidgetItem(self._device_list)
            widget = DeviceItemWidget(device, show_checkbox=multi)
            item.setSizeHint(QSize(0, 60))
            self._device_list.setItemWidget(item, widget)
            if multi:
                widget.checkbox_toggled.connect(self._update_batch_button)
        if multi:
            self._update_batch_button()

    def _update_device_status(self):
        count = len(self._devices)
        has_device = count > 0
        if count == 0:
            self._status_dot.set_online(False)
            self._status_text.setText("No devices found. Make sure your ESP32 is powered on and on the same Wi-Fi.")
            self._setup_btn.setText("Set up new ESP32 →")
            self._setup_btn.show()
            self._drop_zone.set_enabled(True)
            self._update_partition_card()
        else:
            self._status_dot.set_online(True)
            if self._selected_device:
                self._status_text.setText(
                    f"{count} device{'s' if count > 1 else ''} online · "
                    f"Selected: {self._selected_device.friendly_label}"
                )
            else:
                self._status_text.setText(f"{count} device{'s' if count > 1 else ''} found — select one to start")
                self._selected_device = next(iter(self._devices.values()))
            self._setup_btn.setText("+ Add another device")
            self._setup_btn.show()
            self._drop_zone.set_enabled(True)
            self._update_partition_card()
        self._compile_btn.setEnabled(has_device)

    def _on_device_selected(self, item: QListWidgetItem):
        row = self._device_list.row(item)
        name = list(self._devices.keys())[row]
        self._selected_device = self._devices[name]
        self._update_device_status()
        self._update_partition_card()

    # ── Batch flash ───────────────────────────────────────

    def _get_checked_devices(self) -> list[Device]:
        checked = []
        for i in range(self._device_list.count()):
            item = self._device_list.item(i)
            widget: DeviceItemWidget = self._device_list.itemWidget(item)
            if widget and widget.is_checked():
                checked.append(widget.device)
        return checked

    def _update_batch_button(self):
        checked = self._get_checked_devices()
        count = len(checked)
        self._batch_btn.setText(f"Flash Selected ({count})")
        self._batch_btn.setEnabled(count > 0)

    def _start_batch_flash(self):
        devices = self._get_checked_devices()
        if not devices:
            return
        self._batch_queue = list(devices)
        self._batch_index = 0
        self._batch_bar.show()
        self._batch_bar.setValue(0)
        self._batch_btn.setEnabled(False)
        self._process_next_batch()

    def _process_next_batch(self):
        if self._batch_index >= len(self._batch_queue):
            self._batch_bar.hide()
            self._batch_btn.setEnabled(True)
            self._update_batch_button()
            return

        device = self._batch_queue[self._batch_index]
        self._selected_device = device
        total = len(self._batch_queue)
        self._batch_bar.setFormat(
            f"Flashing {self._batch_index + 1}/{total}: {device.friendly_label} ..."
        )
        self._on_ino_received(self._batch_ino_path)

    def _advance_batch(self):
        self._batch_index += 1
        if self._batch_index < len(self._batch_queue):
            pct = int(self._batch_index / len(self._batch_queue) * 100)
            self._batch_bar.setValue(pct)
        QTimer.singleShot(800, self._process_next_batch)

    # ── INO handling ──────────────────────────────────────

    def _switch_input_mode(self, index: int):
        self._input_stack.setCurrentIndex(index)
        active = f"QPushButton {{ font-size: 12px; font-weight: 700; color: {C['accent']}; "
        active += f"background: {C['card']}; border: 1px solid {C['accent']}; "
        active += f"border-radius: 14px; padding: 0 12px; }}"
        active += f"QPushButton:hover {{ background: {C['card_hover']}; }}"

        inactive = f"QPushButton {{ font-size: 12px; font-weight: 600; color: {C['text_muted']}; "
        inactive += f"background: transparent; border: 1px solid {C['border']}; "
        inactive += f"border-radius: 14px; padding: 0 12px; }}"
        inactive += f"QPushButton:hover {{ color: {C['accent']}; border-color: {C['accent']}; }}"

        self._drop_mode_btn.setStyleSheet(active if index == 0 else inactive)
        self._write_mode_btn.setStyleSheet(active if index == 1 else inactive)

    def _on_compile_editor(self):
        code = self._code_editor.toPlainText().strip()
        if not code:
            self._status_text.setText("Write some code first!")
            return
        import tempfile, os
        tmp = tempfile.NamedTemporaryFile(mode="w", suffix=".ino", delete=False, prefix="sketch_")
        tmp.write(code)
        tmp_path = tmp.name
        tmp.close()
        self._on_ino_received(tmp_path)

    def _on_save_editor_code(self):
        code = self._code_editor.toPlainText().strip()
        if not code:
            return
        from PyQt6.QtWidgets import QFileDialog
        path, _ = QFileDialog.getSaveFileName(
            self, "Save Arduino Sketch", "sketch.ino",
            "Arduino files (*.ino);;All files (*)"
        )
        if path:
            with open(path, "w") as f:
                f.write(code)

    def _on_ino_received(self, path: str):
        self._batch_ino_path = path

        # If coming from config confirm, skip preview and compile directly
        if getattr(self._easy_overlay, '_config_confirmed', False):
            self._easy_overlay._config_confirmed = False
            cfg = getattr(self._easy_overlay, '_pending_cfg', None)
            if cfg is None:
                cfg = parse_ino(path)
            self._start_compile(path, cfg)
            return

        if not self._selected_device and self._devices:
            self._selected_device = next(iter(self._devices.values()))

        if not self._selected_device:
            if self._easy_mode:
                self._easy_overlay.show_no_device()
            else:
                msg = QMessageBox(self)
                msg.setWindowTitle("No device found")
                msg.setText("No ESP32 found on your network.")
                msg.setInformativeText(
                    "You can still configure and compile. "
                    "Upload will happen once a device is online.\n\n"
                    "For a new device, plug it in via USB to flash the base firmware first."
                )
                msg.addButton("Continue anyway", QMessageBox.ButtonRole.ActionRole)
                msg.addButton("Cancel", QMessageBox.ButtonRole.RejectRole)
                msg.exec()
                if msg.clickedButton().text() != "Continue anyway":
                    return

        cfg = parse_ino(path)
        if not cfg.board:
            cfg.board = self._board_label.text()
            cfg.flash_size = BOARDS.get(cfg.board, {}).get("flash_size", "4MB")
        elif cfg.board not in BOARDS:
            cfg.flash_size = cfg.flash_size or "4MB"
            if not self._easy_mode:
                msg = QMessageBox(self)
                msg.setWindowTitle("Board not recognized")
                msg.setText(f"😔 Sorry, Espy can't help with '{cfg.board}' — "
                            f"it's not in my supported board list.")
                msg.setInformativeText(
                    "You can pick a compatible board or continue anyway "
                    "(some features may not work correctly)."
                )
                pick = msg.addButton("Pick a board", QMessageBox.ButtonRole.ActionRole)
                msg.addButton("Continue anyway", QMessageBox.ButtonRole.AcceptRole)
                msg.exec()
                if msg.clickedButton() == pick:
                    self._open_board_picker()
                    cfg.board = self._board_label.text()
                    cfg.flash_size = BOARDS.get(cfg.board, {}).get("flash_size", "4MB")

        if self._easy_mode:
            self._easy_overlay.show_config_review(cfg, path)
        else:
            target_name = self._selected_device.friendly_label if self._selected_device else ""
            dlg = ConfigDialog(cfg, target_device=target_name, parent=self)
            dlg.confirmed.connect(lambda c: self._start_compile(path, c))
            dlg.exec()

    def _start_compile(self, ino_path: str, cfg: InoConfig):
        self._stack.setCurrentIndex(1)
        self._flash_scene.start_compile(cfg.board)
        self._pending_cfg = cfg

        if self._compiler:
            self._compiler.quit()
            self._compiler.wait()
        self._compiler = CompilerWorker(ino_path, cfg)
        self._compiler.progress.connect(self._on_compile_progress)
        self._compiler.finished.connect(lambda p: self._start_ota(p, cfg))
        self._compiler.failed.connect(self._on_error)
        self._compiler.start()

    def _on_compile_progress(self, msg: str):
        ml = msg.lower()
        if "check" in ml or "list" in ml:
            pct = 5
        elif "installing" in ml:
            pct = 15
        elif "compiling" in ml:
            pct = 40
        elif "done" in ml or "ready" in ml:
            pct = 90
        else:
            pct = 10
        self._flash_scene.set_progress(pct, msg)
        self._flash_scene.set_status(msg)
        self._easy_overlay.set_mascot_mood("focused")
        if self._easy_mode:
            self._easy_overlay._flash_status.setText(msg)

    def _on_error(self, friendly: str, raw: str):
        self._flash_scene.show_error(friendly, raw)
        cfg = self._pending_cfg or getattr(self, '_last_error_cfg', None)
        if cfg:
            self._flash_scene.set_error_context(cfg)
        self._easy_overlay.set_mascot_mood("surprise")

    def _on_save_binary(self, bin_path: str):
        import shutil
        from pathlib import Path
        from PyQt6.QtWidgets import QFileDialog
        suggested = Path(bin_path).name or "firmware.bin"
        path, _ = QFileDialog.getSaveFileName(
            self, "Save compiled binary", suggested,
            "Binary files (*.bin);;All files (*)"
        )
        if path:
            shutil.copy2(bin_path, path)

    def _on_flash_now(self, bin_path: str):
        if not self._selected_device or self._selected_device.name not in self._devices:
            return
        cfg = self._pending_cfg or InoConfig()
        self._flash_scene.start_ota()
        self._easy_overlay.set_mascot_mood("sweat")
        if self._easy_mode:
            self._easy_overlay._flash_status.setText("Uploading to ESP32...")
        ota_pass = cfg.ota_password if cfg else ""
        if self._ota:
            self._ota.quit()
            self._ota.wait()
        self._ota = OtaWorker(self._selected_device, bin_path, ota_password=ota_pass)
        self._ota.progress.connect(self._flash_scene.set_progress)
        self._ota.finished.connect(self._on_ota_finished)
        self._ota.failed.connect(self._on_ota_error)
        self._ota.start()

    def _start_ota(self, bin_path: str, cfg: InoConfig = None):
        import os
        if self._example_tmp_path:
            try:
                os.unlink(self._example_tmp_path)
            except OSError:
                pass
            self._example_tmp_path = ""
        self._pending_bin = bin_path
        self._pending_cfg = cfg

        if not self._selected_device or self._selected_device.name not in self._devices:
            self._flash_scene.show_compilation_ready(bin_path, has_device=False)
            if self._easy_mode:
                self._easy_overlay._flash_status.setText("Compilation done! Connect an ESP32 to flash.")
            return

        self._flash_scene.start_ota()
        self._easy_overlay.set_mascot_mood("sweat")
        if self._easy_mode:
            self._easy_overlay._flash_status.setText("Uploading to ESP32...")

        ota_pass = cfg.ota_password if cfg else ""
        if self._ota:
            self._ota.quit()
            self._ota.wait()
        self._ota = OtaWorker(self._selected_device, bin_path, ota_password=ota_pass)
        self._ota.progress.connect(self._flash_scene.set_progress)
        self._ota.finished.connect(self._on_ota_finished)
        self._ota.failed.connect(self._on_ota_error)
        self._ota.start()

    def _on_ota_error(self, msg: str):
        self._flash_scene.show_error(msg, "")
        self._easy_overlay.set_mascot_mood("surprise")
        if self._easy_mode:
            self._easy_overlay._flash_status.setText(msg)
        if hasattr(self, '_batch_queue') and self._batch_queue:
            QTimer.singleShot(2000, self._advance_batch)

    def _on_ota_finished(self):
        self._flash_scene.show_success(self._selected_device.name)
        self._easy_overlay.set_mascot_mood("excited")
        if self._easy_mode:
            self._easy_overlay._flash_progress.setValue(100)
            self._easy_overlay._flash_status.setText("Done! Rebooting...")
            QTimer.singleShot(1200, lambda: self._easy_overlay.show_success(self._selected_device.name))
        else:
            self._easy_overlay.show_success(self._selected_device.name)
        if hasattr(self, '_batch_queue') and self._batch_queue:
            QTimer.singleShot(1500, self._advance_batch)

    # ── USB Setup ─────────────────────────────────────────

    def _show_setup_wizard(self):
        if self._easy_mode:
            self._easy_overlay.show_setup()
        else:
            self._show_wizard_page()

    def _on_easy_device_selected(self, name: str):
        if name in self._devices:
            self._selected_device = self._devices[name]
        elif self._devices:
            self._selected_device = next(iter(self._devices.values()))

    def _on_plug_connected(self):
        from workers.usb_flash import UsbFlashWorker
        from discovery.usb import autodetect_port
        from pathlib import Path

        port = autodetect_port()
        if not port:
            return

        if getattr(sys, "frozen", False):
            base = sys._MEIPASS
        else:
            base = str(Path(__file__).parent.parent)
        base_fw = Path(base) / "firmware" / "easyesp_base.bin"
        if not base_fw.exists():
            return

        if hasattr(self, '_usb_worker') and self._usb_worker:
            self._usb_worker.quit()
            self._usb_worker.wait()

        self._usb_worker = UsbFlashWorker(
            port, str(base_fw), "My ESP32", "", ""
        )
        self._usb_worker.finished.connect(lambda: self._show_usb_done())
        self._usb_worker.start()

    def _show_usb_done(self):
        self._easy_overlay.show_success("Your ESP32")

    def _show_serial_logger(self):
        self._serial_logger._refresh_ports()
        self._stack.setCurrentWidget(self._serial_logger)

    def _show_wizard_page(self):
        wizard = SetupWizard(self)
        wizard.finished.connect(lambda: self._stack.setCurrentIndex(0))
        self._stack.addWidget(wizard)
        self._stack.setCurrentWidget(wizard)

    # ── Mode switching ────────────────────────────────────

    def _show_easy_mode(self):
        self._easy_mode = True
        self._sidebar.hide()
        self._stack.hide()
        self._easy_overlay.setVisible(True)
        self._easy_overlay.raise_()
        if hasattr(self, '_logo_mascot'):
            self._logo_mascot.stop_bounce()

    def _switch_to_advanced(self):
        self._easy_mode = False
        self._easy_overlay.setVisible(False)
        self._sidebar.show()
        self._stack.show()
        self._stack.setCurrentIndex(0)
        self._update_device_status()
        if hasattr(self, '_logo_mascot'):
            self._logo_mascot.start_bounce()

    def _toggle_mode(self):
        if self._easy_mode:
            self._switch_to_advanced()
        else:
            self._show_easy_mode()

    def closeEvent(self, e):
        if hasattr(self, "_discovery"):
            self._discovery.stop()
        if self._compiler:
            self._compiler.quit()
            self._compiler.wait(2000)
        if self._ota:
            self._ota.quit()
            self._ota.wait(2000)
        if hasattr(self, "_usb_worker") and self._usb_worker:
            self._usb_worker.quit()
            self._usb_worker.wait(2000)
        if hasattr(self, "_serial_logger"):
            self._serial_logger._worker.disconnect()
            if self._serial_logger._worker.isRunning():
                self._serial_logger._worker.quit()
                self._serial_logger._worker.wait(2000)
        if hasattr(self, "_batch_queue"):
            self._batch_queue.clear()
        if hasattr(self, "_logo_mascot"):
            self._logo_mascot.stop_bounce()
        super().closeEvent(e)
