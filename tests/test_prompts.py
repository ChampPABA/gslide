"""Tests for prompts.json loading and validation."""

import json
import pytest
from pathlib import Path

from gslide.prompts import load_prompts, ValidationError


def write_prompts(tmp_path: Path, data: dict) -> Path:
    """Helper to write a prompts.json file for testing."""
    path = tmp_path / "prompts.json"
    path.write_text(json.dumps(data))
    return path


class TestLoadValidPrompts:
    def test_valid_prompts_loads_correctly(self, tmp_path: Path) -> None:
        data = {
            "presentation_id": "abc123",
            "slides": [
                {"tab": "infographic", "prompt": "Show Q4 revenue"},
                {"tab": "slide", "prompt": "Team overview"},
            ],
        }
        path = write_prompts(tmp_path, data)

        result = load_prompts(path)

        assert result.presentation_id == "abc123"
        assert len(result.slides) == 2
        assert result.slides[0].tab == "infographic"
        assert result.slides[0].prompt == "Show Q4 revenue"
        assert result.slides[1].tab == "slide"


class TestPromptValidationErrors:
    def test_invalid_tab_raises_error(self, tmp_path: Path) -> None:
        data = {
            "presentation_id": "abc123",
            "slides": [{"tab": "invalid_tab", "prompt": "test"}],
        }
        path = write_prompts(tmp_path, data)

        with pytest.raises(ValidationError, match="invalid tab 'invalid_tab'"):
            load_prompts(path)

    def test_missing_presentation_id_raises_error(self, tmp_path: Path) -> None:
        data = {"slides": [{"tab": "slide", "prompt": "test"}]}
        path = write_prompts(tmp_path, data)

        with pytest.raises(ValidationError, match="presentation_id"):
            load_prompts(path)

    def test_missing_slides_raises_error(self, tmp_path: Path) -> None:
        data = {"presentation_id": "abc123"}
        path = write_prompts(tmp_path, data)

        with pytest.raises(ValidationError, match="slides"):
            load_prompts(path)

    def test_slide_missing_tab_raises_error(self, tmp_path: Path) -> None:
        data = {
            "presentation_id": "abc123",
            "slides": [{"prompt": "test"}],
        }
        path = write_prompts(tmp_path, data)

        with pytest.raises(ValidationError, match="missing required field: tab"):
            load_prompts(path)

    def test_slide_missing_prompt_raises_error(self, tmp_path: Path) -> None:
        data = {
            "presentation_id": "abc123",
            "slides": [{"tab": "slide"}],
        }
        path = write_prompts(tmp_path, data)

        with pytest.raises(ValidationError, match="missing required field: prompt"):
            load_prompts(path)


class TestImageValidation:
    def test_valid_images_load_correctly(self, tmp_path: Path) -> None:
        data = {
            "presentation_id": "abc123",
            "slides": [{"tab": "slide", "prompt": "test"}],
            "images": [
                {"target_slide": 2, "prompt": "logo", "insert_as": "image"},
                {"target_slide": 3, "prompt": "bg", "insert_as": "background"},
            ],
        }
        path = write_prompts(tmp_path, data)

        result = load_prompts(path)

        assert len(result.images) == 2
        assert result.images[0].target_slide == 2
        assert result.images[0].insert_as == "image"
        assert result.images[1].insert_as == "background"

    def test_image_defaults_insert_as_to_image(self, tmp_path: Path) -> None:
        data = {
            "presentation_id": "abc123",
            "slides": [{"tab": "slide", "prompt": "test"}],
            "images": [{"target_slide": 1, "prompt": "logo"}],
        }
        path = write_prompts(tmp_path, data)

        result = load_prompts(path)

        assert result.images[0].insert_as == "image"

    def test_image_missing_target_slide_raises_error(self, tmp_path: Path) -> None:
        data = {
            "presentation_id": "abc123",
            "slides": [{"tab": "slide", "prompt": "test"}],
            "images": [{"prompt": "logo"}],
        }
        path = write_prompts(tmp_path, data)

        with pytest.raises(ValidationError, match="target_slide"):
            load_prompts(path)

    def test_image_invalid_insert_as_raises_error(self, tmp_path: Path) -> None:
        data = {
            "presentation_id": "abc123",
            "slides": [{"tab": "slide", "prompt": "test"}],
            "images": [{"target_slide": 1, "prompt": "logo", "insert_as": "overlay"}],
        }
        path = write_prompts(tmp_path, data)

        with pytest.raises(ValidationError, match="invalid insert_as"):
            load_prompts(path)


class TestEmptySlides:
    def test_empty_slides_array_raises_error(self, tmp_path: Path) -> None:
        data = {"presentation_id": "abc123", "slides": []}
        path = write_prompts(tmp_path, data)

        with pytest.raises(ValidationError, match="non-empty"):
            load_prompts(path)
