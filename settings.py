"""Persistent settings for Espy.

Stores user preferences in a JSON file under APP_DIR:
  - theme: "light" (default) or "dark"
  - profiles: list of saved configuration profiles
  - last_update_check: ISO timestamp of last GitHub release check
  - latest_version: latest version seen on GitHub (for "new version" banner)

Other settings (mode_pref, devices cache) continue to use their own
files for backwards compatibility.
"""
from __future__ import annotations
import json
import time
from pathlib import Path
from typing import Any

from constants import APP_DIR
from espy_logging import get_logger

_log = get_logger("settings")

SETTINGS_FILE = APP_DIR / "settings.json"

_DEFAULT: dict[str, Any] = {
    "theme": "light",
    "profiles": [],            # list of {name, board, wifi_ssid, wifi_password, device_name}
    "last_update_check": 0,    # epoch seconds
    "latest_version": None,    # latest version string seen on GitHub
    "last_skipped_version": None,  # version the user dismissed
}


def load() -> dict[str, Any]:
    """Load settings from disk, merged with defaults."""
    data = dict(_DEFAULT)
    if SETTINGS_FILE.exists():
        try:
            on_disk = json.loads(SETTINGS_FILE.read_text())
            if isinstance(on_disk, dict):
                data.update(on_disk)
        except Exception as e:
            _log.warning("Could not parse %s: %s", SETTINGS_FILE, e)
    return data


def save(data: dict[str, Any]) -> None:
    """Persist settings to disk."""
    try:
        APP_DIR.mkdir(parents=True, exist_ok=True)
        SETTINGS_FILE.write_text(json.dumps(data, indent=2))
    except Exception as e:
        _log.warning("Could not write %s: %s", SETTINGS_FILE, e)


def get(key: str, default: Any = None) -> Any:
    """Read a single setting."""
    return load().get(key, default)


def set(key: str, value: Any) -> None:
    """Write a single setting (preserves others)."""
    data = load()
    data[key] = value
    save(data)


# ─── Profile helpers ────────────────────────────────────────────

def list_profiles() -> list[dict]:
    """Return saved configuration profiles."""
    return load().get("profiles", [])


def get_profile(name: str) -> dict | None:
    """Return the named profile, or None if not found."""
    for p in list_profiles():
        if p.get("name") == name:
            return p
    return None


def save_profile(profile: dict) -> bool:
    """Insert or update a profile (matched by name). Returns True on success."""
    if not profile.get("name"):
        return False
    data = load()
    profiles = data.get("profiles", [])
    # Replace if exists, else append.
    for i, p in enumerate(profiles):
        if p.get("name") == profile["name"]:
            profiles[i] = profile
            break
    else:
        profiles.append(profile)
    data["profiles"] = profiles
    save(data)
    return True


def delete_profile(name: str) -> None:
    """Remove a named profile."""
    data = load()
    data["profiles"] = [p for p in data.get("profiles", []) if p.get("name") != name]
    save(data)
