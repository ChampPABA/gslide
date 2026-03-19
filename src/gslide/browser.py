"""Playwright browser lifecycle management."""

from pathlib import Path
from typing import Any

from playwright.sync_api import sync_playwright, BrowserContext, Playwright


class BrowserSession:
    """Manages a Playwright browser context with optional storage state."""

    def __init__(self, headed: bool = False, storage_state: Path | None = None) -> None:
        self._headed = headed
        self._storage_state = storage_state
        self._pw: Playwright | None = None
        self._context: BrowserContext | None = None

    def __enter__(self) -> BrowserContext:
        self._pw = sync_playwright().start()
        browser = self._pw.chromium.launch(headless=not self._headed)

        context_opts: dict[str, Any] = {}
        if self._storage_state and self._storage_state.exists():
            context_opts["storage_state"] = str(self._storage_state)

        self._context = browser.new_context(**context_opts)
        return self._context

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        if self._context:
            self._context.close()
            self._context.browser.close()
        if self._pw:
            self._pw.stop()
        return None


def save_session(context: BrowserContext, path: Path) -> None:
    """Export browser context storage state to a file."""
    path.parent.mkdir(parents=True, exist_ok=True)
    context.storage_state(path=str(path))
