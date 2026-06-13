from __future__ import annotations
import sys
import os
import json
import subprocess
import traceback

from PyQt6.QtWidgets import QApplication, QMessageBox
from PyQt6.QtCore import Qt

from constants import APP_NAME, APP_VERSION, APP_DIR, SYSTEM_FONT, MONO_FONT
from palette import stylesheet
from ui.main_window import MainWindow
from ui.setup_splash import SetupSplash
from tools.install_arduino import download_arduino_cli, install_esp32_core


def setup_high_dpi():
    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
    )


def _run_installer(progress_callback=None) -> bool:
    cli = download_arduino_cli(progress_callback)
    if not cli:
        return False
    install_esp32_core(cli, progress_callback)
    return True


def _needs_setup() -> bool:
    from tools.install_arduino import _tools_dir, _get_data_dir
    tools = _tools_dir()
    cli_name = "arduino-cli.exe" if sys.platform == "win32" else "arduino-cli"
    cli_path = os.path.join(tools, cli_name)
    if not os.path.isfile(cli_path):
        return True
    cli = cli_path
    data_dir = _get_data_dir(cli)
    core_dir = os.path.join(data_dir, "packages", "esp32", "hardware", "esp32")
    if not os.path.isdir(core_dir):
        return True
    return False


def run():
    setup_high_dpi()
    app = QApplication(sys.argv)
    app.setApplicationName(APP_NAME)
    app.setApplicationVersion(APP_VERSION)
    app.setStyleSheet(stylesheet())

    # Set default font
    font = app.font()
    font.setPointSize(10)
    font.setFamilies([f.strip().strip("'") for f in SYSTEM_FONT.split(",")])
    app.setFont(font)

    # Show splash while setting up toolchain on first launch
    splash = None
    if _needs_setup():
        splash = SetupSplash()
        splash.show()
        QApplication.processEvents()

    try:
        _run_installer(splash.set_status if splash else None)
    except Exception:
        traceback.print_exc()

    if splash:
        splash.close()

    window = MainWindow()
    window.show()
    sys.exit(app.exec())
