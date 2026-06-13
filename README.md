# Espy

> Getting people into IoT. Vibe coding got you the code — Espy gets it on the hardware.

[![License: Non-Commercial](https://img.shields.io/badge/License-Non--Commercial-blue.svg)](LICENSE.md)
[![Python](https://img.shields.io/badge/python-3.10+-brightgreen)]()
[![Platform](https://img.shields.io/badge/platform-Linux%20%7C%20Windows-lightgrey)]()

Vibe coding has already dropped the barrier to entry — anyone can get good code now. Espy drops the **next barrier**: getting that code onto real hardware. No wrestling with Arduino IDE, no board configs, no digging for missing libraries, no USB cables after the first flash. Drop a `.ino` file, and Espy handles the rest — auto board detection, auto library resolution, wiring diagrams, and one-click OTA upload.

Espy is a cross-platform desktop application designed to get as many people as possible on board with IoT. It enables **one-click wireless firmware updates for ESP32 microcontrollers over Wi-Fi (OTA)** and handles first-time USB setup. Drop an Arduino `.ino` sketch file onto the app — it compiles it via `arduino-cli` and uploads the binary to the ESP32 over the network. No configuration required.

### What's New

- **Faster OTA** — Chunk size increased to 4 KB for quicker wireless uploads
- **Smarter board detection** — Partial board name matching + fallback for unrecognized boards
- **Cached mascot animations** — No more re-rendering Espy's moods on every resize


## Quick Start

### Easy Mode
Launch Espy, drop your `.ino` file on the drop zone, and flash. No configuration needed.

### Advanced Mode
Switch to Advanced mode for full control over board selection, partition layout, flash size, and OTA settings.

### Setup a New Device
Plug in via USB once to flash the base firmware. After that, all updates happen over Wi-Fi.

---

## Features

- **One-click OTA** — Drop any `.ino` file; Espy compiles it and uploads over Wi-Fi
- **Auto board detection** — Parses your sketch and selects the right ESP32 board automatically
- **Auto library resolver** — Detects missing libraries and fetches them on the fly
- **Wiring diagram help** — Visual pinout diagrams for common ESP32 boards, no more guessing
- **Automatic network discovery** — Finds ESP32s on your local network via mDNS and UDP heartbeat
- **Dual mode UI** — Simple drag-and-drop Easy mode + Advanced mode with full partition/flash control
- **Serial monitor** — USB and Wi-Fi serial monitoring with baud rate and TCP port selection
- **Crash recovery** — Automatic rollback after repeated crashes (ESP32-side watchdog)
- **Captive portal setup** — New devices broadcast a setup Wi-Fi network for first-time configuration
- **Partition editor** — Visual and CSV-based partition table editing
- **Espy mascot** — Animated ESP32 mascot with multiple moods guides the experience

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

# Run Espy
python main.py
```

On first launch, Espy will automatically download `arduino-cli` and install the ESP32 Arduino core.

---

## Development

```bash
# Run from source
python main.py

# Build with PyInstaller
pyinstaller easyesp.spec
```

---

## License

This project is licensed under a **Non-Commercial License**. See [`LICENSE.md`](LICENSE.md) for full terms.

Commercial use is prohibited without prior written permission from the copyright holder.

---

*Built with PyQt6, esptool, and lots of ☕*
