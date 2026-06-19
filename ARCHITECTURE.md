# Architecture

## Overview

EasyESP is a PyQt6 desktop application (with a Kivy-based Android companion) that compiles Arduino `.ino` sketches and uploads them to ESP32 devices over Wi-Fi (OTA). It also flashes base firmware via USB for first-time setup.

The system is structured in four layers:

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
│  │  · Captive portal (first-time Wi-Fi setup via browser) │ │
│  │  · OTA HTTP server (chunked upload + SHA-256 verify)   │ │
│  │  · UDP heartbeat broadcast (port 7777, every 5s)      │ │
│  │  · mDNS advertiser (easyesp-<name>.local)              │ │
│  │  · Crash watchdog (auto-rollback after 3 crashes)     │ │
│  │  · Serial bridge over TCP (port 3232)                  │ │
│  │  · LED state machine (5 modes: slow/fast/solid/double  │ │
│  │    /error)                                              │ │
│  └────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

---

## Directory Layout

```
easyesp/
├── main.py                       # Primary entry point
├── easyesp.py                    # Backward-compatible entry point
├── app.py                        # App bootstrap (QApplication, installer)
├── constants.py                  # App-wide constants, board defs, partitions
├── models.py                     # Data models (Device, InoConfig, LibraryInfo)
├── palette.py                    # Color palette and Qt stylesheet
├── parser.py                     # Arduino .ino file parser
│
├── ui/                           # UI layer
│   ├── main_window.py            # Advanced mode main window (731 lines)
│   ├── easy_overlay.py           # Easy mode overlay UI (1010 lines)
│   ├── drop_zone.py              # File drag-and-drop widget
│   ├── device_list.py            # Device list widget
│   ├── board_picker.py           # ESP32 board selector dialog
│   ├── config_dialog.py          # Flash configuration dialog
│   ├── partition_editor.py       # Visual partition table editor
│   ├── serial_logger.py          # Serial monitor (USB + Wi-Fi TCP)
│   ├── setup_wizard.py           # First-time USB setup wizard
│   ├── progress_scene.py         # Flash progress visualization
│   ├── animations.py             # UI animations (mascot bounce, checkmark)
│   ├── illustrations.py          # SVG illustrations and Espy mascot
│   └── wifi_picker.py            # Wi-Fi network picker
│
├── workers/                      # Background worker threads
│   ├── compiler.py               # Arduino CLI compile worker
│   ├── ota.py                    # OTA upload worker (HTTP chunked)
│   ├── usb_flash.py              # USB flash worker (esptool)
│   ├── serial_reader.py          # Serial/TCP reader worker
│   └── backup.py                 # Firmware backup/restore utility
│
├── discovery/                    # Network device discovery
│   ├── engine.py                 # Discovery engine (orchestrator)
│   ├── mdns.py                   # UDP heartbeat listener (cross-platform)
│   ├── arp.py                    # ARP scan for local subnet
│   ├── usb.py                    # USB port detection (VID/PID)
│   └── cache.py                  # Device cache persistence
│
├── firmware/                     # ESP32 base firmware
│   ├── easyesp_base.ino          # Base firmware (823 lines)
│   ├── easyesp_4mb.csv           # 4MB partition table CSV
│   ├── easyesp_base.bin          # Pre-compiled base firmware
│   └── build_base_firmware.py    # Script to rebuild base firmware
│
├── tools/                        # Bundled tooling
│   ├── install_arduino.py        # arduino-cli installer
│   ├── arduino-cli               # Bundled arduino-cli (Linux)
│   └── arduino-cli.exe           # Bundled arduino-cli (Windows)
│
├── assets/                       # App icons and assets
│   ├── easyesp.png
│   ├── easyesp_64.png
│   └── easyesp.ico
│
├── android/                      # Android companion app (Kivy)
│   ├── main.py                   # Android entry point
│   ├── buildozer.spec            # Buildozer config
│   ├── screens/                  # Kivy screen definitions
│   ├── backend/                  # Android backend (discovery, flash, OTA)
│   └── firmware/
│
├── screenshots/                  # Documentation screenshots
├── build/                        # PyInstaller build cache
└── dist/                         # PyInstaller output (binaries + APK)
```

---

## Data Flows

### 1. OTA Flash Flow

```
User drops .ino file
        │
        ▼
  DropZone.file_dropped signal
        │
        ▼
  Parse .ino → extract board directives, libs, config
        │
        ▼
  Show ConfigDialog (Advanced) or inline review (Easy)
        │
        ▼
  CompilerWorker compiles via arduino-cli
        │
        ├── Auto-installs missing Arduino libraries
        ├── Generates .bin firmware
        └── Returns binary path
        │
        ▼
  OtaWorker: HTTP chunked upload to ESP32 (port 8080)
        │
        ├── Phase 1: POST /ota/start (size + SHA-256 hash)
        ├── Phase 2: POST /ota/chunk (binary data chunks)
        ├── Phase 3: POST /ota/commit (verify + reboot)
        └── Phase 4: ESP32 reboots into new firmware
```

### 2. First-time Setup Flow

```
User plugs ESP32 via USB
        │
        ▼
  Discovery/USB detects port (VID/PID matching)
        │
        ▼
  SetupWizard guides through:
        ├── Board selection
        ├── Device naming
        └── Wi-Fi credentials entry
        │
        ▼
  UsbFlashWorker flashes easyesp_base.bin via esptool
        │
        ▼
  ESP32 boots → creates captive portal AP ("EasyESP-XXXXXX")
        │
        ▼
  User connects to AP → browser captive portal → enters Wi-Fi
        │
        ▼
  ESP32 connects to Wi-Fi → starts UDP heartbeat + mDNS
        │
        ▼
  DiscoveryEngine on desktop detects device → appears in list
```

### 3. Discovery Flow

```
Phase 1 (always on)
  └── UDP heartbeat listener (port 7777) + mDNS queries
       └── ESP32 broadcasts heartbeat JSON every 5s
           { "name": "...", "ip": "...", "version": "..." }

Phase 2 (on stale, ~20s without heartbeat)
  └── Check cached IPs from previous sessions
       └── Probe /easyesp/alive on port 8080

Phase 3 (last resort)
  └── ARP scan of local /24 subnet
       └── Probe each found host on port 8080

Devices removed from list after 20s with no response
```

### 4. Serial Monitor (USB & Wi-Fi)

```
USB mode:
  Serial reader worker (QThread) → pyserial → log display

Wi-Fi mode:
  TCP socket → raw connection to ESP32 port 3232
    → ESP32 bridges to its hardware serial (Serial/UART)
    → Bidirectional: user input sent as TCP TX, ESP32 responses as TCP RX
```

---

## Key Design Decisions

| Decision | Rationale |
|----------|-----------|
| **QStackedWidget navigation** | Pages stacked and switched by index; no navigation history needed |
| **FadeStack (Easy Mode)** | Custom animated stack with cross-fade transitions for polished feel |
| **Dual UI modes** | `EasyOverlay` overlays MainWindow in Easy mode, hidden in Advanced; no separate window management |
| **QThread workers** | All I/O (compilation, OTA, USB flash, serial) runs in worker threads to keep UI responsive |
| **Config inheritance** | `InoConfig` dataclass carries board, flash size, partition scheme, and optional CSV override through the pipeline |
| **SHA-256 verification** | OTA upload hashes the binary client-side; ESP32 verifies before committing |
| **Crash watchdog** | ESP32 tracks boot attempts; after 3 crashes reverts to previous firmware via OTA partition swap |

---

## Technology Stack

| Component | Technology |
|-----------|------------|
| Desktop UI | PyQt6 |
| Android UI | Kivy + Buildozer |
| Firmware | Arduino C++ (ESP32 Arduino Core) |
| Compilation | arduino-cli |
| USB Flashing | esptool |
| Network Discovery | UDP (port 7777) + mDNS + ARP |
| OTA Protocol | HTTP chunked upload (port 8080) |
| Serial Monitor | pyserial (USB) / raw TCP (Wi-Fi, port 3232) |
| Persistence | JSON cache file + ESP32 NVS |
| Desktop Build | PyInstaller |
| Android Build | Docker (kivy/buildozer) |
| Python | 3.10+ (desktop), 3.14 (Android) |
