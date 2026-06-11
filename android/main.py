import os
import sys

from kivy.config import Config

Config.set("kivy", "log_level", "info")
Config.set("kivy", "log_name", "easyesp_%y-%m-%d_%_.txt")

from kivy.app import App
from kivy.uix.screenmanager import ScreenManager
from kivy.core.window import Window

from screens.dashboard import DashboardScreen
from screens.flash import FlashScreen
from screens.ota import OtaScreen


class EasyEspApp(App):
    def build(self):
        self.title = "EasyESP"
        Window.minimum_width = 320
        Window.minimum_height = 480

        sm = ScreenManager()
        sm.add_widget(DashboardScreen(name="dashboard"))
        sm.add_widget(FlashScreen(name="flash"))
        sm.add_widget(OtaScreen(name="ota"))
        return sm


if __name__ == "__main__":
    EasyEspApp().run()
