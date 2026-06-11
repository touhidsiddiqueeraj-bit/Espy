from __future__ import annotations
import sys
import os
import traceback

from PyQt6.QtWidgets import QApplication, QMessageBox
from PyQt6.QtCore import Qt

from constants import APP_NAME, APP_VERSION, APP_DIR, SYSTEM_FONT, MONO_FONT
from palette import stylesheet
from ui.main_window import MainWindow
from tools.install_arduino import download_arduino_cli, install_esp32_core


def setup_high_dpi():
    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
    )


def _run_installer() -> bool:
    cli = download_arduino_cli()
    if not cli:
        return False
    install_esp32_core(cli)
    return True


def run():
    setup_high_dpi()
    app = QApplication(sys.argv)
    app.setApplicationName(APP_NAME)
    app.setApplicationVersion(APP_VERSION)
    app.setStyleSheet(stylesheet())

    # Set default font
    font = app.font()
    font.setPointSize(10)
    font.setFamilies([SYSTEM_FONT.split(",")[0].strip().strip("'")])
    app.setFont(font)

    # Ensure arduino-cli is installed on first launch
    try:
        _run_installer()
    except Exception:
        traceback.print_exc()

    window = MainWindow()
    window.show()
    sys.exit(app.exec())
