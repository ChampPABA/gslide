"""Playwright browser lifecycle management."""

import json
import os
from pathlib import Path

from playwright.sync_api import BrowserContext, Playwright, sync_playwright


class ProfileLockedError(Exception):
    """Raised when the persistent profile is already in use by another process."""


def active_profile_marker(user_data_dir: Path) -> Path:
    """Path to the marker recording which inner Chromium profile holds the session."""
    return user_data_dir.parent / "active-profile"


def resolve_profile_directory(user_data_dir: Path) -> str | None:
    """Return the inner profile-directory holding the Google session.

    Google's interactive login shards the signed-in account into a profile such
    as "Profile 1" rather than "Default". We snapshot that name into a marker at
    login (see auth.snapshot_active_profile); here we read it back so headless
    runs open the SAME profile. Falls back to Local State's last_used, else None
    (Chromium default = "Default").
    """
    marker = active_profile_marker(user_data_dir)
    if marker.exists():
        name = marker.read_text().strip()
        if name:
            return name

    local_state = user_data_dir / "Local State"
    if local_state.exists():
        try:
            last_used = json.loads(local_state.read_text())["profile"]["last_used"]
            if last_used:
                return last_used
        except Exception:
            pass
    return None


class BrowserSession:
    """Manages a persistent Chromium browser context backed by a user-data directory.

    The persistent profile lets Chromium natively persist and rotate Google
    session cookies across runs — no manual storage-state save/load. Non-headed
    runs use Chromium's new headless mode (``--headless=new``); the legacy
    headless shell is detected by Google and bounced to the account chooser.
    """

    _WIDTH = 1600
    _HEIGHT = 900

    def __init__(self, user_data_dir: Path, headed: bool = False) -> None:
        self._user_data_dir = user_data_dir
        self._headed = headed or os.environ.get("GSLIDE_HEADED") == "1"
        self._pw: Playwright | None = None
        self._context: BrowserContext | None = None

    def __enter__(self) -> BrowserContext:
        self._user_data_dir.mkdir(parents=True, exist_ok=True)

        args = [
            "--disable-blink-features=AutomationControlled",
            f"--window-size={self._WIDTH},{self._HEIGHT}",
        ]
        profile = resolve_profile_directory(self._user_data_dir)
        if profile:
            args.append(f"--profile-directory={profile}")
        if not self._headed:
            # New headless mode renders like real Chrome (legacy headless is
            # detected by Google). Launch non-headless and let this arg drive it.
            args.append("--headless=new")

        self._pw = sync_playwright().start()
        try:
            # launch_persistent_context returns the BrowserContext directly
            # (no separate Browser object — context.browser is None).
            # An explicit viewport is required: at the default size the
            # right-sidebar "Help me visualize" icon is off-canvas and unclickable.
            self._context = self._pw.chromium.launch_persistent_context(
                str(self._user_data_dir),
                headless=False,
                viewport={"width": self._WIDTH, "height": self._HEIGHT},
                args=args,
            )
        except Exception as e:
            self._pw.stop()
            if "ProcessSingleton" in str(e) or "SingletonLock" in str(e):
                raise ProfileLockedError(
                    "Profile in use — close other gslide runs and try again."
                ) from e
            raise
        return self._context

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        if self._context:
            self._context.close()
        if self._pw:
            self._pw.stop()
