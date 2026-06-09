"""Integration tests for browser module — requires Playwright Chromium."""

from pathlib import Path

import pytest

from gslide.browser import BrowserSession


class TestBrowserSession:
    def test_launch_headless_and_navigate(self, tmp_path: Path) -> None:
        profile = tmp_path / "profile"
        with BrowserSession(profile) as context:
            page = context.new_page()
            page.goto("https://example.com")
            assert "Example Domain" in page.title()

    def test_profile_dir_created_and_persisted(self, tmp_path: Path) -> None:
        profile = tmp_path / "profile"
        with BrowserSession(profile) as context:
            context.new_page().goto("https://example.com")
        # Persistent context writes profile data to disk on close
        assert profile.exists()
