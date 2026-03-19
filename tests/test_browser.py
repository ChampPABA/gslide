"""Integration tests for browser module — requires Playwright Chromium."""

import pytest

from gslide.browser import BrowserSession


class TestBrowserSession:
    def test_launch_headless_and_navigate(self) -> None:
        with BrowserSession(headed=False) as context:
            page = context.new_page()
            page.goto("https://example.com")
            assert "Example Domain" in page.title()
