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


class TestUpdateCommand:
    def test_update_shows_current_version(self, runner: CliRunner) -> None:
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(stdout="0.1.0\n", returncode=0)
            result = runner.invoke(cli, ["update"])

        assert "v0.1.0" in result.output

    def test_update_already_up_to_date(self, runner: CliRunner) -> None:
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(stdout="0.1.0\n", returncode=0)
            result = runner.invoke(cli, ["update"])

        assert result.exit_code == 0
        assert "Already up to date" in result.output

    def test_update_triggers_npm_update(self, runner: CliRunner) -> None:
        call_count = [0]

        def side_effect(*args, **kwargs):
            call_count[0] += 1
            if call_count[0] == 1:
                return MagicMock(stdout="0.2.0\n", returncode=0)
            return MagicMock(returncode=0)

        with patch("subprocess.run", side_effect=side_effect):
            result = runner.invoke(cli, ["update"])

        assert "v0.2.0" in result.output
        assert "Updated" in result.output
