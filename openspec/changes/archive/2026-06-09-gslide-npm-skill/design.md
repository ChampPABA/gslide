## Context

gslide Python CLI is complete and validated (48 tasks, 32 tests, 5-slide batch generation proven). Now needs packaging for easy distribution and a Claude Code skill for AI-assisted usage. Reference implementation: `notebooklm-py` (pipx/uv install, Playwright Chromium auto-setup).

Current state:
- Python package at `src/gslide/` with `pyproject.toml` (setuptools)
- CLI entry point: `gslide = "gslide.cli:cli"`
- Playwright Chromium required for browser automation
- User's npm scope: `@ChampPABA`

## Goals / Non-Goals

**Goals:**
- One-command install: `npm install -g @champpaba/gslide`
- Zero prerequisites: auto-setup uv, Python, Playwright Chromium
- `gslide update` for self-update
- Claude Code skill that triggers on slide-related requests
- CI/CD auto-publish on git tag

**Non-Goals:**
- Prompt engineering/best practices in the skill (separate concern)
- PyPI distribution (npm-only for now)
- Cross-platform testing (Linux/WSL focus)

## Decisions

### 1. npm wrapper around Python CLI

Use an npm package with a Node.js bin script that delegates to the Python CLI.

**Why:** User wants `npx` workflow. npm is the standard for CLI distribution in the user's ecosystem. The bin script is a thin shim — all logic stays in Python.

**Alternative considered:** PyPI + pipx — rejected because user explicitly chose npx.

### 2. Bundle uv for Python management

The postinstall script downloads `uv` if not present, then uses uv to install Python and the gslide package.

**Why:** Zero prerequisites for the user. uv can install Python itself (~30MB, 5 seconds), is fast (10-100x faster than pip), and is the modern standard. No need to assume Python is pre-installed.

**Install chain:** npm postinstall → check/install uv → check/install Python 3.10+ → create venv → pip install gslide → playwright install chromium

### 3. Postinstall with progress feedback

Show step-by-step progress during postinstall so user knows what's happening during the ~2 minute first install.

**Why:** Chromium download is ~150MB — user needs to know it's working, not hung.

### 4. gslide update via npm

`gslide update` command runs `npm update -g @champpaba/gslide` internally.

**Why:** Simple, uses npm's existing update mechanism. Shows current vs latest version.

### 5. Skill as standalone SKILL.md (no scripts/references)

The Claude Code skill is a single `SKILL.md` file with CLI commands and workflow guidance. No bundled scripts needed — gslide CLI does all the work.

**Why:** gslide is a tool, not a brain. The skill just teaches Claude which commands to use and when.

### 6. skills.sh as single installer

One script that installs both the npm package and copies the skill file.

**Why:** User runs one command and everything is ready — CLI installed, Claude knows how to use it.

### 7. GitHub Actions CI/CD on tag push

Push `v*` tag → GitHub Actions → bump version → npm publish.

**Why:** Standard CI/CD pattern. Version in package.json and pyproject.toml stay in sync.

## Risks / Trade-offs

**[uv availability] → Mitigation**: postinstall downloads uv binary directly from astral.sh. Falls back to pip if uv fails.

**[Chromium download size] → Mitigation**: Show progress. Only downloads once — cached for subsequent installs.

**[npm + Python mismatch] → Mitigation**: postinstall validates Python version and Playwright installation before declaring success.

**[skill triggering accuracy] → Mitigation**: Use skill-creator's description optimization loop to tune trigger phrases after initial deployment.
