# EasyESP

> Flash your ESP32 wirelessly in one click. Drop a `.ino` file, pick a device, done.

[![License: Non-Commercial](https://img.shields.io/badge/License-Non--Commercial-blue.svg)](LICENSE.md)
[![Python](https://img.shields.io/badge/python-3.10+-brightgreen)]()
[![Platform](https://img.shields.io/badge/platform-Linux%20%7C%20Windows%20%7C%20Android-lightgrey)]()

EasyESP is a cross-platform desktop application (with an Android companion app) that enables **one-click wireless firmware updates for ESP32 microcontrollers over Wi-Fi (OTA)**. It also handles first-time USB setup. Drop an Arduino `.ino` sketch file onto the app, it compiles it via `arduino-cli`, and uploads the binary to the ESP32 over the network.


## Quick Start

### Easy Mode
Launch EasyESP, drop your `.ino` file on the drop zone, and flash. No configuration needed.

### Advanced Mode
Switch to Advanced mode for full control over board selection, partition layout, flash size, and OTA settings.

### Setup a New Device
Plug in via USB once to flash the base firmware. After that, all updates happen over Wi-Fi.

---

## Features

- **One-click OTA** — Drop any `.ino` file; EasyESP compiles it and uploads over Wi-Fi
- **Automatic network discovery** — Finds ESP32s on your local network via mDNS and UDP heartbeat
- **Dual mode UI** — Simple drag-and-drop Easy mode + Advanced mode with full partition/flash control
- **Serial monitor** — USB and Wi-Fi serial monitoring with baud rate and TCP port selection
- **Batch flashing** — Flash the same firmware to multiple devices simultaneously
- **Crash recovery** — Automatic rollback after repeated crashes (ESP32-side watchdog)
- **Captive portal setup** — New devices broadcast a setup Wi-Fi network for first-time configuration
- **Partition editor** — Visual and CSV-based partition table editing
- **Espy mascot** — Animated ESP32 mascot with multiple moods guides the experience
- **Android companion app** — Flash and monitor ESP32s from your phone

---

## Architecture

See [`ARCHITECTURE.md`](ARCHITECTURE.md) for a detailed overview of the codebase structure and data flows.

```
┌─────────────────────────────────────────────────────────────┐
│                     UI LAYER (PyQt6)                        │
│  ┌─────────────┐  ┌──────────────┐  ┌───────────────────┐  │
│  │ MainWindow   │  │ EasyOverlay   │  │ SetupWizard       │  │
│  │ (Advanced)   │  │ (Easy Mode)   │  │ (First-time USB)  │  │
│  ├─────────────┤  ├──────────────┤  ├───────────────────┤  │
│  │ ConfigDialog │  │ SerialLogger │  │ DropZone           │  │
│  │ PartitionEdit│  │ DeviceList   │  │ ProgressScene      │  │
│  └──────────────┘  └──────────────┘  └───────────────────┘  │
├─────────────────────────────────────────────────────────────┤
│                   WORKERS (QThreads)                        │
│  ┌──────────────┐  ┌──────────────┐  ┌───────────────────┐  │
│  │ CompilerWk    │  │ OtaWorker     │  │ UsbFlashWorker    │  │
│  │ (arduino-cli) │  │ (HTTP OTA)    │  │ (esptool)         │  │
│  └──────────────┘  └──────────────┘  └───────────────────┘  │
├─────────────────────────────────────────────────────────────┤
│                    DISCOVERY LAYER                          │
│  ┌────────────────────────────────────────────────────────┐ │
│  │ DiscoveryEngine (mDNS + UDP heartbeat + ARP + USB)     │ │
│  └────────────────────────────────────────────────────────┘ │
├─────────────────────────────────────────────────────────────┤
│                   FIRMWARE (ESP32 C++)                      │
│  ┌────────────────────────────────────────────────────────┐ │
│  │ easyesp_base.ino                                       │ │
│  │  - Captive portal for Wi-Fi setup                      │ │
│  │  - OTA HTTP server (chunked upload + SHA-256 verify)   │ │
│  │  - UDP heartbeat broadcast (port 7777)                 │ │
│  │  - mDNS advertiser (easyesp-<name>.local)              │ │
│  │  - Crash watchdog with auto-rollback                   │ │
│  │  - Serial bridge over TCP (port 3232)                  │ │
│  └────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

---

## Requirements

- **Python 3.10+**
- **PyQt6** (`pip install PyQt6`)
- **Arduino CLI** (auto-downloaded on first launch)
- **esptool** (`pip install esptool`)
- **pyserial** (`pip install pyserial`)

---

## Installation

```bash
# Clone the repository
git clone https://github.com/touhidsiddiqueeraj-bit/Espy.git
cd Espy

# Install dependencies
pip install PyQt6 esptool pyserial

# Run EasyESP
python main.py
```

On first launch, EasyESP will automatically download `arduino-cli` and install the ESP32 Arduino core.

---

## Development

```bash
# Run from source
python main.py

# Build with PyInstaller
pyinstaller easyesp.spec
```

---

## Android Companion

An Android app built with Kivy is available under the `android/` directory. Build with Buildozer:

```bash
cd android
./build_apk.sh
```

---

## License

This project is licensed under a **Non-Commercial License**. See [`LICENSE.md`](LICENSE.md) for full terms.

Commercial use is prohibited without prior written permission from the copyright holder.

---

*Built with PyQt6, esptool, and lots of ☕*
