from __future__ import annotations
import sys
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QStackedWidget, QLineEdit, QProgressBar, QFrame,
)
from PyQt6.QtCore import Qt, pyqtSignal, QTimer, QSize
from PyQt6.QtGui import QPixmap

from palette import WARM_PASTEL as C
from constants import EASY_MODE_MIN_FONT, EASY_MODE_TITLE_FONT, EASY_MODE_BODY_FONT
from ui.illustrations import (
    espy_glasses, espy_happy, espy_wink, espy_surprise,
    wifi_illustration, ESPY_MOODS, espy_icon_24,
)
from ui.animations import (
    LoadingDots, BouncyMascot, AnimatedCheckmark, FadeStack, AnimatedArrow,
    BlinkingLED,
)
from ui.drop_zone import DropZone
from ui.board_picker import BoardPicker
from models import Device, InoConfig
from constants import BOARDS, FIRST_RUN_FILE, MODE_PREF_FILE
from examples import get_blink_code, get_led_pin
from parser import parse_ino
from ui.wiring_widget import WiringDiagram


T = EASY_MODE_TITLE_FONT
B = EASY_MODE_BODY_FONT
M = EASY_MODE_MIN_FONT


class EasyOverlay(QWidget):
    switch_to_advanced = pyqtSignal()
    file_selected = pyqtSignal(str)
    start_setup = pyqtSignal()
    plug_connected = pyqtSignal()
    mode_chosen = pyqtSignal(str)
    device_selected = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self._devices: list[Device] = []
        self._selected_device: Device = None
        self._pending_cfg: InoConfig = None
        self._pending_path: str = ""
        self._usb_port: str = ""
        self._selected_board: str = ""
        self._is_onboarding = not FIRST_RUN_FILE.exists()
        self._build_ui()

    def _make_top_bar(self) -> QWidget:
        top = QWidget()
        tl = QHBoxLayout(top)
        tl.setContentsMargins(0, 0, 0, 0)

        self._back_btn = QPushButton("← Back")
        self._back_btn.setObjectName("ghost")
        self._back_btn.clicked.connect(self._go_back)
        self._back_btn.setVisible(False)
        self._back_btn.setToolTip("Go to the previous page")
        tl.addWidget(self._back_btn)

        # Mascot logo (replaces ⚡ emoji)
        self._logo_mascot = BouncyMascot()
        self._logo_mascot.set_mood("idle", 28)
        self._logo_mascot.setFixedSize(28, 34)
        tl.addWidget(self._logo_mascot)

        logo = QLabel("Espy")
        logo.setStyleSheet(f"font-size: 22px; font-weight: 800; color: {C['accent']};")
        tl.addWidget(logo)
        tl.addStretch()

        self._status_label = QLabel("")
        self._status_label.setStyleSheet(f"color: {C['text_muted']}; font-size: 15px;")
        tl.addWidget(self._status_label)

        advanced_btn = QPushButton("Advanced")
        advanced_btn.setObjectName("ghost")
        advanced_btn.clicked.connect(self.switch_to_advanced)
        advanced_btn.setToolTip("Switch to Advanced mode with more controls")
        tl.addWidget(advanced_btn)

        return top

    def _build_ui(self):
        self.setStyleSheet(f"background: {C['bg']};")
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(30, 16, 30, 20)
        main_layout.setSpacing(8)

        self._top_bar = self._make_top_bar()
        main_layout.addWidget(self._top_bar)

        self._stack = FadeStack()
        self._build_onboarding_pages()       # 0
        self._stack.addWidget(self._make_mode_choice_page())     # 3
        self._stack.addWidget(self._make_home_page())            # 4
        self._stack.addWidget(self._make_no_device_page())       # 5
        self._stack.addWidget(self._make_setup_page())           # 6
        self._stack.addWidget(self._make_plug_wait_page())       # 7
        self._stack.addWidget(self._make_wifi_page())            # 8
        self._stack.addWidget(self._make_success_page())         # 9
        self._stack.addWidget(self._make_config_page())          # 10
        self._stack.addWidget(self._make_admin_page())           # 11
        self._stack.addWidget(self._make_board_page())           # 12
        self._stack.addWidget(self._make_flash_progress_page())  # 13
        main_layout.addWidget(self._stack, 1)

        if self._is_onboarding:
            self._stack.setCurrentIndex(self._page_index("onboard"))
        else:
            self._stack.setCurrentIndex(self._page_index("home"))

    def _page_index(self, name: str) -> int:
        pages = {
            "onboard": 0,
            "mode_choice": 1,
            "home": 2, "no_device": 3,
            "setup": 4, "plug_wait": 5, "wifi": 6,
            "success": 7, "config": 8, "admin": 9,
            "board": 10, "flash_progress": 11,
        }
        return pages.get(name, 2)

    def set_mascot_mood(self, mood: str):
        if hasattr(self, "_home_mascot"):
            self._home_mascot.set_mood(mood)

    # ── Onboarding ─────────────────────────────────────────

    def _build_onboarding_pages(self):
        from ui.illustrations import onboarding_flow_svg

        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setSpacing(14)

        mascot = BouncyMascot()
        mascot.set_mood("happy", 48)
        mascot.setFixedSize(48, 60)
        mascot.start_bounce()
        layout.addWidget(mascot, alignment=Qt.AlignmentFlag.AlignCenter)

        title = QLabel("How Espy works")
        title.setStyleSheet(f"font-size: {T}px; font-weight: 700; color: {C['text']};")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        sub = QLabel("No cables. No technical stuff. Just drop and flash.")
        sub.setAlignment(Qt.AlignmentFlag.AlignCenter)
        sub.setStyleSheet(f"color: {C['text_muted']}; font-size: {B - 1}px;")
        layout.addWidget(sub)

        # Flow diagram
        flow_lbl = QLabel()
        pm = QPixmap()
        svg = onboarding_flow_svg(320, 340)
        pm.loadFromData(svg.encode())
        flow_lbl.setPixmap(pm)
        flow_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(flow_lbl, stretch=1)

        # Single page indicator (1/1)
        dot = QLabel("●")
        dot.setStyleSheet(f"font-size: 18px; color: {C['accent']};")
        dot.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(dot)

        btn = QPushButton("Let's go! →")
        btn.setObjectName("primary")
        btn.clicked.connect(lambda: self._stack.fade_to(self._page_index("mode_choice")))
        btn.setToolTip("Set up your ESP32")
        layout.addWidget(btn, alignment=Qt.AlignmentFlag.AlignCenter)

        skip = QPushButton("Skip for now")
        skip.setObjectName("ghost")
        skip.clicked.connect(self._finish_onboarding)
        skip.setToolTip("You can always set this up later")
        layout.addWidget(skip, alignment=Qt.AlignmentFlag.AlignCenter)

        self._stack.addWidget(page)

    def _finish_onboarding(self):
        FIRST_RUN_FILE.parent.mkdir(parents=True, exist_ok=True)
        FIRST_RUN_FILE.write_text("done")
        self._is_onboarding = False
        self._update_home_page()
        self._stack.fade_to(self._page_index("home"))

    def _finish_onboarding_to_setup(self):
        self._finish_onboarding()
        self._stack.fade_to(self._page_index("setup"))

    # ── Mode choice page ────────────────────────────────────

    def _make_mode_choice_page(self) -> QWidget:
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setSpacing(20)

        mascot = BouncyMascot()
        mascot.set_mood("excited", 80)
        mascot.setFixedSize(80, 96)
        mascot.start_bounce()
        layout.addWidget(mascot, alignment=Qt.AlignmentFlag.AlignCenter)

        title = QLabel("How do you want to use Espy?")
        title.setStyleSheet(f"font-size: {T}px; font-weight: 700; color: {C['text']};")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        cards_row = QHBoxLayout()
        cards_row.setSpacing(20)
        cards_row.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Simple mode card
        simple_card = QFrame()
        simple_card.setObjectName("card")
        simple_card.setCursor(Qt.CursorShape.PointingHandCursor)
        simple_card.setFixedSize(260, 210)
        sc = QVBoxLayout(simple_card)
        sc.setAlignment(Qt.AlignmentFlag.AlignCenter)
        sc.setSpacing(10)
        sc.setContentsMargins(18, 18, 18, 18)

        simple_icon = QLabel("✨")
        simple_icon.setStyleSheet("font-size: 36px;")
        simple_icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        sc.addWidget(simple_icon)

        simple_title = QLabel("Simple")
        simple_title.setStyleSheet(f"font-size: 22px; font-weight: 800; color: {C['text']};")
        simple_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        sc.addWidget(simple_title)

        simple_desc = QLabel("Drag, drop, done.\nNo technical stuff.\nJust works.")
        simple_desc.setAlignment(Qt.AlignmentFlag.AlignCenter)
        simple_desc.setStyleSheet(f"font-size: 15px; color: {C['text_muted']}; line-height: 1.4;")
        sc.addWidget(simple_desc)

        simple_btn = QPushButton("Choose Simple")
        simple_btn.setObjectName("primary")
        simple_btn.clicked.connect(lambda: self._choose_mode("simple"))
        sc.addWidget(simple_btn, alignment=Qt.AlignmentFlag.AlignCenter)

        # Advanced mode card
        adv_card = QFrame()
        adv_card.setObjectName("card")
        adv_card.setCursor(Qt.CursorShape.PointingHandCursor)
        adv_card.setFixedSize(260, 210)
        ac = QVBoxLayout(adv_card)
        ac.setAlignment(Qt.AlignmentFlag.AlignCenter)
        ac.setSpacing(10)
        ac.setContentsMargins(18, 18, 18, 18)

        adv_icon = QLabel("⚙️")
        adv_icon.setStyleSheet("font-size: 36px;")
        adv_icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        ac.addWidget(adv_icon)

        adv_title = QLabel("Advanced")
        adv_title.setStyleSheet(f"font-size: 22px; font-weight: 800; color: {C['text']};")
        adv_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        ac.addWidget(adv_title)

        adv_desc = QLabel("Full control over\npartitions, board config,\nOTA settings, and more.")
        adv_desc.setAlignment(Qt.AlignmentFlag.AlignCenter)
        adv_desc.setStyleSheet(f"font-size: 15px; color: {C['text_muted']}; line-height: 1.4;")
        ac.addWidget(adv_desc)

        adv_btn = QPushButton("Choose Advanced")
        adv_btn.setObjectName("secondary")
        adv_btn.clicked.connect(lambda: self._choose_mode("advanced"))
        ac.addWidget(adv_btn, alignment=Qt.AlignmentFlag.AlignCenter)

        cards_row.addWidget(simple_card)
        cards_row.addWidget(adv_card)
        layout.addLayout(cards_row)

        skip_btn = QPushButton("Skip for now — go to app")
        skip_btn.setObjectName("ghost")
        skip_btn.clicked.connect(self._finish_onboarding)
        skip_btn.setToolTip("You can change this later in settings")
        layout.addWidget(skip_btn, alignment=Qt.AlignmentFlag.AlignCenter)

        return page

    def _choose_mode(self, mode: str):
        MODE_PREF_FILE.parent.mkdir(parents=True, exist_ok=True)
        MODE_PREF_FILE.write_text(mode)
        self._finish_onboarding()
        if mode == "advanced":
            self._onboarding_chose_advanced = True
            QTimer.singleShot(400, self.switch_to_advanced.emit)

    # ── Dynamic home page ───────────────────────────────────

    def _make_home_page(self) -> QWidget:
        page = QWidget()
        self._home_layout = QVBoxLayout(page)
        self._home_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._home_layout.setSpacing(16)

        self._home_mascot = BouncyMascot()
        self._home_mascot.setFixedSize(160, 180)
        self._home_mascot.set_mood("idle")
        self._home_mascot.set_bounce_style("idle")
        self._home_mascot.start_bounce()
        self._home_layout.addWidget(self._home_mascot, alignment=Qt.AlignmentFlag.AlignCenter)

        self._home_arrow = AnimatedArrow("down")
        self._home_arrow.setFixedSize(40, 40)
        self._home_arrow.hide()
        self._home_layout.addWidget(self._home_arrow, alignment=Qt.AlignmentFlag.AlignCenter)

        self._home_title = QLabel()
        self._home_title.setStyleSheet(f"font-size: {T}px; font-weight: 700; color: {C['text']};")
        self._home_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._home_layout.addWidget(self._home_title)

        self._home_sub = QLabel()
        self._home_sub.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._home_sub.setWordWrap(True)
        self._home_sub.setStyleSheet(f"color: {C['text_muted']}; font-size: {B}px;")
        self._home_layout.addWidget(self._home_sub)

        # ── Blink teaser (shown when device connected) ────────
        self._blink_teaser = QFrame()
        self._blink_teaser.setObjectName("card")
        self._blink_teaser.hide()
        bt = QHBoxLayout(self._blink_teaser)
        bt.setContentsMargins(20, 14, 20, 14)
        bt.setSpacing(14)
        bt.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self._blink_led = BlinkingLED()
        bt.addWidget(self._blink_led)

        bt_text = QVBoxLayout()
        bt_text.setSpacing(2)
        self._blink_label = QLabel("Would you like to see your board blink?")
        self._blink_label.setStyleSheet(f"font-size: 17px; font-weight: 600; color: {C['text']};")
        bt_text.addWidget(self._blink_label)

        self._blink_hint = QLabel("Built-in LED blink example for your ESP32")
        self._blink_hint.setStyleSheet(f"font-size: 13px; color: {C['text_muted']};")
        bt_text.addWidget(self._blink_hint)
        bt.addLayout(bt_text)

        self._blink_btn = QPushButton("✨ Yes, blink it!")
        self._blink_btn.setObjectName("primary")
        self._blink_btn.setFixedHeight(36)
        self._blink_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self._blink_btn.clicked.connect(self._on_blink_example)
        bt.addWidget(self._blink_btn)
        self._home_layout.addWidget(self._blink_teaser)

        self._home_dev_picker = QPushButton("Choose device...")
        self._home_dev_picker.setObjectName("secondary")
        self._home_dev_picker.setFixedWidth(280)
        self._home_dev_picker.clicked.connect(self._cycle_device)
        self._home_dev_picker.hide()
        self._home_dev_picker.setToolTip("Select which ESP32 to flash")
        self._home_layout.addWidget(self._home_dev_picker, alignment=Qt.AlignmentFlag.AlignCenter)

        self._home_drop = DropZone()
        self._home_drop.file_dropped.connect(self._on_file)
        self._home_drop.file_chosen.connect(self._on_file)
        self._home_drop.hide()
        self._home_layout.addWidget(self._home_drop, stretch=1)

        self._home_btn = QPushButton()
        self._home_btn.setObjectName("primary")
        self._home_btn.clicked.connect(self._on_home_btn)
        self._home_btn.setToolTip("Plug in your ESP32 via USB to get started")
        self._home_layout.addWidget(self._home_btn, alignment=Qt.AlignmentFlag.AlignCenter)

        self._update_home_page()
        return page

    def _on_home_btn(self):
        self._stack.fade_to(self._page_index("setup"))

    def _on_blink_example(self):
        board = self._selected_board or "ESP32 Dev Module"
        code = get_blink_code(board)

        import tempfile
        tmp = tempfile.NamedTemporaryFile(mode="w", suffix=".ino", delete=False, prefix="blink_")
        tmp.write(code)
        tmp_path = tmp.name
        tmp.close()

        cfg = parse_ino(tmp_path)
        if not cfg.board or cfg.board not in BOARDS:
            cfg.board = board
            cfg.flash_size = BOARDS.get(board, {}).get("flash_size", "4MB")

        self._pending_cfg = cfg
        self._pending_path = tmp_path
        self._config_confirmed = True
        self._confirming = True
        self.set_mascot_mood("excited")
        self._flash_progress.setValue(0)
        self._flash_status.setText("Starting blink compilation...")
        self._stack.fade_to(self._page_index("flash_progress"))

        from PyQt6.QtCore import QTimer as Qtimer
        Qtimer.singleShot(500, lambda: self.file_selected.emit(tmp_path))

    def _show_blink_teaser(self):
        device = self._selected_device
        board = self._selected_board or "ESP32 Dev Module"
        led_pin = get_led_pin(board)
        self._blink_label.setText(f"Would you like to see your {device.friendly_label if device else 'ESP32'} blink?")
        self._blink_hint.setText(f"Built-in LED on GPIO {led_pin}  ·  {board}")
        self._blink_teaser.show()
        self._blink_led.start()
        self.set_mascot_mood("excited")
        self._home_mascot.set_bounce_style("excited")

    def _update_home_page(self):
        count = len(self._devices)
        if count == 0:
            self._blink_teaser.hide()
            self._home_mascot.set_mood("sad", 160)
            self._home_mascot.set_bounce_style("sad")
            self._home_title.setText("No ESP32s yet!")
            self._home_sub.setText("Set up your first ESP32 to\nstart flashing over Wi-Fi.")
            self._home_dev_picker.hide()
            self._home_drop.hide()
            self._home_btn.setText("Set up my ESP32 →")
            self._home_btn.show()
            self._home_arrow.show()
        elif count == 1:
            self._home_mascot.set_mood("happy", 160)
            self._home_mascot.set_bounce_style("happy")
            dev = self._devices[0]
            self._selected_device = dev
            self._home_title.setText(f"{dev.friendly_label} is ready!")
            self._home_sub.setText("Drop your .ino file to flash it.")
            self._home_dev_picker.hide()
            self._home_drop.show()
            self._home_btn.hide()
            self._home_arrow.hide()
            self.device_selected.emit(dev.name)
            self._show_blink_teaser()
        else:
            self._home_mascot.set_mood("happy", 160)
            self._home_mascot.set_bounce_style("happy")
            self._home_title.setText(f"{count} ESP32s found!")
            self._home_sub.setText("Pick a device, then drop your code.")
            self._home_dev_picker.show()
            self._update_device_picker()
            self._home_drop.show()
            self._home_btn.hide()
            self._home_arrow.hide()
            if self._selected_device:
                self.device_selected.emit(self._selected_device.name)
            self._show_blink_teaser()

    # ── Setup flow pages ────────────────────────────────────

    def _make_setup_page(self) -> QWidget:
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setSpacing(16)

        # Mascot + small USB cable side by side
        vis_row = QHBoxLayout()
        vis_row.setAlignment(Qt.AlignmentFlag.AlignCenter)
        vis_row.setSpacing(12)

        mascot = BouncyMascot()
        mascot.set_mood("happy", 80)
        mascot.setFixedSize(80, 96)
        mascot.start_bounce()
        vis_row.addWidget(mascot)

        from ui.illustrations import usb_illustration
        usb_lbl = QLabel()
        pm = QPixmap()
        pm.loadFromData(usb_illustration(100).encode())
        usb_lbl.setPixmap(pm)
        usb_lbl.setFixedSize(100, 80)
        vis_row.addWidget(usb_lbl)

        layout.addLayout(vis_row)

        title = QLabel("Plug in your ESP32")
        title.setStyleSheet(f"font-size: {T}px; font-weight: 700; color: {C['text']};")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        sub = QLabel(
            "Connect the USB cable between your computer\n"
            "and the ESP32 board. I'll handle the rest."
        )
        sub.setAlignment(Qt.AlignmentFlag.AlignCenter)
        sub.setStyleSheet(f"color: {C['text_muted']}; font-size: {B}px;")
        layout.addWidget(sub)

        big_btn = QPushButton("I plugged it in! →")
        big_btn.setObjectName("primary")
        big_btn.clicked.connect(self._on_plug_button)
        big_btn.setToolTip("Make sure the USB cable is connected to your ESP32 and this computer")
        layout.addWidget(big_btn, alignment=Qt.AlignmentFlag.AlignCenter)

        skip_btn = QPushButton("Skip — take me to the app")
        skip_btn.setObjectName("ghost")
        skip_btn.clicked.connect(self._skip_setup)
        skip_btn.setToolTip("You can always set this up later")
        layout.addWidget(skip_btn, alignment=Qt.AlignmentFlag.AlignCenter)

        return page

    def _make_plug_wait_page(self) -> QWidget:
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setSpacing(18)

        self._plug_dots = LoadingDots()
        layout.addWidget(self._plug_dots, alignment=Qt.AlignmentFlag.AlignCenter)

        title = QLabel("Looking for your ESP32...")
        title.setStyleSheet(f"font-size: {T - 2}px; font-weight: 700; color: {C['text']};")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        self._plug_status = QLabel("Check that the USB cable is connected.")
        self._plug_status.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._plug_status.setStyleSheet(f"color: {C['text_muted']}; font-size: {B}px;")
        layout.addWidget(self._plug_status)

        retry_btn = QPushButton("Try again")
        retry_btn.setObjectName("secondary")
        retry_btn.clicked.connect(self._retry_usb_detect)
        retry_btn.setToolTip("Check your cable and try again")
        layout.addWidget(retry_btn, alignment=Qt.AlignmentFlag.AlignCenter)

        back_btn = QPushButton("← Back")
        back_btn.setObjectName("ghost")
        back_btn.clicked.connect(lambda: self._stack.fade_to(self._page_index("setup")))
        back_btn.setToolTip("Go back to the setup page")
        layout.addWidget(back_btn, alignment=Qt.AlignmentFlag.AlignCenter)

        return page

    def _make_wifi_page(self) -> QWidget:
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setSpacing(16)

        from ui.animations import PulsingWifi
        pw = PulsingWifi()
        pw.setFixedSize(100, 80)
        layout.addWidget(pw, alignment=Qt.AlignmentFlag.AlignCenter)

        mascot = BouncyMascot()
        mascot.set_mood("searching", 50)
        mascot.setFixedSize(50, 62)
        mascot.start_bounce()
        layout.addWidget(mascot, alignment=Qt.AlignmentFlag.AlignCenter)

        title = QLabel("Connect to Wi-Fi")
        title.setStyleSheet(f"font-size: {T}px; font-weight: 700; color: {C['text']};")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        sub = QLabel("Your ESP32 will use this to receive updates wirelessly.")
        sub.setAlignment(Qt.AlignmentFlag.AlignCenter)
        sub.setStyleSheet(f"color: {C['text_muted']}; font-size: {B - 1}px;")
        layout.addWidget(sub)

        self._setup_ssid = QLineEdit()
        self._setup_ssid.setPlaceholderText("Your Wi-Fi name (e.g. MyHomeNetwork)")
        self._setup_ssid.setMinimumWidth(320)
        self._setup_ssid.setToolTip("The name of your home Wi-Fi network")
        layout.addWidget(self._setup_ssid)

        self._setup_password = QLineEdit()
        self._setup_password.setEchoMode(QLineEdit.EchoMode.Password)
        self._setup_password.setPlaceholderText("Wi-Fi password")
        self._setup_password.setMinimumWidth(320)
        self._setup_password.setToolTip("Saved on your ESP32 — not your computer")
        layout.addWidget(self._setup_password)

        self._wifi_error = QLabel("")
        self._wifi_error.setStyleSheet(f"color: {C['error']}; font-size: 15px;")
        self._wifi_error.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._wifi_error.hide()
        layout.addWidget(self._wifi_error)

        btn = QPushButton("Save & Continue →")
        btn.setObjectName("primary")
        btn.clicked.connect(self._on_wifi_save)
        btn.setToolTip("Save Wi-Fi details to your ESP32")
        layout.addWidget(btn, alignment=Qt.AlignmentFlag.AlignCenter)

        back_btn = QPushButton("← Back")
        back_btn.setObjectName("ghost")
        back_btn.clicked.connect(lambda: self._stack.fade_to(self._page_index("setup")))
        back_btn.setToolTip("Go back to the previous step")
        layout.addWidget(back_btn, alignment=Qt.AlignmentFlag.AlignCenter)

        return page

    def _make_no_device_page(self) -> QWidget:
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setSpacing(18)

        mascot = BouncyMascot()
        mascot.set_mood("surprise", 120)
        mascot.setFixedSize(120, 140)
        mascot.start_bounce()
        layout.addWidget(mascot, alignment=Qt.AlignmentFlag.AlignCenter)

        title = QLabel("I can't find your ESP32")
        title.setStyleSheet(f"font-size: {T}px; font-weight: 700; color: {C['text']};")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        sub = QLabel(
            "Make sure it's powered on and on the same Wi‑Fi.\n"
            "For a new device, set it up with USB first."
        )
        sub.setAlignment(Qt.AlignmentFlag.AlignCenter)
        sub.setStyleSheet(f"color: {C['text_muted']}; font-size: {B}px;")
        layout.addWidget(sub)

        btn = QPushButton("Set up with USB →")
        btn.setObjectName("primary")
        btn.clicked.connect(lambda: self._stack.fade_to(self._page_index("setup")))
        btn.setToolTip("Plug your ESP32 in via USB to set it up")
        layout.addWidget(btn, alignment=Qt.AlignmentFlag.AlignCenter)

        return page

    def _make_success_page(self) -> QWidget:
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setSpacing(18)

        self._success_check = AnimatedCheckmark()
        self._success_check.setFixedSize(120, 120)
        layout.addWidget(self._success_check, alignment=Qt.AlignmentFlag.AlignCenter)

        self._success_title = QLabel("It works! 🎉")
        self._success_title.setStyleSheet(f"font-size: {T}px; font-weight: 700; color: {C['success']};")
        self._success_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self._success_title)

        self._success_sub = QLabel("")
        self._success_sub.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._success_sub.setStyleSheet(f"color: {C['text_muted']}; font-size: {B}px;")
        layout.addWidget(self._success_sub)

        btn = QPushButton("Flash another →")
        btn.setObjectName("primary")
        btn.clicked.connect(lambda: self._back_to_home())
        btn.setToolTip("Go back to flash another device")
        layout.addWidget(btn, alignment=Qt.AlignmentFlag.AlignCenter)

        return page

    def _make_config_page(self) -> QWidget:
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setSpacing(14)
        layout.setContentsMargins(40, 16, 40, 16)

        mascot = BouncyMascot()
        mascot.set_mood("wink", 100)
        mascot.setFixedSize(100, 120)
        mascot.start_bounce()
        layout.addWidget(mascot, alignment=Qt.AlignmentFlag.AlignCenter)

        title = QLabel("I read your code!")
        title.setStyleSheet(f"font-size: {T - 2}px; font-weight: 700; color: {C['text']};")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        card = QFrame()
        card.setObjectName("card")
        cl = QVBoxLayout(card)
        cl.setSpacing(8)
        cl.setContentsMargins(20, 16, 20, 16)
        self._config_target_lbl = QLabel("")
        self._config_target_lbl.setStyleSheet(f"color: {C['accent']}; font-size: 17px; font-weight: 700;")
        cl.addWidget(self._config_target_lbl)
        self._config_name_lbl = QLabel("")
        self._config_board_lbl = QLabel("")
        self._config_partition_lbl = QLabel("")
        self._config_wifi_lbl = QLabel("")
        self._config_libs_lbl = QLabel("")
        for lbl in [self._config_name_lbl, self._config_board_lbl,
                     self._config_partition_lbl, self._config_wifi_lbl,
                     self._config_libs_lbl]:
            lbl.setStyleSheet(f"color: {C['text']}; font-size: 17px;")
            cl.addWidget(lbl)
        self._config_partition_lbl.hide()
        self._config_warning_lbl = QLabel("")
        self._config_warning_lbl.setStyleSheet(f"color: {C['warning']}; font-size: 15px;")
        self._config_warning_lbl.setWordWrap(True)
        self._config_warning_lbl.hide()
        cl.addWidget(self._config_warning_lbl)

        part_edit_btn = QPushButton("Edit partition layout")
        part_edit_btn.setObjectName("ghost")
        part_edit_btn.setStyleSheet(
            f"QPushButton{{ font-size: 14px; color: {C['accent']}; }}"
        )
        part_edit_btn.clicked.connect(self._edit_partitions)
        part_edit_btn.setToolTip("Change flash size, partition scheme, or custom partition table")
        cl.addWidget(part_edit_btn)

        layout.addWidget(card)

        # ── Wiring section ────────────────────────────────────────
        self._wiring_card = QFrame()
        self._wiring_card.setObjectName("card")
        self._wiring_card.hide()
        wc = QVBoxLayout(self._wiring_card)
        wc.setContentsMargins(20, 14, 20, 14)
        wc.setSpacing(8)

        wiring_title = QLabel("🔌  Wiring — what to connect where")
        wiring_title.setStyleSheet(f"font-weight: 700; font-size: 15px; color: {C['text']};")
        wc.addWidget(wiring_title)

        self._wiring_diagram = WiringDiagram()
        self._wiring_diagram.setMinimumHeight(240)
        wc.addWidget(self._wiring_diagram)

        self._wiring_detail = QVBoxLayout()
        wc.addLayout(self._wiring_detail)
        layout.addWidget(self._wiring_card)

        btn = QPushButton("Looks good! Flash it →")
        btn.setObjectName("primary")
        btn.clicked.connect(self._confirm_config)
        btn.setToolTip("Start compiling and uploading to your ESP32")
        layout.addWidget(btn, alignment=Qt.AlignmentFlag.AlignCenter)

        back_btn = QPushButton("← Choose a different file")
        back_btn.setObjectName("ghost")
        back_btn.clicked.connect(lambda: self._back_to_home())
        back_btn.setToolTip("Pick a different .ino file")
        layout.addWidget(back_btn, alignment=Qt.AlignmentFlag.AlignCenter)

        return page

    def _make_admin_page(self) -> QWidget:
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setSpacing(18)

        mascot = BouncyMascot()
        mascot.set_mood("idle", 80)
        mascot.setFixedSize(80, 96)
        mascot.start_bounce()
        layout.addWidget(mascot, alignment=Qt.AlignmentFlag.AlignCenter)

        title = QLabel("Admin")
        title.setStyleSheet(f"font-size: {T}px; font-weight: 700; color: {C['text']};")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        sub = QLabel("Reset or reconfigure your ESP32s.")
        sub.setAlignment(Qt.AlignmentFlag.AlignCenter)
        sub.setStyleSheet(f"color: {C['text_muted']}; font-size: {B}px;")
        layout.addWidget(sub)

        btn = QPushButton("Set up a new ESP32")
        btn.setObjectName("primary")
        btn.clicked.connect(lambda: self._stack.fade_to(self._page_index("setup")))
        btn.setToolTip("Plug in a new ESP32 via USB to get started")
        layout.addWidget(btn, alignment=Qt.AlignmentFlag.AlignCenter)

        part_btn = QPushButton("Partition settings")
        part_btn.setObjectName("secondary")
        part_btn.clicked.connect(self._edit_partitions_default)
        part_btn.setToolTip("Change flash size, partition scheme, or edit partition table")
        layout.addWidget(part_btn, alignment=Qt.AlignmentFlag.AlignCenter)

        back_btn = QPushButton("← Back to home")
        back_btn.setObjectName("ghost")
        back_btn.clicked.connect(lambda: self._back_to_home())
        back_btn.setToolTip("Go back to the home page")
        layout.addWidget(back_btn, alignment=Qt.AlignmentFlag.AlignCenter)

        return page

    def _make_board_page(self) -> QWidget:
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setSpacing(14)

        mascot = BouncyMascot()
        mascot.set_mood("happy", 60)
        mascot.setFixedSize(60, 72)
        mascot.start_bounce()
        layout.addWidget(mascot, alignment=Qt.AlignmentFlag.AlignCenter)

        title = QLabel("Which ESP32 do you have?")
        title.setStyleSheet(f"font-size: {T}px; font-weight: 700; color: {C['text']};")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        sub = QLabel(
            "Pick the board that matches your hardware.\n"
            "Check the label on the metal chip on your board."
        )
        sub.setAlignment(Qt.AlignmentFlag.AlignCenter)
        sub.setStyleSheet(f"color: {C['text_muted']}; font-size: {B - 1}px;")
        layout.addWidget(sub)

        from ui.board_picker import BoardPicker
        self._board_picker = BoardPicker()
        self._board_picker.board_selected.connect(self._on_board_selected)
        layout.addWidget(self._board_picker, stretch=1)

        self._board_next_btn = QPushButton("Next →")
        self._board_next_btn.setObjectName("primary")
        self._board_next_btn.setEnabled(False)
        self._board_next_btn.clicked.connect(self._after_board_chosen)
        self._board_next_btn.setToolTip("Select a board first")
        layout.addWidget(self._board_next_btn, alignment=Qt.AlignmentFlag.AlignCenter)

        back_btn = QPushButton("← Back")
        back_btn.setObjectName("ghost")
        back_btn.clicked.connect(lambda: self._stack.fade_to(self._page_index("plug_wait")))
        layout.addWidget(back_btn, alignment=Qt.AlignmentFlag.AlignCenter)

        return page

    def _on_board_selected(self, name: str):
        self._selected_board = name
        self._board_next_btn.setEnabled(True)
        self._board_next_btn.setText(f"Next — {name} →")

    def _after_board_chosen(self):
        self._stack.fade_to(self._page_index("wifi"))

    def _make_flash_progress_page(self) -> QWidget:
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setSpacing(18)

        self._flash_progress = QProgressBar()
        self._flash_progress.setMinimum(0)
        self._flash_progress.setMaximum(100)
        self._flash_progress.setValue(0)
        self._flash_progress.setMinimumWidth(300)
        self._flash_progress.setTextVisible(True)
        layout.addWidget(self._flash_progress, alignment=Qt.AlignmentFlag.AlignCenter)

        self._flash_status = QLabel("Preparing to flash...")
        self._flash_status.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._flash_status.setStyleSheet(f"color: {C['text_muted']}; font-size: {B}px;")
        layout.addWidget(self._flash_status)

        return page

    # ── Public API ──────────────────────────────────────────

    def set_devices(self, devices: list[Device]):
        self._devices = devices
        if devices and not self._selected_device:
            self._selected_device = devices[0]
            self._update_device_picker()
        self._update_home_page()

    def set_status(self, msg: str):
        self._status_label.setText(msg)

    def show_no_device(self):
        self.set_mascot_mood("surprise")
        self._stack.fade_to(self._page_index("no_device"))

    def show_success(self, device_name: str):
        self.set_mascot_mood("excited")
        self._success_title.setText("It works! 🎉")
        self._success_sub.setText(f"{device_name} is running your code.")
        self._stack.fade_to(self._page_index("success"))
        QTimer.singleShot(200, self._success_check.start_animate)

    def show_config_review(self, cfg: InoConfig, path: str):
        self.set_mascot_mood("wink")
        self._pending_cfg = cfg
        self._pending_path = path
        target = self._selected_device.friendly_label if self._selected_device else ""
        self._config_target_lbl.setText(f"🎯  Target: {target}" if target else "")
        self._config_name_lbl.setText(f"  Device: {cfg.device_name or 'My ESP32'}")
        self._config_board_lbl.setText(f"  Board: {cfg.board}")
        flash = cfg.flash_size_override or cfg.flash_size
        scheme = cfg.partition_scheme.replace("_", " ").title()
        if cfg.partition_csv_override:
            pt = f"  Partitions: {flash} · {scheme} (custom CSV)"
        else:
            pt = f"  Partitions: {flash} · {scheme}"
        self._config_partition_lbl.setText(pt)
        self._config_partition_lbl.show()
        self._config_wifi_lbl.setText(f"  Wi‑Fi: {cfg.wifi_ssid or '(from device)'}")
        libs_text = "  " + ", ".join(l.name for l in cfg.libraries) if cfg.libraries else ""
        self._config_libs_lbl.setText(libs_text)
        if cfg.has_ota_conflict:
            self._config_warning_lbl.setText("I'll remove old OTA code for you.")
            self._config_warning_lbl.show()
        else:
            self._config_warning_lbl.hide()

        # Wiring section
        if cfg.detected_pins or cfg.wiring_suggestions:
            self._wiring_diagram.set_data(
                cfg.board,
                [{"gpio": p.gpio, "name": p.name, "direction": p.direction}
                 for p in cfg.detected_pins],
                [{"component": s.component, "pins": s.pins, "protocol": s.protocol,
                  "library": s.library, "notes": s.notes, "color": s.color}
                 for s in cfg.wiring_suggestions],
            )
            # Clear old detail rows
            while self._wiring_detail.count():
                item = self._wiring_detail.takeAt(0)
                if item.widget():
                    item.widget().deleteLater()
            for s in cfg.wiring_suggestions:
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
                self._wiring_detail.addLayout(row)
            self._wiring_card.show()
        else:
            self._wiring_card.hide()

        self._stack.fade_to(self._page_index("config"))

    def show_setup(self):
        self._stack.fade_to(self._page_index("setup"))

    # ── Internal: setup flow ────────────────────────────────

    def _on_plug_button(self):
        self.set_mascot_mood("searching")
        self._stack.fade_to(self._page_index("plug_wait"))
        self._plug_dots.start()
        self._plug_status.setText("Check that the USB cable is connected.")
        QTimer.singleShot(1500, self._do_usb_detect)

    def _do_usb_detect(self):
        from discovery.usb import usb_probe
        ports = usb_probe()
        if ports:
            self._plug_dots.stop()
            self._plug_status.setText(f"✓ Found it! ({ports[0]['port']})")
            self._plug_status.setStyleSheet(f"color: {C['success']}; font-size: {B}px;")
            self._usb_port = ports[0]['port']
            self.set_mascot_mood("happy")
            QTimer.singleShot(800, lambda: self._stack.fade_to(self._page_index("board")))
        else:
            self._plug_dots.stop()
            self._plug_status.setText("✗ Could not find your ESP32. Try a different USB cable.")
            self._plug_status.setStyleSheet(f"color: {C['error']}; font-size: {B}px;")

    def _retry_usb_detect(self):
        self._plug_dots.start()
        self._plug_status.setText("Check that the USB cable is connected.")
        self._plug_status.setStyleSheet(f"color: {C['text_muted']}; font-size: {B}px;")
        QTimer.singleShot(1500, self._do_usb_detect)

    def _on_wifi_save(self):
        ssid = self._setup_ssid.text().strip()
        if not ssid:
            self._wifi_error.setText("Please enter your Wi-Fi network name.")
            self._wifi_error.show()
            return
        password = self._setup_password.text().strip()
        self._wifi_error.hide()

        self._stack.fade_to(self._page_index("flash_progress"))
        self._flash_status.setText("Flashing your ESP32...")
        self._flash_progress.setValue(10)
        self._start_usb_flash(ssid, password)

    def _start_usb_flash(self, ssid: str, password: str):
        from workers.usb_flash import UsbFlashWorker
        from pathlib import Path

        if getattr(sys, "frozen", False):
            base = sys._MEIPASS
        else:
            base = str(Path(__file__).parent.parent)
        base_fw = Path(base) / "firmware" / "easyesp_base.bin"
        if not base_fw.exists():
            self._flash_status.setText("Base firmware not found — reinstall Espy.")
            return

        if not self._usb_port:
            self._flash_status.setText("No USB port found — try plugging in again.")
            return

        name = "My ESP32"
        self._usb_worker = UsbFlashWorker(self._usb_port, str(base_fw),
                                          name, ssid, password,
                                          board=self._selected_board)
        self._usb_worker.progress.connect(self._on_flash_progress)
        self._usb_worker.finished.connect(self._on_flash_done)
        self._usb_worker.failed.connect(self._on_flash_failed)
        self._usb_worker.start()

    def _on_flash_progress(self, pct: int, msg: str):
        self._flash_progress.setValue(pct)
        self._flash_status.setText(msg)

    def _on_flash_done(self):
        self._confirming = False
        self._flash_progress.setValue(100)
        self._finish_onboarding_if_needed()
        self.show_success("Your ESP32")

    def _on_flash_failed(self, msg: str):
        self._confirming = False
        self._flash_status.setText(msg)
        self._flash_status.setStyleSheet(f"color: {C['error']}; font-size: {B}px;")

    # ── Partition editor (shared) ───────────────────────────

    def _confirm_config(self):
        if getattr(self, '_confirming', False):
            return
        if self._pending_path and self._pending_cfg:
            self._confirming = True
            self._pending_cfg.bin_size_bytes = 0
            self._config_confirmed = True
            self._flash_progress.setValue(0)
            self._flash_status.setText("Starting compilation...")
            self._stack.fade_to(self._page_index("flash_progress"))
            QTimer.singleShot(100, lambda: self.file_selected.emit(self._pending_path))

    def _edit_partitions(self):
        if self._pending_cfg is None:
            return
        from ui.partition_editor import PartitionEditor
        editor = PartitionEditor(self._pending_cfg, self)
        editor.applied.connect(self._on_partitions_edited)
        editor.exec()

    def _edit_partitions_default(self):
        cfg = InoConfig()
        from ui.partition_editor import PartitionEditor
        editor = PartitionEditor(cfg, self)
        editor.applied.connect(self._on_partitions_edited_default)
        editor.exec()

    def _on_partitions_edited_default(self, cfg: InoConfig):
        self._pending_cfg = cfg
        self._status_label.setText(f"Partitions: {cfg.partition_scheme.replace('_', ' ').title()} · {cfg.flash_size}")

    def _on_partitions_edited(self, cfg: InoConfig):
        self._pending_cfg = cfg
        if self._pending_path:
            self.show_config_review(cfg, self._pending_path)

    # ── Internal: file handling ─────────────────────────────

    def _on_file(self, path: str):
        self._pending_path = path
        self.set_mascot_mood("wink")
        self.file_selected.emit(path)

    def _update_device_picker(self):
        if self._selected_device:
            txt = self._selected_device.friendly_label
            self._home_dev_picker.setText(txt)
        elif self._devices:
            self._selected_device = self._devices[0]
            self._home_dev_picker.setText(self._selected_device.friendly_label)
        else:
            self._home_dev_picker.setText("No device")

    def _cycle_device(self):
        if not self._devices:
            self.show_no_device()
            return
        idx = 0
        for i, d in enumerate(self._devices):
            if d is self._selected_device:
                idx = (i + 1) % len(self._devices)
                break
        self._selected_device = self._devices[idx]
        self._update_device_picker()
        self._home_title.setText(f"{self._selected_device.friendly_label} is ready!")
        self._home_sub.setText("Drop your .ino file to flash it.")
        self.device_selected.emit(self._selected_device.name)
        self._show_blink_teaser()

    def _go_back(self):
        current = self._stack.currentIndex()
        if current > 0:
            self._stack.fade_to(current - 1)

    def _skip_setup(self):
        self._finish_onboarding_if_needed()
        self._back_to_home()
        self.set_mascot_mood("idle")
        self._status_label.setText("You can set up an ESP32 anytime from the button above.")

    def _finish_onboarding_if_needed(self):
        if self._is_onboarding:
            FIRST_RUN_FILE.parent.mkdir(parents=True, exist_ok=True)
            FIRST_RUN_FILE.write_text("done")
            self._is_onboarding = False

    def _back_to_home(self):
        self._update_home_page()
        self._stack.fade_to(self._page_index("home"))
