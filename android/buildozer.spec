[app]

title = EasyESP

package.name = easyesp

package.domain = org.easyesp

source.dir = .

source.include_exts = py,png,jpg,kv,atlas,bin

version = 1.0.0

requirements = python3,kivy,pyserial

orientation = portrait

fullscreen = 0

presplash.filename = %(source.dir)s/assets/easyesp.png

icon.filename = %(source.dir)s/assets/easyesp.png

android.permissions = INTERNET, ACCESS_WIFI_STATE, CHANGE_WIFI_MULTICAST_STATE, ACCESS_NETWORK_STATE, ACCESS_FINE_LOCATION

android.extra_manifest_xml = %(source.dir)s/usb_features.xml

android.api = 34

android.minapi = 26

android.ndk = 27b

android.archs = arm64-v8a

android.allow_backup = False

android.accept_sdk_license = True

android.ndk_api = 26

p4a.source_dir = /home/user/p4a

p4a.setup_py = false

[buildozer]

log_level = 1

warn_on_root = 1
