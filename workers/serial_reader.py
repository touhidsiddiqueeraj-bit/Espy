from __future__ import annotations
import socket
import select
import time
from PyQt6.QtCore import QThread, pyqtSignal


class SerialReaderWorker(QThread):
    data_received = pyqtSignal(str)
    connected = pyqtSignal()
    disconnected = pyqtSignal()
    error = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self._running = False
        self._mode: str = ""
        self._serial = None
        self._sock: socket.socket = None
        self._buffer = ""

    def connect_serial(self, port: str, baudrate: int = 115200):
        self._mode = "serial"
        self._port = port
        self._baudrate = baudrate
        self.start()

    def connect_tcp(self, host: str, port: int = 3232):
        self._mode = "tcp"
        self._host = host
        self._tcp_port = port
        self.start()

    def disconnect(self):
        self._running = False
        self.wait(2000)

    def send(self, data: str):
        if self._mode == "serial" and self._serial:
            try:
                self._serial.write(data.encode())
            except Exception as e:
                self.error.emit(f"Send failed: {e}")
        elif self._mode == "tcp" and self._sock:
            try:
                self._sock.sendall(data.encode())
            except Exception as e:
                self.error.emit(f"Send failed: {e}")

    def run(self):
        self._running = True
        try:
            if self._mode == "serial":
                self._run_serial()
            elif self._mode == "tcp":
                self._run_tcp()
        except Exception as e:
            self.error.emit(str(e))
        finally:
            self._cleanup()
            self.disconnected.emit()

    def _run_serial(self):
        import serial
        self._serial = serial.Serial(self._port, self._baudrate, timeout=0.5)
        self.connected.emit()
        while self._running:
            try:
                if self._serial.in_waiting:
                    raw = self._serial.read(self._serial.in_waiting)
                    text = raw.decode("utf-8", errors="replace")
                    self._buffer += text
                    if "\n" in self._buffer:
                        lines = self._buffer.split("\n")
                        for line in lines[:-1]:
                            self.data_received.emit(line + "\n")
                        self._buffer = lines[-1]
                else:
                    time.sleep(0.05)
            except serial.SerialException as e:
                self.error.emit(f"Serial error: {e}")
                break
            except Exception as e:
                self.error.emit(f"Read error: {e}")
                break

    def _run_tcp(self):
        self._sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._sock.settimeout(5.0)
        self._sock.connect((self._host, self._tcp_port))
        self._sock.setblocking(False)
        self.connected.emit()
        while self._running:
            try:
                r, _, _ = select.select([self._sock], [], [], 0.1)
                if r:
                    raw = self._sock.recv(4096)
                    if not raw:
                        break
                    text = raw.decode("utf-8", errors="replace")
                    self._buffer += text
                    if "\n" in self._buffer:
                        lines = self._buffer.split("\n")
                        for line in lines[:-1]:
                            self.data_received.emit(line + "\n")
                        self._buffer = lines[-1]
            except socket.timeout:
                continue
            except Exception as e:
                self.error.emit(f"TCP error: {e}")
                break

    def _cleanup(self):
        if self._serial:
            try:
                self._serial.close()
            except Exception:
                pass
            self._serial = None
        if self._sock:
            try:
                self._sock.close()
            except Exception:
                pass
            self._sock = None
