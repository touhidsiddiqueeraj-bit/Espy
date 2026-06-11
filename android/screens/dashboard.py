from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.clock import Clock
from kivy.metrics import dp

from backend.discovery import DiscoveryThread, usb_probe
from backend.models import Device


class DashboardScreen(Screen):
    def on_enter(self):
        self._clear_list()
        self.disco = DiscoveryThread(
            on_device_found=self._on_device_found,
            on_device_lost=self._on_device_lost,
            on_usb_found=self._on_usb_found,
        )
        self.disco.start()
        Clock.schedule_interval(self._refresh_usb, 3)
        self.ids.status_label.text = "Scanning..."

    def on_leave(self):
        if hasattr(self, "disco"):
            self.disco.stop()
        Clock.unschedule(self._refresh_usb)

    def _clear_list(self):
        self.ids.device_list.clear_widgets()

    def _on_device_found(self, dev: Device):
        Clock.schedule_once(lambda dt: self._add_row(dev))

    def _add_row(self, dev: Device):
        box = BoxLayout(size_hint_y=None, height=dp(52), spacing=dp(8))

        info = Label(
            text=f"{dev.label}\n{dev.ip}:{dev.port}",
            size_hint_x=0.6,
            halign="left",
            valign="middle",
            text_size=(None, None),
        )
        info.bind(text_size=lambda *a: setattr(info, "text_size", (info.width, None)))
        box.add_widget(info)

        ota_btn = Button(
            text="OTA",
            size_hint_x=0.2,
            background_color=(0.2, 0.4, 0.8, 1),
        )
        ota_btn.bind(on_press=lambda bt, d=dev: self.open_ota(d))
        box.add_widget(ota_btn)

        self.ids.device_list.add_widget(box)
        count = len(self.ids.device_list.children)
        self.ids.status_label.text = f"{count} device(s)"

    def _on_device_lost(self, name: str):
        Clock.schedule_once(lambda dt: self._refresh_from_known())

    def _refresh_from_known(self):
        pass

    def _on_usb_found(self, ports: list):
        Clock.schedule_once(lambda dt: self._update_usb(ports))

    def _update_usb(self, ports: list):
        for port in ports:
            exists = False
            for child in self.ids.device_list.children:
                if isinstance(child, BoxLayout) and hasattr(child, "usb_port"):
                    if child.usb_port == port["port"]:
                        exists = True
                        break
            if not exists:
                self._add_usb_row(port)

    def _add_usb_row(self, port: dict):
        box = BoxLayout(size_hint_y=None, height=dp(52), spacing=dp(8))
        box.usb_port = port["port"]

        info = Label(
            text=f"USB: {port['port']}\n{port.get('description', '')}",
            size_hint_x=0.6,
            halign="left",
            valign="middle",
            text_size=(None, None),
        )
        info.bind(text_size=lambda *a: setattr(info, "text_size", (info.width, None)))
        box.add_widget(info)

        flash_btn = Button(
            text="Flash",
            size_hint_x=0.2,
            background_color=(0.2, 0.6, 0.2, 1),
        )
        flash_btn.bind(on_press=lambda bt, p=port["port"]: self.open_flash(p))
        box.add_widget(flash_btn)

        self.ids.device_list.add_widget(box)

    def _refresh_usb(self, dt):
        ports = usb_probe()
        self._update_usb(ports)

    def open_flash(self, port: str):
        self.manager.current = "flash"
        self.manager.flash_port = port

    def open_ota(self, device: Device):
        self.manager.current = "ota"
        self.manager.ota_device = device
