from kivy.uix.screenmanager import Screen
from kivy.clock import Clock
from kivy.properties import StringProperty, NumericProperty

from backend.ota import OtaUpdateThread
from backend.models import Device


class OtaScreen(Screen):
    status = StringProperty("Ready")
    progress = NumericProperty(0)
    device_label = StringProperty("")

    def on_enter(self):
        dev: Device = getattr(self.manager, "ota_device", None)
        if dev:
            self.device_label = dev.label
        else:
            self.device_label = "No device selected"
        self.progress = 0
        self.status = "Ready"

    def on_leave(self):
        pass

    def start_ota(self):
        dev: Device = getattr(self.manager, "ota_device", None)
        if not dev or not dev.ip:
            self.status = "No device selected"
            return

        import os
        bin_path = ""
        candidates = [
            os.path.join(os.path.dirname(__file__), "..", "firmware", "easyesp_base.bin"),
            os.path.join(os.getcwd(), "firmware", "easyesp_base.bin"),
        ]
        for c in candidates:
            if os.path.isfile(c):
                bin_path = c
                break
        if not bin_path:
            self.status = "Firmware binary not found"
            return

        self._thread = OtaUpdateThread(
            ip=dev.ip,
            port=dev.port,
            bin_path=bin_path,
            on_progress=self._on_progress,
            on_finished=self._on_finished,
            on_failed=self._on_failed,
        )
        self._thread.start()
        self.status = "Uploading..."

    def _on_progress(self, pct: int, msg: str):
        Clock.schedule_once(lambda dt: self._update(pct, msg))

    def _update(self, pct: int, msg: str):
        self.progress = pct
        self.status = msg

    def _on_finished(self):
        Clock.schedule_once(lambda dt: self._done())

    def _done(self):
        self.progress = 100
        self.status = "OTA update complete!"

    def _on_failed(self, err: str):
        Clock.schedule_once(lambda dt: self._fail(err))

    def _fail(self, err: str):
        self.status = f"Failed: {err}"
        self.progress = 0

    def back(self):
        self.manager.current = "dashboard"
