"""Tests for Click CLI entry point."""

import json
import subprocess
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest
from click.testing import CliRunner

from gslide.cli import cli


@pytest.fixture
def runner() -> CliRunner:
    return CliRunner()


class TestHelpOutput:
    def test_main_help_shows_auth_and_gen(self, runner: CliRunner) -> None:
        result = runner.invoke(cli, ["--help"])

        assert result.exit_code == 0
        assert "auth" in result.output
        assert "gen" in result.output

    def test_auth_help_shows_login_status_logout(self, runner: CliRunner) -> None:
        result = runner.invoke(cli, ["auth", "--help"])

        assert result.exit_code == 0
        assert "login" in result.output
        assert "status" in result.output
        assert "logout" in result.output

    def test_gen_help_shows_all_subcommands(self, runner: CliRunner) -> None:
        result = runner.invoke(cli, ["gen", "--help"])

        assert result.exit_code == 0
        for cmd in ("slide", "infographic", "image", "batch"):
            assert cmd in result.output


class TestGenArgValidation:
    def test_infographic_without_presentation_exits_error(self, runner: CliRunner) -> None:
        result = runner.invoke(cli, ["gen", "infographic", "--prompt", "test"])

        assert result.exit_code != 0
        assert "presentation" in result.output.lower()

    def test_batch_nonexistent_file_exits_error(self, runner: CliRunner) -> None:
        result = runner.invoke(cli, ["gen", "batch", "--file", "nonexistent.json"])

        assert result.exit_code != 0

    def test_batch_dry_run_prints_summary(self, runner: CliRunner, tmp_path: Path) -> None:
        prompts = {
            "presentation_id": "abc123",
            "slides": [
                {"tab": "infographic", "prompt": "Q4 revenue"},
                {"tab": "slide", "prompt": "Team overview"},
            ],
        }
        prompts_file = tmp_path / "prompts.json"
        prompts_file.write_text(json.dumps(prompts))

        result = runner.invoke(cli, ["gen", "batch", "--file", str(prompts_file), "--dry-run"])

        assert result.exit_code == 0
        assert "abc123" in result.output
        assert "Slides: 2" in result.output
        assert "infographic" in result.output
        assert "slide" in result.output


class TestLogoutCommand:
    def test_logout_when_logged_in(self, runner: CliRunner, tmp_path: Path) -> None:
        state_file = tmp_path / "storage_state.json"
        state_file.write_text("{}")

        with patch("gslide.auth.get_storage_path", return_value=state_file):
            result = runner.invoke(cli, ["auth", "logout"])

        assert result.exit_code == 0
        assert "Logged out" in result.output
        assert not state_file.exists()

    def test_logout_when_not_logged_in(self, runner: CliRunner, tmp_path: Path) -> None:
        state_file = tmp_path / "nonexistent.json"

        with patch("gslide.auth.get_storage_path", return_value=state_file):
            result = runner.invoke(cli, ["auth", "logout"])

        assert result.exit_code == 0
        assert "Not logged in" in result.output


class TestUpdateCommand:
    def test_update_shows_current_version(self, runner: CliRunner) -> None:
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(returncode=0, stdout="0.2.0\n")
            result = runner.invoke(cli, ["update"])

        assert "Current:" in result.output
        assert "Updating..." in result.output

    def test_update_runs_npm_install(self, runner: CliRunner) -> None:
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(returncode=0, stdout="0.2.0\n")
            result = runner.invoke(cli, ["update"])

        assert result.exit_code == 0
        # First call should be npm install -g @champpaba/gslide@latest
        first_call_args = mock_run.call_args_list[0][0][0]
        assert "install" in first_call_args
        assert "@champpaba/gslide@latest" in first_call_args

    def test_update_fails_gracefully(self, runner: CliRunner) -> None:
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(returncode=1)
            result = runner.invoke(cli, ["update"])

        assert result.exit_code != 0
        assert "failed" in result.output.lower()
