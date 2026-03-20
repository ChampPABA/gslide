"""Generation logic — browser automation for 'Help me visualize' feature.

Selector discoveries (validated Mar 20, 2026):
- Panel opener: div[aria-label="Help me visualize"] (right sidebar icon)
- Tabs: role="tab" with name="Slide"/"Image"/"Infographic" (must filter :visible)
- Text input: visible textarea (use keyboard.type, not fill; iterate to skip hidden)
- Submit: get_by_role("button", name="Create", exact=True)
- Filmstrip: [aria-label*="filmstrip"] (partial match — label varies: "Hide filmstrip" etc.)
- Generation takes 30-60s, shows "Creating..." tooltip
- Insert button text varies: "Insert as new slide" / "Insert on new slide" (Google A/B tests)
- After insert, stale preview persists in panel — must track stale srcs to click correct preview
"""

import sys
import time

import click
from playwright.sync_api import Page, TimeoutError as PwTimeout

from gslide.auth import require_login
from gslide.browser import BrowserSession
from gslide.prompts import PromptsData, Tab

PRESENTATION_URL = "https://docs.google.com/presentation/d/{id}/edit"
DEFAULT_TIMEOUT_MS = 120_000  # 120s — generation can take 30-60s
PANEL_LOAD_TIMEOUT_MS = 10_000
SLIDES_LOAD_TIMEOUT_MS = 60_000


class GenerationError(Exception):
    """Raised when slide generation fails."""


# --- Navigation & Panel ---


def navigate_to_presentation(page: Page, presentation_id: str) -> None:
    """Load presentation, wait for UI, check auth."""
    url = PRESENTATION_URL.format(id=presentation_id)
    page.goto(url, wait_until="domcontentloaded")

    # Google Slides is heavy — give it time, check for auth redirect
    page.wait_for_timeout(5000)

    if "accounts.google.com" in page.url:
        raise GenerationError("Session expired. Run: gslide auth login")

    if presentation_id not in page.url:
        raise GenerationError("Cannot access presentation")

    # Wait for filmstrip sidebar to confirm Slides UI loaded
    try:
        page.wait_for_selector(
            '[aria-label*="filmstrip"]', timeout=SLIDES_LOAD_TIMEOUT_MS
        )
    except PwTimeout as e:
        raise GenerationError("Google Slides UI did not load in time") from e


def _is_panel_open(page: Page) -> bool:
    """Check if the HMV panel is currently open (visible tabs)."""
    tabs = page.locator('[role="tab"]:visible')
    for i in range(tabs.count()):
        text = tabs.nth(i).text_content() or ""
        if text.strip() in ("Slide", "Image", "Infographic"):
            return True
    return False


def open_panel(page: Page) -> None:
    """Open 'Help me visualize' panel. Toggle-aware: skip click if already open."""
    if _is_panel_open(page):
        return

    hmv = page.locator('div[aria-label="Help me visualize"]')
    hmv.click()

    # Wait for HMV panel tabs (Slide/Image/Infographic) — must be visible
    page.wait_for_selector('[role="tab"]:visible', timeout=PANEL_LOAD_TIMEOUT_MS)


def _reopen_panel(page: Page, retries: int = 2) -> None:
    """Reopen the HMV panel after insert overlay is dismissed."""
    for attempt in range(retries + 1):
        try:
            # If panel is already open, done
            if _is_panel_open(page):
                return
            # Click HMV icon to open
            hmv = page.locator('div[aria-label="Help me visualize"]')
            hmv.click()
            page.wait_for_selector('[role="tab"]:visible', timeout=PANEL_LOAD_TIMEOUT_MS)
            return
        except (PwTimeout, Exception):
            if attempt < retries:
                page.wait_for_timeout(1000)
                continue
            raise GenerationError("Failed to reopen HMV panel after insert")


def select_tab(page: Page, tab_name: str) -> None:
    """Click the tab (Slide/Infographic/Image) in the panel."""
    tab = page.get_by_role("tab", name=tab_name)
    tab.click()
    page.wait_for_timeout(300)


def _find_visible_textarea(page: Page) -> object:
    all_ta = page.locator("textarea")
    for i in range(all_ta.count()):
        ta = all_ta.nth(i)
        if ta.is_visible():
            return ta
    raise GenerationError("No visible text input found in panel")


def _snapshot_preview_srcs(page: Page) -> set[str]:
    """Capture current preview image src URLs to detect stale previews."""
    srcs: set[str] = set()
    preview = page.locator('img[src*="googleusercontent.com"]')
    for i in range(preview.count()):
        try:
            src = preview.nth(i).get_attribute("src") or ""
            if src:
                srcs.add(src)
        except Exception:
            continue
    return srcs


def fill_and_create(
    page: Page, prompt: str, timeout_ms: int = DEFAULT_TIMEOUT_MS
) -> set[str]:
    """Type prompt, click Create, wait for NEW preview image to appear.

    Returns the stale_srcs set so callers can pass it to _click_preview_image
    to ensure only the NEW preview is clicked (not stale ones from prior generations).
    """
    # Snapshot existing preview URLs BEFORE creating — used to detect stale images
    stale_srcs = _snapshot_preview_srcs(page)

    textarea = _find_visible_textarea(page)
    textarea.click()
    page.wait_for_timeout(200)

    textarea.fill("")
    page.keyboard.type(prompt, delay=10)
    page.wait_for_timeout(500)

    create_btn = page.get_by_role("button", name="Create", exact=True)
    if not create_btn.is_enabled():
        raise GenerationError("Create button is disabled — prompt may be too short")
    create_btn.click()

    # Poll for: NEW preview image appears OR error text
    viewport = page.viewport_size or {"width": 1280}
    panel_x = viewport["width"] * 0.6

    start = time.monotonic()
    while (time.monotonic() - start) * 1000 < timeout_ms:
        page.wait_for_timeout(5000)

        # Check for error
        error_text = page.get_by_text("We didn't quite get that", exact=False)
        if error_text.count() > 0 and error_text.first.is_visible():
            raise GenerationError(
                "Generation failed: prompt too vague — try a more detailed prompt"
            )

        # Check for NEW preview image in HMV panel (not in stale_srcs)
        preview = page.locator('img[src*="googleusercontent.com"]')
        for i in range(preview.count()):
            try:
                img = preview.nth(i)
                if img.is_visible():
                    bb = img.bounding_box()
                    src = img.get_attribute("src") or ""
                    if bb and bb["width"] > 100 and bb["x"] > panel_x and src not in stale_srcs:
                        return stale_srcs  # NEW preview appeared — generation complete
            except Exception:
                continue

    raise GenerationError(f"Generation timed out after {timeout_ms // 1000}s")


# --- Tab-specific insert logic ---


def _click_preview_image(page: Page, stale_srcs: set[str] | None = None) -> None:
    """Click the NEW preview image in the HMV panel, skipping stale previews."""
    viewport = page.viewport_size or {"width": 1280}
    panel_x_threshold = viewport["width"] * 0.6
    stale = stale_srcs or set()

    preview = page.locator('img[src*="googleusercontent.com"]')
    for i in range(preview.count()):
        try:
            img = preview.nth(i)
            if img.is_visible():
                bb = img.bounding_box()
                src = img.get_attribute("src") or ""
                # Must be: in panel area, not stale, reasonable size
                if bb and bb["width"] > 100 and bb["x"] > panel_x_threshold and src not in stale:
                    page.mouse.click(
                        bb["x"] + bb["width"] / 2,
                        bb["y"] + bb["height"] / 2,
                    )
                    page.wait_for_timeout(2000)
                    return
        except Exception:
            continue
    raise GenerationError("Generated preview image not found")


def _click_insert_button(page: Page, text: str) -> None:
    """Click an insert button by text, with fallbacks for Google's changing UI."""
    # Try 1: text match with both "on"/"as" variants
    variants = [text]
    if "as new slide" in text:
        variants.append(text.replace("as new slide", "on new slide"))
    elif "on new slide" in text:
        variants.append(text.replace("on new slide", "as new slide"))

    for variant in variants:
        btn = page.get_by_text(variant)
        if btn.count() > 0 and btn.first.is_visible():
            btn.first.click()
            return

    # Try 2: class selector + dispatchEvent (bypasses visibility check)
    cls_btn = page.locator(".unifiedPreviewBubbleRightSectionInsertButtonWithMenu")
    if cls_btn.count() > 0:
        cls_btn.first.dispatch_event("click")
        return

    # Try 3: role=button containing "Insert" + dispatchEvent
    role_btn = page.get_by_role("button", name="Insert")
    for i in range(role_btn.count()):
        btn_text = role_btn.nth(i).text_content() or ""
        if "new slide" in btn_text.lower():
            role_btn.nth(i).dispatch_event("click")
            return

    raise GenerationError(f"'{text}' button not found after clicking preview")


def _wait_for_slide_insert(page: Page, previous_count: int, timeout_ms: int = 10000) -> None:
    """Poll filmstrip until slide count increases or timeout."""
    start = time.monotonic()
    while (time.monotonic() - start) * 1000 < timeout_ms:
        items = page.locator('[aria-label*="filmstrip"] [role="listitem"]')
        if items.count() > previous_count:
            return
        page.wait_for_timeout(500)


def _insert_on_new_slide(page: Page, stale_srcs: set[str] | None = None) -> None:
    """Click NEW preview then insert as new slide."""
    filmstrip_items = page.locator('[aria-label*="filmstrip"] [role="listitem"]')
    previous_count = filmstrip_items.count()
    _click_preview_image(page, stale_srcs=stale_srcs)
    _click_insert_button(page, "Insert as new slide")
    _wait_for_slide_insert(page, previous_count)


def insert_image(page: Page, insert_as: str = "image", stale_srcs: set[str] | None = None) -> None:
    """Click NEW preview then insert as image or background."""
    filmstrip_items = page.locator('[aria-label*="filmstrip"] [role="listitem"]')
    previous_count = filmstrip_items.count()
    _click_preview_image(page, stale_srcs=stale_srcs)

    option_text = "Insert as background" if insert_as == "background" else "Insert as image"

    try:
        _click_insert_button(page, option_text)
    except GenerationError:
        # Fallback: try "Insert as new slide"
        _click_insert_button(page, "Insert as new slide")

    _wait_for_slide_insert(page, previous_count)


def check_url(page: Page, presentation_id: str) -> None:
    if presentation_id not in page.url:
        raise GenerationError("Browser navigated away from target presentation")


# --- Orchestration ---


def gen_single(
    presentation_id: str,
    tab: str,
    prompt: str,
    *,
    timeout: int = 120,
    slide_index: int | None = None,
    insert_as: str = "image",
) -> None:
    """Generate a single slide/infographic/image via browser automation."""
    storage_path = require_login()
    timeout_ms = timeout * 1000

    with BrowserSession(storage_state=storage_path) as context:
        page = context.new_page()

        try:
            navigate_to_presentation(page, presentation_id)

            if tab == Tab.IMAGE and slide_index is not None:
                _navigate_to_slide(page, slide_index)
            else:
                open_panel(page)

            select_tab(page, tab.capitalize())
            stale_srcs = fill_and_create(page, prompt, timeout_ms=timeout_ms)
            check_url(page, presentation_id)

            if tab == Tab.IMAGE:
                insert_image(page, insert_as=insert_as, stale_srcs=stale_srcs)
            else:
                _insert_on_new_slide(page, stale_srcs=stale_srcs)

            check_url(page, presentation_id)
            click.echo(f"Done: {tab} generated successfully.")

        except GenerationError as e:
            click.echo(f"Error: {e}", err=True)
            try:
                page.screenshot(path="/tmp/gslide_error.png")
                click.echo("Debug screenshot saved to /tmp/gslide_error.png")
            except Exception:
                pass
            sys.exit(2)


def _navigate_to_slide(page: Page, slide_index: int) -> None:
    """Navigate to a specific slide by index and open panel."""
    slides = page.locator('[aria-label*="filmstrip"] [role="listitem"]')
    if slide_index <= slides.count():
        slides.nth(slide_index - 1).click()
        page.wait_for_timeout(500)

    open_panel(page)


# --- Batch ---


def gen_batch(
    prompts_data: PromptsData,
    *,
    continue_on_error: bool = False,
    timeout: int = 120,
) -> None:
    """Generate all slides from prompts data in a single browser session."""
    storage_path = require_login()
    timeout_ms = timeout * 1000
    total_slides = len(prompts_data.slides)
    total_images = len(prompts_data.images)
    errors: list[tuple[int, str, str]] = []
    start_time = time.monotonic()

    with BrowserSession(storage_state=storage_path) as context:
        page = context.new_page()

        try:
            navigate_to_presentation(page, prompts_data.presentation_id)
            open_panel(page)
        except GenerationError as e:
            click.echo(f"Error: {e}", err=True)
            sys.exit(2)

        current_tab: str | None = None

        # Phase 1: Generate slides
        for i, slide in enumerate(prompts_data.slides, 1):
            label = f"[{i}/{total_slides}]"
            click.echo(f"  {label} {slide.tab}: {slide.prompt[:50]}...")

            try:
                check_url(page, prompts_data.presentation_id)

                if slide.tab != current_tab:
                    select_tab(page, slide.tab.capitalize())
                    current_tab = slide.tab

                t0 = time.monotonic()
                stale_srcs = fill_and_create(page, slide.prompt, timeout_ms=timeout_ms)

                if slide.tab == Tab.IMAGE:
                    insert_image(page, stale_srcs=stale_srcs)
                else:
                    _insert_on_new_slide(page, stale_srcs=stale_srcs)

                elapsed = time.monotonic() - t0
                click.echo(f"  {label} done ({elapsed:.1f}s)")

                # Return to last slide and reopen panel for next generation
                page.keyboard.press("End")
                page.wait_for_timeout(500)

                # Dismiss any lingering overlay, then reopen HMV panel
                page.keyboard.press("Escape")
                page.wait_for_timeout(500)
                _reopen_panel(page)

            except Exception as e:
                errors.append((i, slide.tab, str(e)))
                click.echo(f"  {label} FAILED: {e}")
                if not continue_on_error:
                    break

        # Phase 2: Generate images
        for i, img in enumerate(prompts_data.images, 1):
            label = f"[img {i}/{total_images}]"
            click.echo(f"  {label} slide {img.target_slide}: {img.prompt[:50]}...")

            try:
                check_url(page, prompts_data.presentation_id)
                _navigate_to_slide(page, img.target_slide)

                if current_tab != Tab.IMAGE:
                    select_tab(page, "Image")
                    current_tab = Tab.IMAGE

                t0 = time.monotonic()
                stale_srcs = fill_and_create(page, img.prompt, timeout_ms=timeout_ms)
                insert_image(page, insert_as=img.insert_as, stale_srcs=stale_srcs)

                elapsed = time.monotonic() - t0
                click.echo(f"  {label} done ({elapsed:.1f}s)")

            except Exception as e:
                errors.append((total_slides + i, "image", str(e)))
                click.echo(f"  {label} FAILED: {e}")
                if not continue_on_error:
                    break

    # Summary
    total_elapsed = time.monotonic() - start_time
    total_ops = total_slides + total_images
    succeeded = total_ops - len(errors)

    click.echo()
    click.echo(f"Batch complete: {succeeded}/{total_ops} succeeded in {total_elapsed:.1f}s")
    if errors:
        click.echo(f"Failed ({len(errors)}):")
        for idx, tab, err in errors:
            click.echo(f"  #{idx} ({tab}): {err}")
    click.echo(
        f"Presentation: {PRESENTATION_URL.format(id=prompts_data.presentation_id)}"
    )
