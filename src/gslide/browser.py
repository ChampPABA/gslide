"""Playwright browser lifecycle management."""

import os
from pathlib import Path

from playwright.sync_api import BrowserContext, Playwright, sync_playwright


class ProfileLockedError(Exception):
    """Raised when the persistent profile is already in use by another process."""


class BrowserSession:
    """Manages a persistent Chromium browser context backed by a user-data directory.

    The persistent profile lets Chromium natively persist and rotate Google
    session cookies across runs — no manual storage-state save/load.
    """

    def __init__(self, user_data_dir: Path, headed: bool = False) -> None:
        self._user_data_dir = user_data_dir
        self._headed = headed or os.environ.get("GSLIDE_HEADED") == "1"
        self._pw: Playwright | None = None
        self._context: BrowserContext | None = None

    def __enter__(self) -> BrowserContext:
        self._user_data_dir.mkdir(parents=True, exist_ok=True)
        self._pw = sync_playwright().start()
        try:
            # launch_persistent_context returns the BrowserContext directly
            # (no separate Browser object — context.browser is None).
            self._context = self._pw.chromium.launch_persistent_context(
                str(self._user_data_dir),
                headless=not self._headed,
                args=["--disable-blink-features=AutomationControlled"],
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
