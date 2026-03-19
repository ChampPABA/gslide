## 1. Project Setup

- [x] 1.1 Create `pyproject.toml` with dependencies (playwright, click, pytest) and `[project.scripts]` entry for `gslide` CLI
- [x] 1.2 Create `src/gslide/__init__.py` and package structure
- [x] 1.3 Install dependencies: `pip install -e ".[dev]"` and `playwright install chromium`
- [x] 1.4 Verify `gslide --help` runs (empty CLI skeleton)

## 2. Prompts Module (TDD — pure logic, no browser)

- [x] 2.1 Write `tests/test_prompts.py` — test: valid prompts.json loads correctly (fields: presentation_id, slides[].tab, slides[].prompt)
- [x] 2.2 Write `tests/test_prompts.py` — test: invalid tab value raises validation error
- [x] 2.3 Write `tests/test_prompts.py` — test: missing required fields raises validation error
- [x] 2.4 Write `tests/test_prompts.py` — test: images[] validation (target_slide, prompt, insert_as)
- [x] 2.5 Write `tests/test_prompts.py` — test: empty slides array raises validation error
- [x] 2.6 Implement `src/gslide/prompts.py` — make all tests pass

## 3. Auth Module (TDD — file I/O, mockable)

- [x] 3.1 Write `tests/test_auth.py` — test: `get_storage_path()` returns `~/.gslide/storage_state.json`
- [x] 3.2 Write `tests/test_auth.py` — test: `is_logged_in()` returns True when file exists, False when missing
- [x] 3.3 Write `tests/test_auth.py` — test: `save_storage_state(data)` creates directory and writes JSON
- [x] 3.4 Write `tests/test_auth.py` — test: `delete_storage_state()` removes file, no error if missing
- [x] 3.5 Implement `src/gslide/auth.py` — make all tests pass (file operations only, no browser)

## 4. CLI Module (TDD — Click CliRunner)

- [x] 4.1 Write `tests/test_cli.py` — test: `gslide --help` shows auth and gen groups
- [x] 4.2 Write `tests/test_cli.py` — test: `gslide auth --help` shows login, status, logout
- [x] 4.3 Write `tests/test_cli.py` — test: `gslide gen --help` shows slide, infographic, image, batch
- [x] 4.4 Write `tests/test_cli.py` — test: `gslide gen infographic` without --presentation exits with error
- [x] 4.5 Write `tests/test_cli.py` — test: `gslide gen batch --file nonexistent.json` exits with error
- [x] 4.6 Write `tests/test_cli.py` — test: `gslide gen batch --file valid.json --dry-run` prints summary without launching browser
- [x] 4.7 Implement `src/gslide/cli.py` — make all tests pass (wire commands to auth/gen modules)

## 5. Browser Module (integration — Playwright lifecycle)

- [x] 5.1 Implement `src/gslide/browser.py` — `launch_browser(headed=False, storage_state=None)` returns browser context
- [x] 5.2 Implement `src/gslide/browser.py` — `save_session(context, path)` exports storage state to file
- [x] 5.3 Write integration test: launch headless browser, navigate to google.com, close — verify no crash

## 6. Auth Browser Integration

- [x] 6.1 Implement `auth.login()` — launch headed browser, navigate to Google Slides, wait for login, save storage state
- [x] 6.2 Implement `auth.status()` — load storage state, launch headless, check if Google Slides loads without redirect
- [x] 6.3 Implement `auth.logout()` — delete storage state file (already done in step 3)
- [x] 6.4 Wire auth CLI commands to auth module functions

## 7. Gen Module — Single Generation (core logic)

- [x] 7.1 Implement `gen.navigate_to_presentation(page, presentation_id)` — load URL, wait for UI, check auth
- [x] 7.2 Implement `gen.open_panel(page)` — press End, click "Help me visualize", wait for panel
- [x] 7.3 Implement `gen.select_tab(page, tab_name)` — click Slide/Infographic/Image tab
- [x] 7.4 Implement `gen.fill_and_create(page, prompt, timeout)` — clear input, type prompt, click Create, wait for result
- [x] 7.5 Implement `gen.insert_infographic(page)` — click "Insert as new slide"
- [x] 7.6 Implement `gen.insert_slide(page)` — click dropdown → "Insert"
- [x] 7.7 Implement `gen.insert_image(page, insert_as)` — click preview, dropdown → "Insert as image/background"
- [x] 7.8 Implement `gen.check_url(page, presentation_id)` — URL safety check
- [x] 7.9 Implement `gen.gen_single(presentation_id, tab, prompt, **opts)` — compose above functions into single gen flow
- [x] 7.10 Write `tests/test_gen.py` — test gen_single with mocked page (verify function call sequence)

## 8. Gen Batch Module

- [x] 8.1 Implement `gen.gen_batch(prompts_data, **opts)` — loop through slides[], manage panel state, print progress
- [x] 8.2 Implement batch image phase — process images[] after slides, navigate to target slides
- [x] 8.3 Implement `--continue-on-error` — try/except per slide, collect errors, print summary
- [x] 8.4 Write `tests/test_gen.py` — test batch with mocked page (verify loop, progress, error collection)

## 9. End-to-End Integration Test

- [x] 9.1 Manual test: `gslide auth login` — verify headed browser opens, login works, storage state saved
- [x] 9.2 Manual test: `gslide auth status` — verify session check works
- [x] 9.3 Manual test: `gslide gen infographic --presentation ID --prompt "test"` — verify single gen works
- [x] 9.4 Manual test: `gslide gen batch --file prompts.json` — verify batch with 2-3 slides
- [x] 9.5 Manual test: verify generated slides appear in Google Slides presentation
<!-- All validated. Insert flow: click preview image → "Insert on new slide" button -->
