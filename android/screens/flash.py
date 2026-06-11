from kivy.uix.screenmanager import Screen
from kivy.clock import Clock
from kivy.properties import StringProperty, NumericProperty

from backend.flash import UsbFlashThread


class FlashScreen(Screen):
    status = StringProperty("Ready")
    progress = NumericProperty(0)
    board = StringProperty("ESP32 Dev Module")

    def on_enter(self):
        self.status = f"Port: {getattr(self.manager, 'flash_port', '?')}"
        self.progress = 0

    def on_leave(self):
        self._cancel()

    def start_flash(self):
        port = getattr(self.manager, "flash_port", "")
        if not port:
            self.status = "No USB port selected"
            return

        base_fw = ""
        import os
        candidates = [
            os.path.join(os.path.dirname(__file__), "..", "firmware", "easyesp_base.bin"),
            os.path.join(os.getcwd(), "firmware", "easyesp_base.bin"),
        ]
        for c in candidates:
            if os.path.isfile(c):
                base_fw = c
                break
        if not base_fw:
            self.status = "Firmware binary not found"
            return

        self._thread = UsbFlashThread(
            port=port,
            base_fw_path=base_fw,
            board=self.board,
            on_progress=self._on_progress,
            on_finished=self._on_finished,
            on_failed=self._on_failed,
        )
        self._thread.start()
        self.status = "Flashing..."

    def _on_progress(self, pct: int, msg: str):
        Clock.schedule_once(lambda dt: self._update_progress(pct, msg))

    def _update_progress(self, pct: int, msg: str):
        self.progress = pct
        self.status = msg

    def _on_finished(self):
        Clock.schedule_once(lambda dt: self._done())

    def _done(self):
        self.progress = 100
        self.status = "Complete!"
        Clock.schedule_once(lambda dt: setattr(self, "status", "Done — unplug USB"), 0.5)

    def _on_failed(self, err: str):
        Clock.schedule_once(lambda dt: self._fail(err))

    def _fail(self, err: str):
        self.status = f"Failed: {err}"
        self.progress = 0

    def _cancel(self):
        if hasattr(self, "_thread") and self._thread and self._thread.is_alive():
            pass

    def back(self):
        self.manager.current = "dashboard"
