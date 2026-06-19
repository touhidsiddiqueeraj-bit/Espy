"""Auto-update checker — fetches latest release from GitHub.

Checks github.com/touhidsiddiqueeraj-bit/Espy/releases/latest every 24h
and exposes a "new version available" signal that the UI can show as
a banner. Cached in settings.json to avoid hitting GitHub on every launch.
"""
from __future__ import annotations
import json
import re
import time
import urllib.request
from typing import Optional

from PyQt6.QtCore import QThread, pyqtSignal

from constants import APP_VERSION
import settings
from espy_logging import get_logger

_log = get_logger("updates")

# Where to check for releases. If the user forks the repo, change this.
REPO_OWNER = "touhidsiddiqueeraj-bit"
REPO_NAME = "Espy"
RELEASES_URL = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/releases/latest"

# Check at most once per day to be polite to GitHub.
CHECK_INTERVAL_SECONDS = 24 * 60 * 60


def _parse_version(v: str) -> tuple[int, ...]:
    """'v1.2.3' → (1, 2, 3). Non-numeric parts are dropped."""
    nums = re.findall(r"\d+", v)
    return tuple(int(n) for n in nums[:3])  # max 3 components


def _is_newer(latest: str, current: str) -> bool:
    """True if `latest` is a higher version than `current`."""
    try:
        return _parse_version(latest) > _parse_version(current)
    except Exception:
        return False


class UpdateChecker(QThread):
    """Background thread that checks GitHub for a newer release.

    Emits:
      - update_available(latest_version, release_url) if a newer version exists
      - up_to_date() if we're on the latest
      - check_failed(error_message) if the network/request failed

    The result is cached in settings.json so we don't hit GitHub more
    than once per day.
    """
    update_available = pyqtSignal(str, str)   # latest_version, html_url
    up_to_date       = pyqtSignal()
    check_failed     = pyqtSignal(str)

    def __init__(self, force: bool = False):
        super().__init__()
        self._force = force

    def run(self):
        # Throttle: skip if we checked recently, unless force=True.
        if not self._force:
            last_check = settings.get("last_update_check", 0)
            if time.time() - last_check < CHECK_INTERVAL_SECONDS:
                # Use cached result.
                cached_latest = settings.get("latest_version")
                if cached_latest and _is_newer(cached_latest, APP_VERSION):
                    skipped = settings.get("last_skipped_version")
                    if skipped != cached_latest:
                        url = settings.get("latest_release_url", "")
                        self.update_available.emit(cached_latest, url)
                return

        try:
            req = urllib.request.Request(
                RELEASES_URL,
                headers={
                    "Accept": "application/vnd.github+json",
                    "User-Agent": f"Espy/{APP_VERSION}",
                },
            )
            with urllib.request.urlopen(req, timeout=8) as resp:
                data = json.loads(resp.read().decode("utf-8"))

            latest = data.get("tag_name", "") or data.get("name", "")
            html_url = data.get("html_url", "")
            if not latest:
                self.check_failed.emit("GitHub response missing tag_name")
                return

            # Persist to settings.
            s = settings.load()
            s["last_update_check"] = time.time()
            s["latest_version"] = latest
            s["latest_release_url"] = html_url
            settings.save(s)

            if _is_newer(latest, APP_VERSION):
                skipped = settings.get("last_skipped_version")
                if skipped == latest:
                    _log.info("Update %s available but user skipped it.", latest)
                    return
                _log.info("Update available: %s (current: %s)", latest, APP_VERSION)
                self.update_available.emit(latest, html_url)
            else:
                _log.info("App is up to date (current: %s, latest: %s).",
                          APP_VERSION, latest)
                self.up_to_date.emit()

        except Exception as e:
            _log.warning("Update check failed: %s", e)
            self.check_failed.emit(str(e))


def mark_skipped(version: str) -> None:
    """User dismissed the update banner — don't bug them about this version again."""
    settings.set("last_skipped_version", version)
