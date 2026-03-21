"""Load and validate prompts.json files for batch generation."""

import json
from dataclasses import dataclass, field
import sys

if sys.version_info >= (3, 11):
    from enum import StrEnum
else:
    from enum import Enum

    class StrEnum(str, Enum):
        """Backport for Python < 3.11."""

from pathlib import Path


class ValidationError(Exception):
    """Raised when prompts.json validation fails."""


class Tab(StrEnum):
    SLIDE = "slide"
    INFOGRAPHIC = "infographic"
    IMAGE = "image"


VALID_TABS = frozenset(Tab)


@dataclass(frozen=True)
class SlidePrompt:
    tab: str
    prompt: str


@dataclass(frozen=True)
class ImagePrompt:
    target_slide: int
    prompt: str
    insert_as: str = "image"


@dataclass(frozen=True)
class PromptsData:
    presentation_id: str
    slides: list[SlidePrompt]
    images: list[ImagePrompt] = field(default_factory=list)


def _is_storytelling_format(raw: dict) -> bool:
    """Detect storytelling.json format by checking for presentation.topic and slides[].prompt."""
    return (
        "presentation" in raw
        and isinstance(raw["presentation"], dict)
        and "topic" in raw["presentation"]
        and "slides" in raw
    )


def _convert_storytelling(raw: dict) -> dict:
    """Convert storytelling.json format to prompts format."""
    presentation = raw["presentation"]
    presentation_id = presentation.get("presentation_id", "")

    if not presentation_id:
        raise ValidationError(
            "storytelling.json missing presentation.presentation_id — "
            "add it before running batch generation"
        )

    slides = []
    for s in raw["slides"]:
        if "prompt" not in s or "tab" not in s:
            continue
        slides.append({"tab": s["tab"], "prompt": s["prompt"]})

    return {
        "presentation_id": presentation_id,
        "slides": slides,
    }


def load_prompts(path: Path) -> PromptsData:
    raw = json.loads(path.read_text())

    if not isinstance(raw, dict):
        raise ValidationError("Prompts file must be a JSON object")

    # Auto-detect storytelling.json format and convert
    if _is_storytelling_format(raw):
        raw = _convert_storytelling(raw)

    if "presentation_id" not in raw:
        raise ValidationError("Missing required field: presentation_id")

    if "slides" not in raw:
        raise ValidationError("Missing required field: slides")

    slides_raw = raw["slides"]
    if not isinstance(slides_raw, list) or len(slides_raw) == 0:
        raise ValidationError("slides must be a non-empty array")

    slides: list[SlidePrompt] = []
    for i, s in enumerate(slides_raw):
        if "tab" not in s:
            raise ValidationError(f"slides[{i}]: missing required field: tab")
        if "prompt" not in s:
            raise ValidationError(f"slides[{i}]: missing required field: prompt")
        if s["tab"] not in VALID_TABS:
            raise ValidationError(
                f"slides[{i}]: invalid tab '{s['tab']}', must be one of: {', '.join(sorted(VALID_TABS))}"
            )
        slides.append(SlidePrompt(tab=s["tab"], prompt=s["prompt"]))

    images: list[ImagePrompt] = []
    for i, img in enumerate(raw.get("images", [])):
        if "target_slide" not in img:
            raise ValidationError(f"images[{i}]: missing required field: target_slide")
        if "prompt" not in img:
            raise ValidationError(f"images[{i}]: missing required field: prompt")
        insert_as = img.get("insert_as", "image")
        if insert_as not in ("image", "background"):
            raise ValidationError(
                f"images[{i}]: invalid insert_as '{insert_as}', must be 'image' or 'background'"
            )
        images.append(ImagePrompt(
            target_slide=img["target_slide"],
            prompt=img["prompt"],
            insert_as=insert_as,
        ))

    return PromptsData(
        presentation_id=raw["presentation_id"],
        slides=slides,
        images=images,
    )
