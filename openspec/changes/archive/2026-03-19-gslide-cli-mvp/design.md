## Context

gslide is a greenfield Python CLI that automates Google Slides' "Help me visualize" feature via browser automation. POC completed Mar 16-17, 2026 validated the approach. The tool works alongside `gws` CLI (Google Workspace CLI) which handles REST API operations.

Current state:
- `gws` CLI installed and authenticated
- `agent-browser` v0.9.0 available (but gslide will use Playwright directly, not agent-browser)
- POC code in `/tmp/gslides_api_test.py` (reference only)
- `~/.notebooklm/storage_state.json` exists as pattern reference

## Goals / Non-Goals

**Goals:**
- CLI that generates slides via "Help me visualize" with all 3 tabs (Slide, Infographic, Image)
- Batch generation from `prompts.json` with progress reporting
- Reliable session management (login once, reuse cookies)
- TDD approach: tests written before implementation, small-to-big increments
- Works as a standalone CLI and as a tool callable from Claude skill

**Non-Goals:**
- Craft Mode (Claude as creative director + Slides REST API) — future change
- Google Slides REST API wrapper — `gws` handles this
- Prompt engineering/templates — Claude generates prompts dynamically
- Style presets — user/Claude provides full style in prompt each time
- GUI or web interface

## Decisions

### 1. Playwright Python (direct) over agent-browser subprocess

Use `playwright` Python package directly instead of shelling out to `agent-browser`.

**Why:** gen batch requires loop + error handling + state tracking across 30-50s generation cycles. Shell subprocess parsing is fragile. Playwright gives native async/await, try/except, timeouts, and screenshot debugging.

**Alternative considered:** Shell wrapping agent-browser — rejected due to poor error handling and inability to manage state between steps.

### 2. Click for CLI framework

Use `click` over `argparse` for CLI.

**Why:** Click provides better UX (help text, error messages, parameter validation), is well-tested, and is the standard for Python CLIs. Minimal dependency.

### 3. Storage state file for auth persistence

Save Playwright browser context storage state (cookies + localStorage) to `~/.gslide/storage_state.json`.

**Why:** Same pattern as notebooklm-py. Playwright's `context.storage_state()` serializes all cookies including httpOnly. `context.add_cookies()` or `browser.new_context(storage_state=path)` restores them.

### 4. Unified insert strategy (click preview → insert)

All three tabs use the same insert flow discovered during live testing (Mar 19, 2026):
- Click the generated preview image to open the insert overlay
- Click "Insert on new slide" button
- **Image tab** has fallback options: "Insert as image" or "Insert as background"

**Why:** Live testing revealed that all tabs share the same UX pattern — clicking the preview image opens a fullscreen overlay with the "Insert on new slide" button. The original POC incorrectly assumed tab-specific flows (dropdown menus, etc.).

### 5. Selectors by text/aria-label, not element refs

Use `page.get_by_text()`, `page.get_by_role()`, `page.locator('[aria-label*="..."]')` instead of hard-coded element refs.

**Why:** Element refs (e.g., ref=e50) change every session. Text and aria-labels are stable across sessions.

### 6. Project structure: src layout with pyproject.toml

```
gslide/
├── pyproject.toml
├── tests/
│   ├── test_prompts.py        ← TDD: pure logic, no browser
│   ├── test_auth.py           ← TDD: file operations, config
│   ├── test_cli.py            ← TDD: click CLI integration
│   └── test_gen.py            ← integration: needs browser (mock)
├── src/
│   └── gslide/
│       ├── __init__.py
│       ├── cli.py             ← click CLI entry point
│       ├── auth.py            ← login, status, logout
│       ├── browser.py         ← Playwright browser lifecycle
│       ├── gen.py             ← gen logic per tab + batch
│       └── prompts.py         ← prompts.json load + validate
```

### 7. TDD strategy: pure logic first, browser later

| Module | TDD? | Why |
|--------|------|-----|
| `prompts.py` | Yes — pure logic | JSON validation, style merging, field checking — no side effects |
| `auth.py` | Yes — file I/O only | Storage state file CRUD, path management — mockable filesystem |
| `cli.py` | Yes — click testing | Click's CliRunner for invocation testing — no browser needed |
| `browser.py` | No — integration | Browser lifecycle management — test via real browser in integration |
| `gen.py` | Partial — mock Playwright | Core logic testable with mocked page objects; full flow needs integration test |

## Risks / Trade-offs

**[Google UI changes] → Mitigation**: Selectors based on text/aria-label are more stable than refs, but Google can still change button text or panel layout. Keep selectors in constants for easy updates. Add screenshot-on-failure for debugging.

**[Generation timeout variability] → Mitigation**: Default 120s timeout with `--timeout` flag override. Poll for result appearance rather than fixed sleep.

**[Session expiry mid-batch] → Mitigation**: Check auth before starting batch. If session expires during batch (redirect to login), abort with clear error showing progress so user can resume.

**[Blank first page edge case] → Mitigation**: POC saw this but official docs don't confirm. Add optional cleanup step in batch. Verify during implementation.

**[Headless detection] → Mitigation**: Google blocks headless for login (requires headed). Post-login headless works. Use `--headed` flag for login command only.
