"""Tests for gen module — mocked Playwright page for call sequence verification."""

from pathlib import Path
from unittest.mock import MagicMock, patch, PropertyMock

import pytest

from gslide.gen import (
    navigate_to_presentation,
    check_url,
    fill_and_create,
    GenerationError,
)


def _make_locator_mock(count: int = 0, visible: bool = False, enabled: bool = False):
    """Create a mock locator that returns proper int for count()."""
    loc = MagicMock()
    loc.count.return_value = count
    loc.first.is_visible.return_value = visible
    loc.first.is_enabled.return_value = enabled
    return loc


def _make_page_mock(url: str = "https://docs.google.com/presentation/d/abc123/edit"):
    """Create a page mock with properly configured locator responses."""
    page = MagicMock()
    page.url = url

    # By default, get_by_text and get_by_role return locators with count=0
    page.get_by_text.return_value = _make_locator_mock(count=0)

    # Make get_by_role return enabled Insert button (generation "completes" immediately)
    def get_by_role_side_effect(role, *, name="", exact=False):
        if name == "Create":
            return _make_locator_mock(count=1, visible=True, enabled=True)
        if name in ("Insert as new slide", "Insert", "Replace"):
            return _make_locator_mock(count=1, visible=True, enabled=True)
        if name in ("tab",):
            return MagicMock()
        return _make_locator_mock(count=0)

    page.get_by_role.side_effect = get_by_role_side_effect

    # Make get_by_text return "Insert on new slide" button for insert flow
    def get_by_text_side_effect(text, exact=False):
        if "Insert on new slide" in str(text):
            return _make_locator_mock(count=1, visible=True, enabled=True)
        return _make_locator_mock(count=0)

    page.get_by_text.side_effect = get_by_text_side_effect

    # Make locator return proper mocks for textarea and preview image
    def locator_side_effect(selector):
        if selector == "textarea":
            ta_list = MagicMock()
            ta_list.count.return_value = 1
            visible_ta = MagicMock()
            visible_ta.is_visible.return_value = True
            ta_list.nth.return_value = visible_ta
            return ta_list
        if "googleusercontent.com" in selector:
            # Generated preview image — visible, large
            img_list = MagicMock()
            img_list.count.return_value = 1
            img_mock = MagicMock()
            img_mock.is_visible.return_value = True
            img_mock.bounding_box.return_value = {"x": 900, "y": 200, "width": 280, "height": 156}
            img_list.nth.return_value = img_mock
            return img_list
        loc = MagicMock()
        loc.count.return_value = 0
        return loc

    page.locator.side_effect = locator_side_effect

    return page


class TestNavigateToPresentation:
    def test_raises_on_auth_redirect(self) -> None:
        page = _make_page_mock(url="https://accounts.google.com/signin")

        with pytest.raises(GenerationError, match="Session expired"):
            navigate_to_presentation(page, "abc123")

    def test_raises_on_wrong_presentation(self) -> None:
        page = _make_page_mock(url="https://docs.google.com/presentation/d/OTHER/edit")

        with pytest.raises(GenerationError, match="Cannot access"):
            navigate_to_presentation(page, "abc123")


class TestCheckUrl:
    def test_passes_when_url_matches(self) -> None:
        page = _make_page_mock()
        check_url(page, "abc123")  # should not raise

    def test_raises_on_url_drift(self) -> None:
        page = _make_page_mock(url="https://docs.google.com/presentation/d/OTHER/edit")

        with pytest.raises(GenerationError, match="navigated away"):
            check_url(page, "abc123")


class TestFillAndCreate:
    def test_completes_when_insert_button_appears(self) -> None:
        page = _make_page_mock()
        # The default mock already has Insert button appearing
        fill_and_create(page, "test prompt", timeout_ms=10_000)
        # No exception = success

    def test_raises_on_generation_error_message(self) -> None:
        page = _make_page_mock()

        # Make error text visible, no preview image
        def get_by_text_side_effect(text, exact=False):
            if isinstance(text, str) and "didn't quite get that" in text.lower():
                return _make_locator_mock(count=1, visible=True)
            return _make_locator_mock(count=0)

        page.get_by_text.side_effect = get_by_text_side_effect

        # No preview image appears
        def locator_no_preview(selector):
            if selector == "textarea":
                ta_list = MagicMock()
                ta_list.count.return_value = 1
                visible_ta = MagicMock()
                visible_ta.is_visible.return_value = True
                ta_list.nth.return_value = visible_ta
                return ta_list
            loc = MagicMock()
            loc.count.return_value = 0
            return loc

        page.locator.side_effect = locator_no_preview

        with pytest.raises(GenerationError, match="prompt too vague"):
            fill_and_create(page, "bad prompt", timeout_ms=10_000)


class TestGenSingle:
    @patch("gslide.gen.BrowserSession")
    def test_gen_single_calls_goto_with_presentation_id(
        self, mock_browser_cls: MagicMock, tmp_path: Path
    ) -> None:
        mock_context = MagicMock()
        mock_page = _make_page_mock()
        mock_context.new_page.return_value = mock_page
        mock_browser_cls.return_value.__enter__ = MagicMock(return_value=mock_context)
        mock_browser_cls.return_value.__exit__ = MagicMock(return_value=None)

        storage = tmp_path / ".gslide" / "storage_state.json"
        storage.parent.mkdir(parents=True)
        storage.write_text("{}")

        with patch("gslide.gen.require_login", return_value=storage):
            from gslide.gen import gen_single
            gen_single("abc123", "infographic", "Show Q4 revenue")

        mock_page.goto.assert_called_once()
        assert "abc123" in mock_page.goto.call_args[0][0]


class TestGenBatch:
    @patch("gslide.gen.BrowserSession")
    def test_batch_processes_all_slides(
        self, mock_browser_cls: MagicMock, tmp_path: Path
    ) -> None:
        from gslide.gen import gen_batch
        from gslide.prompts import PromptsData, SlidePrompt

        mock_context = MagicMock()
        mock_page = _make_page_mock()
        mock_context.new_page.return_value = mock_page
        mock_browser_cls.return_value.__enter__ = MagicMock(return_value=mock_context)
        mock_browser_cls.return_value.__exit__ = MagicMock(return_value=None)

        storage = tmp_path / ".gslide" / "storage_state.json"
        storage.parent.mkdir(parents=True)
        storage.write_text("{}")

        prompts_data = PromptsData(
            presentation_id="abc123",
            slides=[
                SlidePrompt(tab="infographic", prompt="Revenue chart"),
                SlidePrompt(tab="slide", prompt="Team overview"),
            ],
        )

        with patch("gslide.gen.require_login", return_value=storage):
            gen_batch(prompts_data)

        mock_page.goto.assert_called_once()

    @patch("gslide.gen.BrowserSession")
    @patch("gslide.gen.fill_and_create", side_effect=[Exception("gen failed"), None])
    @patch("gslide.gen._insert_on_new_slide")
    def test_batch_continue_on_error_does_not_abort(
        self,
        mock_insert_on_new_slide: MagicMock,
        mock_fill: MagicMock,
        mock_browser_cls: MagicMock,
        tmp_path: Path,
    ) -> None:
        from gslide.gen import gen_batch
        from gslide.prompts import PromptsData, SlidePrompt

        mock_context = MagicMock()
        mock_page = _make_page_mock()
        mock_context.new_page.return_value = mock_page
        mock_browser_cls.return_value.__enter__ = MagicMock(return_value=mock_context)
        mock_browser_cls.return_value.__exit__ = MagicMock(return_value=None)

        storage = tmp_path / ".gslide" / "storage_state.json"
        storage.parent.mkdir(parents=True)
        storage.write_text("{}")

        prompts_data = PromptsData(
            presentation_id="abc123",
            slides=[
                SlidePrompt(tab="infographic", prompt="Fail"),
                SlidePrompt(tab="slide", prompt="Should run"),
            ],
        )

        with patch("gslide.gen.require_login", return_value=storage):
            gen_batch(prompts_data, continue_on_error=True)

        # Both fill_and_create calls were attempted
        assert mock_fill.call_count == 2
        # Second slide's insert was called (first failed before insert)
        mock_insert_on_new_slide.assert_called_once()
