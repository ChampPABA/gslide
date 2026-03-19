"""Tests for auth module — file I/O operations for session management."""

import json
from pathlib import Path

from gslide.auth import get_storage_path, is_logged_in, save_storage_state, delete_storage_state


class TestGetStoragePath:
    def test_returns_path_under_home_gslide(self) -> None:
        path = get_storage_path()

        assert path.name == "storage_state.json"
        assert path.parent.name == ".gslide"
        assert path.parent.parent == Path.home()


class TestIsLoggedIn:
    def test_returns_true_when_file_exists(self, tmp_path: Path, monkeypatch) -> None:
        state_file = tmp_path / ".gslide" / "storage_state.json"
        state_file.parent.mkdir()
        state_file.write_text("{}")
        monkeypatch.setattr("gslide.auth.get_storage_path", lambda: state_file)

        assert is_logged_in() is True

    def test_returns_false_when_file_missing(self, tmp_path: Path, monkeypatch) -> None:
        state_file = tmp_path / ".gslide" / "storage_state.json"
        monkeypatch.setattr("gslide.auth.get_storage_path", lambda: state_file)

        assert is_logged_in() is False


class TestSaveStorageState:
    def test_creates_directory_and_writes_json(self, tmp_path: Path, monkeypatch) -> None:
        state_file = tmp_path / ".gslide" / "storage_state.json"
        monkeypatch.setattr("gslide.auth.get_storage_path", lambda: state_file)

        save_storage_state({"cookies": [{"name": "SID", "value": "abc"}]})

        assert state_file.exists()
        data = json.loads(state_file.read_text())
        assert data["cookies"][0]["name"] == "SID"


class TestDeleteStorageState:
    def test_removes_existing_file(self, tmp_path: Path, monkeypatch) -> None:
        state_file = tmp_path / "storage_state.json"
        state_file.write_text("{}")
        monkeypatch.setattr("gslide.auth.get_storage_path", lambda: state_file)

        delete_storage_state()

        assert not state_file.exists()

    def test_no_error_when_file_missing(self, tmp_path: Path, monkeypatch) -> None:
        state_file = tmp_path / "storage_state.json"
        monkeypatch.setattr("gslide.auth.get_storage_path", lambda: state_file)

        delete_storage_state()  # should not raise
