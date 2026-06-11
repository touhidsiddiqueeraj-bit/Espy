from __future__ import annotations
import json
import time
import hashlib
import urllib.request
import threading

CHUNK_SIZE = 1024
TIMEOUT_TOTAL = 60
POST_FLASH_WINDOW = 15


class OtaUpdateThread(threading.Thread):
    def __init__(self, ip: str, port: int, bin_path: str,
                 on_progress: callable = None,
                 on_finished: callable = None,
                 on_failed: callable = None):
        super().__init__(daemon=True)
        self.ip = ip
        self.port = port
        self.bin_path = bin_path
        self.on_progress = on_progress
        self.on_finished = on_finished
        self.on_failed = on_failed

    def _post(self, path: str, data: bytes | dict,
              is_json: bool = False, timeout: int = 5) -> dict:
        url = f"http://{self.ip}:{self.port}{path}"
        if is_json:
            body = json.dumps(data).encode("utf-8")
            headers = {"Content-Type": "application/json"}
        else:
            body = data if isinstance(data, bytes) else b""
            headers = {"Content-Type": "application/octet-stream"}
        headers["Content-Length"] = str(len(body))
        req = urllib.request.Request(url, data=body, headers=headers, method="POST")
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return json.loads(resp.read().decode("utf-8"))

    def run(self):
        try:
            with open(self.bin_path, "rb") as f:
                firmware = f.read()

            size = len(firmware)
            checksum = hashlib.sha256(firmware).hexdigest()
            deadline = time.time() + TIMEOUT_TOTAL

            if self.on_progress:
                self.on_progress(2, "Connecting...")

            resp = self._post("/easyesp/start", {
                "firmware_size_bytes": size,
                "checksum_sha256": checksum,
                "version_tag": f"fw_{int(time.time())}",
                "compiled_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            }, is_json=True, timeout=5)

            if resp.get("status") != "ready" and not resp.get("accepted"):
                if self.on_failed:
                    self.on_failed("Device not ready.")
                return

            chunks = [firmware[i:i+CHUNK_SIZE] for i in range(0, size, CHUNK_SIZE)]
            total = len(chunks)

            for i, chunk in enumerate(chunks):
                if time.time() > deadline:
                    if self.on_failed:
                        self.on_failed("Upload timed out.")
                    return

                pct = int(5 + (i / total) * 85)
                if self.on_progress:
                    self.on_progress(pct, f"Uploading... {i+1}/{total}")

                ok = False
                for attempt in range(3):
                    try:
                        cr = self._post(f"/easyesp/chunk/{i}", chunk, timeout=2)
                        if cr.get("status") == "ok" or cr.get("chunk") == i:
                            ok = True
                            break
                    except Exception:
                        if attempt == 2:
                            break
                        time.sleep(0.3)

                if not ok:
                    if self.on_failed:
                        self.on_failed(f"Chunk {i+1} failed.")
                    return

            if self.on_progress:
                self.on_progress(92, "Verifying...")

            cr = self._post("/easyesp/commit", {
                "total_chunks": total,
                "total_bytes": size,
                "final_checksum": checksum, "checksum_type": "sha256",
            }, is_json=True, timeout=10)

            if cr.get("status") != "committed":
                reason = cr.get("reason", "unknown")
                if self.on_failed:
                    self.on_failed(f"Verification failed ({reason})")
                return

            if self.on_progress:
                self.on_progress(95, "Rebooting...")

            reboot_ms = cr.get("rebooting_in_ms", 2000)
            time.sleep(reboot_ms / 1000 + 1)

            deadline2 = time.time() + POST_FLASH_WINDOW
            while time.time() < deadline2:
                remaining = int(deadline2 - time.time())
                if self.on_progress:
                    self.on_progress(95, f"Waiting for device... {remaining}s")
                try:
                    req = urllib.request.Request(
                        f"http://{self.ip}:{self.port}/easyesp/alive"
                    )
                    with urllib.request.urlopen(req, timeout=2) as r:
                        alive = json.loads(r.read())
                        if alive.get("status") == "running":
                            if self.on_progress:
                                self.on_progress(100, "Done!")
                            if self.on_finished:
                                self.on_finished()
                            return
                except Exception:
                    pass
                time.sleep(2)

            if self.on_failed:
                self.on_failed("Device didn't respond after reboot.")

        except Exception as e:
            if self.on_failed:
                self.on_failed(str(e))
