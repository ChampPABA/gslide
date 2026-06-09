"""Tests for auth module — persistent profile session management."""

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from gslide.auth import get_profile_dir, is_logged_in, delete_profile, require_login, login


class TestGetProfileDir:
    def test_returns_path_under_home_gslide(self) -> None:
        path = get_profile_dir()

        assert path.name == "profile"
        assert path.parent.name == ".gslide"
        assert path.parent.parent == Path.home()


class TestIsLoggedIn:
    def test_returns_true_when_profile_exists(self, tmp_path: Path, monkeypatch) -> None:
        profile = tmp_path / ".gslide" / "profile"
        profile.mkdir(parents=True)
        monkeypatch.setattr("gslide.auth.get_profile_dir", lambda: profile)

        assert is_logged_in() is True

    def test_returns_false_when_profile_missing(self, tmp_path: Path, monkeypatch) -> None:
        profile = tmp_path / ".gslide" / "profile"
        monkeypatch.setattr("gslide.auth.get_profile_dir", lambda: profile)

        assert is_logged_in() is False


class TestDeleteProfile:
    def test_removes_existing_profile(self, tmp_path: Path, monkeypatch) -> None:
        profile = tmp_path / "profile"
        profile.mkdir()
        (profile / "Cookies").write_text("x")
        monkeypatch.setattr("gslide.auth.get_profile_dir", lambda: profile)

        delete_profile()

        assert not profile.exists()

    def test_no_error_when_profile_missing(self, tmp_path: Path, monkeypatch) -> None:
        profile = tmp_path / "profile"
        monkeypatch.setattr("gslide.auth.get_profile_dir", lambda: profile)

        delete_profile()  # should not raise


class TestRequireLogin:
    def test_returns_dir_when_profile_exists(self, tmp_path: Path, monkeypatch) -> None:
        profile = tmp_path / ".gslide" / "profile"
        profile.mkdir(parents=True)
        monkeypatch.setattr("gslide.auth.get_profile_dir", lambda: profile)

        result = require_login()

        assert result == profile

    def test_exits_when_profile_missing(self, tmp_path: Path, monkeypatch) -> None:
        profile = tmp_path / ".gslide" / "profile"
        monkeypatch.setattr("gslide.auth.get_profile_dir", lambda: profile)

        with pytest.raises(SystemExit) as exc_info:
            require_login()

        assert exc_info.value.code == 1


class TestLoginAbortCleanup:
    def test_aborted_login_removes_freshly_created_profile(
        self, tmp_path: Path, monkeypatch
    ) -> None:
        profile = tmp_path / ".gslide" / "profile"
        monkeypatch.setattr("gslide.auth.get_profile_dir", lambda: profile)

        # BrowserSession is a context manager; its __enter__ creates the profile dir
        # (mimics launch_persistent_context) and returns a context whose new_page works.
        def fake_enter(self):
            profile.mkdir(parents=True, exist_ok=True)
            return MagicMock()

        with patch("gslide.browser.BrowserSession.__enter__", fake_enter), \
             patch("gslide.browser.BrowserSession.__exit__", lambda *a: None), \
             patch("builtins.input", side_effect=KeyboardInterrupt):
            with pytest.raises(SystemExit) as exc_info:
                login()

        assert exc_info.value.code == 1
        assert not profile.exists()  # freshly-created profile cleaned up on abort
