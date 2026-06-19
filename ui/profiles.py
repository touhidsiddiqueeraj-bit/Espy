"""Configuration profiles dialog — save and load named WiFi/board/name profiles.

Saves typing the same WiFi password 8 times when flashing 8 devices.
"""
from __future__ import annotations

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QLineEdit, QComboBox, QFormLayout, QMessageBox, QListWidget,
    QListWidgetItem, QFrame, QInputDialog, QWidget,
)
from PyQt6.QtCore import Qt, pyqtSignal

from palette import WARM_PASTEL as C
from constants import BOARDS
from models import InoConfig
import settings
from espy_logging import get_logger

_log = get_logger("ui.profiles")


class ProfilesDialog(QDialog):
    """Manage saved configuration profiles.

    A profile stores: name, board, wifi_ssid, wifi_password, device_name.
    The user can apply a profile to the current ConfigDialog without
    re-typing the WiFi password every time.
    """

    profile_applied = pyqtSignal(dict)  # emitted when user picks a profile

    def __init__(self, current_cfg: InoConfig | None = None, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Configuration Profiles")
        self.setMinimumSize(560, 480)
        self.setStyleSheet(f"background: {C['bg']}; color: {C['text']};")
        self._current_cfg = current_cfg
        self._build_ui()
        self._refresh_list()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(12)

        title = QLabel("Configuration Profiles")
        title.setStyleSheet(f"font-size: 20px; font-weight: 700; color: {C['text']};")
        layout.addWidget(title)

        sub = QLabel(
            "Save your WiFi credentials, board type, and device name as a profile. "
            "Apply it to multiple devices without re-typing the password each time."
        )
        sub.setWordWrap(True)
        sub.setStyleSheet(f"color: {C['text_muted']}; font-size: 13px;")
        layout.addWidget(sub)

        # Profile list
        self._list = QListWidget()
        self._list.setStyleSheet(
            f"background: {C['card']}; border: 1px solid {C['border']}; border-radius: 8px;"
        )
        self._list.itemDoubleClicked.connect(self._apply_selected)
        layout.addWidget(self._list, 1)

        # Action buttons
        btn_row = QHBoxLayout()
        save_btn = QPushButton("Save current as profile")
        save_btn.setObjectName("primary")
        save_btn.clicked.connect(self._save_current)
        btn_row.addWidget(save_btn)
        apply_btn = QPushButton("Apply selected")
        apply_btn.setObjectName("secondary")
        apply_btn.clicked.connect(self._apply_selected)
        btn_row.addWidget(apply_btn)
        edit_btn = QPushButton("Edit")
        edit_btn.setObjectName("secondary")
        edit_btn.clicked.connect(self._edit_selected)
        btn_row.addWidget(edit_btn)
        delete_btn = QPushButton("Delete")
        delete_btn.setObjectName("danger")
        delete_btn.clicked.connect(self._delete_selected)
        btn_row.addWidget(delete_btn)
        close_btn = QPushButton("Close")
        close_btn.setObjectName("ghost")
        close_btn.clicked.connect(self.accept)
        btn_row.addWidget(close_btn)
        layout.addLayout(btn_row)

    def _refresh_list(self):
        self._list.clear()
        for p in settings.list_profiles():
            item = QListWidgetItem(
                f"{p.get('name', '?')}  —  {p.get('board', '?')}  /  "
                f"SSID: {p.get('wifi_ssid', '?')}  /  Device: {p.get('device_name', '?')}"
            )
            item.setData(Qt.ItemDataRole.UserRole, p)
            self._list.addItem(item)
        if self._list.count() == 0:
            item = QListWidgetItem("(no profiles yet — click 'Save current as profile')")
            item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEnabled)
            self._list.addItem(item)

    def _save_current(self):
        if not self._current_cfg:
            QMessageBox.information(self, "No config",
                "Drop a .ino file first so Espy has something to save as a profile.")
            return
        # Ask for a profile name
        name, ok = QInputDialog.getText(
            self, "Profile name", "Profile name:",
            text=self._current_cfg.device_name or "My Profile",
        )
        if not ok or not name.strip():
            return
        profile = {
            "name": name.strip(),
            "board": self._current_cfg.board,
            "wifi_ssid": self._current_cfg.wifi_ssid,
            "wifi_password": self._current_cfg.wifi_password,
            "device_name": self._current_cfg.device_name,
        }
        if settings.save_profile(profile):
            _log.info("Saved profile %r", profile["name"])
            self._refresh_list()
        else:
            QMessageBox.warning(self, "Save failed", "Profile name is required.")

    def _apply_selected(self):
        item = self._list.currentItem()
        if not item:
            return
        profile = item.data(Qt.ItemDataRole.UserRole)
        if not profile:
            return
        self.profile_applied.emit(profile)
        self.accept()

    def _edit_selected(self):
        """Open a dialog pre-filled with the selected profile's values.

        User can change any field (name, board, WiFi SSID, WiFi password,
        device name) and save. Uses settings.save_profile() which handles
        update-or-insert by name.
        """
        item = self._list.currentItem()
        if not item:
            QMessageBox.information(self, "No selection",
                "Select a profile to edit first.")
            return
        profile = item.data(Qt.ItemDataRole.UserRole)
        if not profile:
            return

        dlg = _EditProfileDialog(profile, self)
        if dlg.exec() and dlg.result_profile:
            new_profile = dlg.result_profile
            # If the name changed, delete the old one first
            old_name = profile.get("name", "")
            if old_name and old_name != new_profile["name"]:
                settings.delete_profile(old_name)
            settings.save_profile(new_profile)
            _log.info("Edited profile: %s → %s", old_name, new_profile["name"])
            self._refresh_list()

    def _delete_selected(self):
        item = self._list.currentItem()
        if not item:
            return
        profile = item.data(Qt.ItemDataRole.UserRole)
        if not profile:
            return
        name = profile.get("name", "")
        if QMessageBox.question(
            self, "Delete profile",
            f"Delete profile '{name}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        ) == QMessageBox.StandardButton.Yes:
            settings.delete_profile(name)
            _log.info("Deleted profile %r", name)
            self._refresh_list()


class _EditProfileDialog(QDialog):
    """Small dialog for editing an existing profile's fields.

    Pre-fills all fields with the profile's current values. On accept,
    result_profile contains the updated dict.
    """

    def __init__(self, profile: dict, parent=None):
        super().__init__(parent)
        self.setWindowTitle(f"Edit profile — {profile.get('name', '?')}")
        self.setMinimumWidth(440)
        self.setStyleSheet(f"background: {C['bg']}; color: {C['text']};")
        self.result_profile: dict | None = None
        self._build_ui(profile)

    def _build_ui(self, profile: dict):
        from PyQt6.QtWidgets import (
            QFormLayout, QLineEdit, QComboBox,
        )

        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(12)

        title = QLabel("Edit profile")
        title.setStyleSheet(f"font-size: 18px; font-weight: 700; color: {C['text']};")
        layout.addWidget(title)

        form = QFormLayout()
        form.setSpacing(10)
        form.setLabelAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)

        self._name_edit = QLineEdit(profile.get("name", ""))
        self._name_edit.setPlaceholderText("Profile name")

        self._board_combo = QComboBox()
        self._board_combo.addItems(list(BOARDS.keys()))
        current_board = profile.get("board", "ESP32 Dev Module")
        idx = self._board_combo.findText(current_board)
        if idx >= 0:
            self._board_combo.setCurrentIndex(idx)

        self._ssid_edit = QLineEdit(profile.get("wifi_ssid", ""))
        self._ssid_edit.setPlaceholderText("Wi-Fi network name")

        self._pass_edit = QLineEdit(profile.get("wifi_password", ""))
        self._pass_edit.setEchoMode(QLineEdit.EchoMode.Password)
        self._pass_edit.setPlaceholderText("Wi-Fi password")

        # Password show/hide toggle
        show_pass_btn = QPushButton("👁")
        show_pass_btn.setObjectName("secondary")
        show_pass_btn.setFixedWidth(36)
        show_pass_btn.setCheckable(True)
        show_pass_btn.setToolTip("Show / hide password")
        show_pass_btn.toggled.connect(
            lambda checked: self._pass_edit.setEchoMode(
                QLineEdit.EchoMode.Normal if checked
                else QLineEdit.EchoMode.Password
            )
        )
        pass_row = QHBoxLayout()
        pass_row.setContentsMargins(0, 0, 0, 0)
        pass_row.setSpacing(6)
        pass_row.addWidget(self._pass_edit, 1)
        pass_row.addWidget(show_pass_btn)
        pass_container = QWidget()
        pass_container.setLayout(pass_row)

        self._device_edit = QLineEdit(profile.get("device_name", ""))
        self._device_edit.setPlaceholderText("e.g. Kitchen Light")

        form.addRow("Profile name", self._name_edit)
        form.addRow("Board", self._board_combo)
        form.addRow("Wi-Fi SSID", self._ssid_edit)
        form.addRow("Wi-Fi password", pass_container)
        form.addRow("Device name", self._device_edit)
        layout.addLayout(form)

        btn_row = QHBoxLayout()
        btn_row.addStretch()
        save_btn = QPushButton("Save changes")
        save_btn.setObjectName("primary")
        save_btn.clicked.connect(self._save)
        btn_row.addWidget(save_btn)
        cancel_btn = QPushButton("Cancel")
        cancel_btn.setObjectName("ghost")
        cancel_btn.clicked.connect(self.reject)
        btn_row.addWidget(cancel_btn)
        layout.addLayout(btn_row)

    def _save(self):
        name = self._name_edit.text().strip()
        if not name:
            QMessageBox.warning(self, "Missing name", "Profile name is required.")
            return
        self.result_profile = {
            "name":         name,
            "board":        self._board_combo.currentText(),
            "wifi_ssid":    self._ssid_edit.text().strip(),
            "wifi_password": self._pass_edit.text(),
            "device_name":  self._device_edit.text().strip(),
        }
        self.accept()
