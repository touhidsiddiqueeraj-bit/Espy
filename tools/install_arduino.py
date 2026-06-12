from __future__ import annotations
import os
import sys
import stat
import json
import shutil
import subprocess
import hashlib
import time
import urllib.request
import urllib.error
import zipfile
import tarfile
from pathlib import Path


def _cb(fn, msg):
    if fn:
        fn(msg)


def _tools_dir() -> str:
    if getattr(sys, "frozen", False):
        base = sys._MEIPASS
    else:
        base = str(Path(__file__).parent.parent)
    tools = os.path.join(base, "tools")
    os.makedirs(tools, exist_ok=True)
    return tools


def _detect_platform() -> tuple[str, str, str]:
    """Return (arch, platform, ext) for arduino-cli download."""
    import platform
    machine = platform.machine().lower()
    if machine in ("amd64", "x86_64"):
        arch = "64bit"
    elif machine in ("aarch64", "arm64"):
        arch = "ARM64"
    elif machine.startswith("arm"):
        arch = "ARM32"
    else:
        arch = "32bit"

    if sys.platform == "win32":
        return arch, "Windows", ".zip"
    elif sys.platform == "darwin":
        return arch, "macOS", ".tar.gz"
    else:
        return arch, "Linux", ".tar.gz"


def _download_url(arch: str, platform: str) -> str:
    base = "https://downloads.arduino.cc/arduino-cli"
    # Map to release asset names (actual GitHub release naming)
    arch_map = {
        "64bit": "64bit",
        "32bit": "32bit",
        "ARM64": "ARM64",
        "ARMv6": "ARMv6",
        "ARMv7": "ARMv7",
    }
    a = arch_map.get(arch, "64bit")
    ext = ".zip" if platform == "Windows" else ".tar.gz"
    return f"{base}/arduino-cli_latest_{platform}_{a}{ext}"


def download_arduino_cli(progress_callback=None) -> str | None:
    tools = _tools_dir()
    cli_path = os.path.join(tools, "arduino-cli.exe" if sys.platform == "win32" else "arduino-cli")

    if os.path.isfile(cli_path):
        return cli_path

    arch, platform, ext = _detect_platform()
    url = _download_url(arch, platform)
    archive_path = os.path.join(tools, f"arduino-cli{ext}")

    _cb(progress_callback, "Downloading arduino-cli...")
    try:
        urllib.request.urlretrieve(url, archive_path)
    except Exception as e:
        _cb(progress_callback, f"Download failed: {e}")
        return None

    _cb(progress_callback, "Extracting arduino-cli...")
    try:
        if ext == ".zip":
            with zipfile.ZipFile(archive_path) as zf:
                for member in zf.namelist():
                    if member.endswith("arduino-cli") or member.endswith("arduino-cli.exe"):
                        zf.extract(member, tools)
                        extracted = os.path.join(tools, member)
                        if extracted != cli_path:
                            shutil.move(extracted, cli_path)
                        break
        else:
            with tarfile.open(archive_path, "r:gz") as tf:
                for member in tf.getmembers():
                    if member.name.endswith("arduino-cli") or member.name.endswith("arduino-cli.exe"):
                        tf.extract(member, tools)
                        extracted = os.path.join(tools, member.name)
                        if extracted != cli_path:
                            shutil.move(extracted, cli_path)
                        break
    except Exception as e:
        _cb(progress_callback, f"Extraction failed: {e}")
        return None
    finally:
        if os.path.isfile(archive_path):
            os.remove(archive_path)

    if os.path.isfile(cli_path):
        st = os.stat(cli_path)
        os.chmod(cli_path, st.st_mode | stat.S_IEXEC | stat.S_IXGRP | stat.S_IXOTH)
        return cli_path

    return None


_PACKAGE_INDEX_URL = "https://espressif.github.io/arduino-esp32/package_esp32_index.json"
_ESP32_CORE_VERSION = "3.3.10"
_HOST = "x86_64-pc-linux-gnu"


def _sha256_of(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while True:
            chunk = f.read(65536)
            if not chunk:
                break
            h.update(chunk)
    return h.hexdigest()


def _download_with_retry(url: str, path: str, checksum: str | None = None) -> bool:
    for attempt in range(3):
        try:
            urllib.request.urlretrieve(url, path)
        except Exception as e:
            if attempt < 2:
                print(f"  Retrying {url.split('/')[-1]} ({attempt+2}/3)...")
                time.sleep(2 * (attempt + 1))
                continue
            print(f"  Failed after 3 attempts: {e}")
            return False
        if checksum:
            expected = checksum.replace("SHA-256:", "").strip().lower()
            actual = _sha256_of(path)
            if actual != expected:
                if attempt < 2:
                    print(f"  Checksum mismatch, retrying...")
                    time.sleep(2 * (attempt + 1))
                    continue
                print(f"  Checksum mismatch for {url}")
                return False
        return True
    return False


def _extract_archive(archive_path: str, dest: str) -> bool:
    os.makedirs(dest, exist_ok=True)
    temp = dest + ".tmp"
    if os.path.isdir(temp):
        shutil.rmtree(temp)
    try:
        if archive_path.endswith(".zip"):
            with zipfile.ZipFile(archive_path) as zf:
                zf.extractall(temp)
        elif archive_path.endswith(".tar.gz"):
            with tarfile.open(archive_path, "r:gz") as tf:
                tf.extractall(temp)
        else:
            return False

        items = os.listdir(temp)
        if len(items) == 1 and os.path.isdir(os.path.join(temp, items[0])):
            inner = os.path.join(temp, items[0])
            for item in os.listdir(inner):
                shutil.move(os.path.join(inner, item), dest)
        else:
            for item in items:
                shutil.move(os.path.join(temp, item), dest)
        shutil.rmtree(temp)
        return True
    except Exception as e:
        if os.path.isdir(temp):
            shutil.rmtree(temp, ignore_errors=True)
        print(f"  Extraction error: {e}")
        return False


def _get_data_dir(cli: str) -> str:
    try:
        r = subprocess.run(
            [cli, "config", "dump", "--format", "json"],
            capture_output=True, text=True
        )
        if r.returncode == 0:
            cfg = json.loads(r.stdout)
            data_dir = cfg.get("directories", {}).get("data", "")
            if data_dir:
                return data_dir
    except Exception:
        pass
    default = os.path.expanduser("~/.arduino15")
    os.makedirs(default, exist_ok=True)
    return default


def install_esp32_core(cli: str, progress_callback=None) -> bool:
    data_dir = _get_data_dir(cli)
    packages_dir = os.path.join(data_dir, "packages", "esp32")
    os.makedirs(packages_dir, exist_ok=True)

    # Download package index
    _cb(progress_callback, "Downloading package index...")
    index_path = os.path.join(data_dir, "package_esp32_index.json")
    if not _download_with_retry(_PACKAGE_INDEX_URL, index_path):
        _cb(progress_callback, "Failed to download package index")
        return False

    with open(index_path) as f:
        index = json.load(f)

    # Find the esp32 version we want
    esp32_pkg = index["packages"][0]
    platform = None
    for p in esp32_pkg["platforms"]:
        if p["version"] == _ESP32_CORE_VERSION:
            platform = p
            break
    if not platform:
        _cb(progress_callback, f"ESP32 core v{_ESP32_CORE_VERSION} not found in package index")
        return False

    # Build (packager, name, version) tool lookup across all packages
    tool_lookup = {}
    for pkg in index["packages"]:
        for t in pkg.get("tools", []):
            tool_lookup[(pkg["name"], t["name"], t["version"])] = t

    # ── Download & extract core ────────────────────────
    core_dir = os.path.join(packages_dir, "hardware", "esp32", _ESP32_CORE_VERSION)
    if not os.path.isdir(core_dir):
        _cb(progress_callback, "Downloading ESP32 core (200MB+)...")
        core_zip = os.path.join(data_dir, "esp32-core.zip")
        if not _download_with_retry(platform["url"], core_zip, platform["checksum"]):
            _cb(progress_callback, "Failed to download ESP32 core")
            return False
        _cb(progress_callback, "Extracting ESP32 core...")
        if not _extract_archive(core_zip, core_dir):
            _cb(progress_callback, "Failed to extract ESP32 core")
            return False
        os.remove(core_zip)

    # ── Download & extract all tool dependencies ───────
    tools_dir = os.path.join(packages_dir, "tools")
    os.makedirs(tools_dir, exist_ok=True)

    for dep in platform["toolsDependencies"]:
        pk = dep["packager"]
        tn = dep["name"]
        tv = dep["version"]
        key = (pk, tn, tv)
        t = tool_lookup.get(key)
        if not t:
            continue

        # Find matching system for our host
        sys_info = None
        for s in t.get("systems", []):
            if s.get("host") == _HOST:
                sys_info = s
                break
        if not sys_info:
            continue

        tool_dir = os.path.join(tools_dir, tn, tv)
        if os.path.isdir(tool_dir):
            continue

        _cb(progress_callback, f"Downloading {tn} {tv}...")
        ext = ".zip" if sys_info["url"].endswith(".zip") else ".tar.gz"
        archive_path = os.path.join(data_dir, f"{tn}-{tv}{ext}")
        if not _download_with_retry(sys_info["url"], archive_path, sys_info["checksum"]):
            _cb(progress_callback, f"Skipping {tn} (download failed)")
            continue

        _cb(progress_callback, f"Extracting {tn}...")
        os.makedirs(tool_dir, exist_ok=True)
        if not _extract_archive(archive_path, tool_dir):
            shutil.rmtree(tool_dir, ignore_errors=True)
            continue
        os.remove(archive_path)

    # ── Update core index so arduino-cli knows about the platform ──
    _cb(progress_callback, "Updating arduino-cli core index...")
    subprocess.run([cli, "core", "update-index"], capture_output=True, text=True)

    # ── Write installed.json for the platform ─────
    installed_path = os.path.join(packages_dir, "installed.json")
    platforms_list = []
    if os.path.isfile(installed_path):
        try:
            with open(installed_path) as f:
                platforms_list = json.load(f)
        except Exception:
            pass

    record = {
        "name": "esp32",
        "version": _ESP32_CORE_VERSION,
        "url": platform["url"],
    }
    if record not in platforms_list:
        platforms_list.append(record)
    with open(installed_path, "w") as f:
        json.dump(platforms_list, f)

    _cb(progress_callback, "ESP32 core installation complete!")
    return True


def get_installed_libs(cli: str) -> set[str]:
    try:
        r = subprocess.run(
            [cli, "lib", "list", "--format", "json"],
            capture_output=True, text=True
        )
        if r.returncode != 0:
            return set()
        data = json.loads(r.stdout)
        if isinstance(data, list):
            return {lib.get("library", {}).get("name", "") for lib in data}
        if isinstance(data, dict):
            libs = data.get("libraries", [])
            return {lib.get("library", {}).get("name", "") for lib in libs}
    except Exception:
        return set()
    return set()


def install_missing_libs(cli: str, lib_names: list[str], progress_callback=None) -> list[str]:
    installed = get_installed_libs(cli)
    missing = [n for n in lib_names if n not in installed]
    if not missing:
        return []
    failed: list[str] = []
    for lib in missing:
        r = subprocess.run(
            [cli, "lib", "install", lib],
            capture_output=True, text=True
        )
        if r.returncode != 0:
            failed.append(lib)
        if progress_callback:
            progress_callback(lib, r.returncode == 0)
    return failed
