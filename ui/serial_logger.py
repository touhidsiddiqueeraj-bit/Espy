from __future__ import annotations
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QLineEdit, QComboBox, QTextEdit, QFrame, QSplitter,
)
from PyQt6.QtCore import Qt, pyqtSignal, QTimer
from PyQt6.QtGui import QFont

from palette import WARM_PASTEL as C
from workers.serial_reader import SerialReaderWorker


class SerialLogger(QWidget):
    closed = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._worker = SerialReaderWorker()
        self._worker.data_received.connect(self._on_data)
        self._worker.connected.connect(self._on_connected)
        self._worker.disconnected.connect(self._on_disconnected)
        self._worker.error.connect(self._on_worker_error)
        self._baudrates = ["9600", "19200", "38400", "57600", "74880", "115200", "230400", "921600"]
        self._auto_scroll = True
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(6)

        # ── Toolbar ──────────────────────────────────────────
        toolbar = QFrame()
        toolbar.setObjectName("card")
        toolbar.setStyleSheet(
            f"QFrame#card {{ background: {C['card']}; border-bottom: 1px solid {C['border']}; "
            f"border-radius: 0px; border-top: none; border-left: none; border-right: none; }}"
        )
        tl = QHBoxLayout(toolbar)
        tl.setContentsMargins(14, 10, 14, 10)
        tl.setSpacing(8)

        mode_lbl = QLabel("Mode:")
        mode_lbl.setStyleSheet(f"color: {C['text_muted']}; font-size: 13px; font-weight: 600; background: transparent;")
        tl.addWidget(mode_lbl)

        self._mode_combo = QComboBox()
        self._mode_combo.addItems(["USB", "Wi-Fi"])
        self._mode_combo.currentTextChanged.connect(self._on_mode_changed)
        self._mode_combo.setToolTip("USB: connect via serial cable · Wi-Fi: connect via network")
        self._mode_combo.setFixedHeight(32)
        tl.addWidget(self._mode_combo)

        # Styled separator
        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.VLine)
        sep.setFixedHeight(20)
        sep.setStyleSheet(f"color: {C['border']}; background: {C['border']}; margin: 0 4px;")
        tl.addWidget(sep)

        # USB controls
        self._port_combo = QComboBox()
        self._port_combo.setMinimumWidth(160)
        self._port_combo.setFixedHeight(32)
        self._port_combo.setToolTip("Serial port")
        self._port_combo.addItem("Detecting ports...")
        tl.addWidget(self._port_combo)

        self._baud_combo = QComboBox()
        self._baud_combo.addItems(self._baudrates)
        self._baud_combo.setCurrentText("115200")
        self._baud_combo.setFixedHeight(32)
        self._baud_combo.setToolTip("Baud rate")
        tl.addWidget(self._baud_combo)

        # Wi-Fi controls (hidden by default)
        self._host_input = QLineEdit()
        self._host_input.setPlaceholderText("192.168.1.x")
        self._host_input.setFixedWidth(140)
        self._host_input.setFixedHeight(32)
        self._host_input.setToolTip("ESP32 IP address")
        self._host_input.hide()
        tl.addWidget(self._host_input)

        self._tcp_port_input = QLineEdit()
        self._tcp_port_input.setPlaceholderText("3232")
        self._tcp_port_input.setFixedWidth(60)
        self._tcp_port_input.setFixedHeight(32)
        self._tcp_port_input.setToolTip("TCP port (default: 3232)")
        self._tcp_port_input.hide()
        tl.addWidget(self._tcp_port_input)

        self._connect_btn = QPushButton("Connect")
        self._connect_btn.setObjectName("primary")
        self._connect_btn.setFixedHeight(32)
        self._connect_btn.setStyleSheet(
            f"QPushButton {{ min-width: 90px; max-width: 110px; font-size: 13px; "
            f"font-weight: 600; padding: 0 16px; border-radius: 8px; }}"
        )
        self._connect_btn.clicked.connect(self._toggle_connection)
        self._connect_btn.setToolTip("Connect to device")
        tl.addWidget(self._connect_btn)

        tl.addStretch()

        self._back_btn = QPushButton("← Back")
        self._back_btn.setObjectName("ghost")
        self._back_btn.setFixedHeight(32)
        self._back_btn.setStyleSheet(
            f"QPushButton {{ font-size: 13px; padding: 0 14px; "
            f"background: transparent; border: 1px solid {C['border']}; "
            f"border-radius: 8px; color: {C['text_muted']}; }}"
            f"QPushButton:hover {{ background: {C['card_hover']}; }}"
        )
        self._back_btn.clicked.connect(self._go_back)
        self._back_btn.setToolTip("Return to main page")
        tl.addWidget(self._back_btn)

        self._clear_btn = QPushButton("Clear")
        self._clear_btn.setObjectName("ghost")
        self._clear_btn.setFixedHeight(32)
        self._clear_btn.setStyleSheet(
            f"QPushButton {{ font-size: 13px; padding: 0 14px; "
            f"background: transparent; border: 1px solid {C['border']}; "
            f"border-radius: 8px; color: {C['text_muted']}; }}"
            f"QPushButton:hover {{ background: {C['card_hover']}; }}"
        )
        self._clear_btn.clicked.connect(self._clear_log)
        self._clear_btn.setToolTip("Clear output")
        tl.addWidget(self._clear_btn)

        layout.addWidget(toolbar)

        # ── Status bar ───────────────────────────────────────
        self._status_lbl = QLabel("Disconnected")
        self._status_lbl.setStyleSheet(
            f"color: {C['text_muted']}; font-size: 12px; padding: 3px 14px; "
            f"background: {C['bg']};"
        )
        layout.addWidget(self._status_lbl)

        # ── Log output ───────────────────────────────────────
        self._output = QTextEdit()
        self._output.setReadOnly(True)
        self._output.setFont(QFont("Courier New", 11))
        self._output.setStyleSheet(
            f"QTextEdit {{ background: #1a1a2e; color: #e0e0e0; border: none; "
            f"border-radius: 8px; padding: 8px; }}"
        )
        self._output.verticalScrollBar().valueChanged.connect(self._on_scroll)
        layout.addWidget(self._output, 1)

        # ── Send bar ─────────────────────────────────────────
        send_bar = QFrame()
        send_bar.setObjectName("card")
        send_bar.setStyleSheet(
            f"QFrame#card {{ background: {C['card']}; border-top: 1px solid {C['border']}; "
            f"border-radius: 0; border-bottom: none; border-left: none; border-right: none; }}"
        )
        sl = QHBoxLayout(send_bar)
        sl.setContentsMargins(12, 8, 12, 8)
        sl.setSpacing(8)

        self._send_input = QLineEdit()
        self._send_input.setPlaceholderText("Type a command and press Enter...")
        self._send_input.setFixedHeight(34)
        self._send_input.setStyleSheet(
            f"font-size: 13px; padding: 4px 10px; background: white; "
            f"border: 1px solid {C['border']}; border-radius: 8px;"
        )
        self._send_input.returnPressed.connect(self._send)
        sl.addWidget(self._send_input, 1)

        self._send_btn = QPushButton("Send")
        self._send_btn.setObjectName("primary")
        self._send_btn.setFixedHeight(34)
        self._send_btn.setFixedWidth(80)
        self._send_btn.setEnabled(False)
        self._send_btn.clicked.connect(self._send)
        self._send_btn.setToolTip("Send command to device")
        self._send_btn.setStyleSheet(
            f"QPushButton {{ font-size: 13px; font-weight: 600; "
            f"min-width: 80px; max-width: 80px; width: 80px; "
            f"min-height: 34px; max-height: 34px; "
            f"padding: 0 8px; border-radius: 8px; "
            f"background: {C['accent']}; color: white; border: none; }}"
            f"QPushButton:hover {{ background: {C['accent_hover']}; }}"
            f"QPushButton:disabled {{ background: {C['border']}; color: {C['text_faint']}; }}"
        )
        sl.addWidget(self._send_btn)

        layout.addWidget(send_bar)

        # Refresh ports on startup
        QTimer.singleShot(200, self._refresh_ports)

    def _on_mode_changed(self, mode: str):
        is_usb = mode == "USB"
        self._port_combo.setVisible(is_usb)
        self._baud_combo.setVisible(is_usb)
        self._host_input.setVisible(not is_usb)
        self._tcp_port_input.setVisible(not is_usb)
        if is_usb:
            self._refresh_ports()

    def _refresh_ports(self):
        try:
            import serial.tools.list_ports
            ports = list(serial.tools.list_ports.comports())
            self._port_combo.clear()
            for p in ports:
                self._port_combo.addItem(f"{p.device} ({p.description})", p.device)
            if not ports:
                self._port_combo.addItem("No ports found")
        except Exception:
            self._port_combo.clear()
            self._port_combo.addItem("Could not scan ports")

    def _toggle_connection(self):
        if self._worker.isRunning():
            self._disconnect()
        else:
            self._connect()

    def _connect(self):
        if self._mode_combo.currentText() == "USB":
            if self._port_combo.count() == 0 or self._port_combo.currentData() is None:
                self._log_line("No serial port selected")
                return
            port = self._port_combo.currentData()
            baud = int(self._baud_combo.currentText())
            self._log_line(f"Connecting to {port} @ {baud} baud...")
            self._status_lbl.setText(f"Connecting to {port}...")
            self._worker.connect_serial(port, baud)
        else:
            host = self._host_input.text().strip()
            if not host:
                self._log_line("Enter an IP address")
                return
            port_text = self._tcp_port_input.text().strip() or "3232"
            try:
                tcp_port = int(port_text)
            except ValueError:
                self._log_line("Invalid port number")
                return
            self._log_line(f"Connecting to {host}:{tcp_port}...")
            self._status_lbl.setText(f"Connecting to {host}:{tcp_port}...")
            self._worker.connect_tcp(host, tcp_port)

    def _disconnect(self):
        self._worker.disconnect()
        self._connect_btn.setText("Connect")
        self._connect_btn.setEnabled(True)
        self._send_btn.setEnabled(False)
        self._send_input.setEnabled(False)
        self._status_lbl.setText("Disconnected")
        self._log_line("Disconnected")

    def _on_connected(self):
        self._connect_btn.setText("Disconnect")
        self._send_btn.setEnabled(True)
        self._send_input.setEnabled(True)
        self._status_lbl.setText("Connected")
        self._log_line("Connected")

    def _on_disconnected(self):
        self._connect_btn.setText("Connect")
        self._connect_btn.setEnabled(True)
        self._send_btn.setEnabled(False)
        self._send_input.setEnabled(False)
        self._status_lbl.setText("Disconnected")

    def _on_worker_error(self, msg: str):
        self._log_line(f"ERROR: {msg}")
        self._status_lbl.setText(f"Error: {msg}")
        self._disconnect()

    def _on_data(self, text: str):
        self._log_line(text.rstrip())

    def _send(self):
        text = self._send_input.text()
        if text and self._worker.isRunning():
            self._worker.send(text + "\n")
            self._log_line(f">>> {text}")
            self._send_input.clear()

    def _clear_log(self):
        self._output.clear()

    def _log_line(self, text: str):
        self._output.append(text)
        if self._auto_scroll:
            sb = self._output.verticalScrollBar()
            sb.setValue(sb.maximum())

    def _on_scroll(self, val: int):
        sb = self._output.verticalScrollBar()
        self._auto_scroll = val >= sb.maximum() - 5

    def _go_back(self):
        self._worker.disconnect()
        self.closed.emit()

    def closeEvent(self, event):
        self._worker.disconnect()
        self.closed.emit()
        super().closeEvent(event)
