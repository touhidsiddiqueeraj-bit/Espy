from __future__ import annotations
import json
import time
import hashlib
import urllib.request
from typing import Optional

from PyQt6.QtCore import QThread, pyqtSignal

from models import Device
from constants import OTA_CHUNK_SIZE, OTA_TIMEOUT_TOTAL, POST_FLASH_HEARTBEAT_WINDOW


class OtaWorker(QThread):
    progress = pyqtSignal(int, str)
    finished = pyqtSignal()
    failed = pyqtSignal(str)

    def __init__(self, device: Device, bin_path: str, ota_password: str = ""):
        super().__init__()
        self.device = device
        self.bin_path = bin_path
        self.ota_password = ota_password

    def _post(self, path: str, data: bytes | dict,
              is_json: bool = False, timeout: int = 5) -> dict:
        url = f"http://{self.device.ip}:{self.device.port}{path}"
        if is_json:
            body = json.dumps(data).encode("utf-8")
            headers = {"Content-Type": "application/json"}
        else:
            body = data if isinstance(data, bytes) else b""
            headers = {"Content-Type": "application/octet-stream"}

        headers["Content-Length"] = str(len(body))
        if self.ota_password:
            headers["X-OTA-Password"] = self.ota_password

        req = urllib.request.Request(url, data=body, headers=headers, method="POST")
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return json.loads(resp.read().decode("utf-8"))

    def run(self):
        try:
            with open(self.bin_path, "rb") as f:
                firmware = f.read()

            size = len(firmware)
            checksum = hashlib.sha256(firmware).hexdigest()
            deadline = time.time() + OTA_TIMEOUT_TOTAL

            # Phase 1: Handshake
            self.progress.emit(2, "Connecting to device...")
            resp = self._post("/espy/start", {
                "firmware_size_bytes": size,
                "checksum_sha256": checksum,
                "version_tag": f"user_fw_{int(time.time())}",
                "compiled_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            }, is_json=True, timeout=5)

            if resp.get("status") != "ready" and not resp.get("accepted"):
                self.failed.emit("Device is not ready to receive firmware. It may be busy.")
                return

            # Phase 2: Chunked upload
            chunks = [firmware[i:i+OTA_CHUNK_SIZE] for i in range(0, size, OTA_CHUNK_SIZE)]
            total = len(chunks)

            for i, chunk in enumerate(chunks):
                if time.time() > deadline:
                    self.failed.emit("Upload timed out. Try again with a stronger Wi-Fi signal.")
                    return

                pct = int(5 + (i / total) * 85)
                self.progress.emit(pct, f"Uploading... {i+1}/{total}")

                ok = False
                for attempt in range(3):
                    try:
                        cr = self._post(f"/espy/chunk/{i}", chunk, timeout=2)
                        if cr.get("status") == "ok" or cr.get("chunk") == i:
                            ok = True
                            break
                    except Exception:
                        if attempt == 2:
                            break
                        time.sleep(0.3)

                if not ok:
                    self.failed.emit(
                        f"Upload stopped at chunk {i+1}. "
                        "Check your Wi-Fi signal and try again."
                    )
                    return

            # Phase 3: Commit
            self.progress.emit(92, "Verifying firmware...")
            cr = self._post("/espy/commit", {
                "total_chunks": total,
                "total_bytes": size,
                "final_checksum": checksum, "checksum_type": "sha256",
            }, is_json=True, timeout=10)

            if cr.get("status") != "committed":
                reason = cr.get("reason", "unknown")
                self.failed.emit(
                    f"Verification failed ({reason}). "
                    "The device kept its previous firmware."
                )
                return

            # Phase 4: Post-reboot heartbeat
            self.progress.emit(95, "Rebooting device...")
            reboot_ms = cr.get("rebooting_in_ms", 2000)
            time.sleep(reboot_ms / 1000 + 1)

            pb_deadline = time.time() + POST_FLASH_HEARTBEAT_WINDOW
            while time.time() < pb_deadline:
                remaining = int(pb_deadline - time.time())
                self.progress.emit(95, f"Waiting for device to come back online... {remaining}s")
                try:
                    req = urllib.request.Request(
                        f"http://{self.device.ip}:{self.device.port}/espy/alive"
                    )
                    with urllib.request.urlopen(req, timeout=2) as r:
                        alive = json.loads(r.read())
                        if alive.get("status") == "running":
                            self.progress.emit(100, "Done!")
                            self.device.firmware_version = alive.get("version", "unknown")
                            self.finished.emit()
                            return
                except Exception:
                    pass
                time.sleep(2)

            self.failed.emit(
                "Device didn't respond after reboot. "
                "The new firmware may have changed the OTA port, "
                "or the code has a bug. Plug in via USB to recover."
            )

        except Exception as e:
            self.failed.emit(str(e))
