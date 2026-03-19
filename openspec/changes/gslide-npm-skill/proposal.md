## Why

gslide CLI ใช้งานได้แล้วแต่ยังติดตั้งยาก (ต้อง clone repo, สร้าง venv, pip install เอง) และ Claude ยังไม่รู้จัก gslide — ต้องสอนทุกครั้ง ต้องทำให้ติดตั้งง่ายด้วย `npm install -g @champpaba/gslide` และสร้าง Claude Code skill ให้ trigger อัตโนมัติเมื่อ user อยากทำ slide

## What Changes

- New npm package `@champpaba/gslide` wrapping Python CLI with auto-setup (uv + Python + Playwright Chromium)
- New `gslide update` CLI command for self-update
- New Claude Code skill (`skills/gslide.md`) teaching Claude how to use gslide CLI
- New `skills.sh` installer script that installs CLI + copies skill in one step
- New GitHub Actions CI/CD workflow for auto-publish to npm on version tag

## Capabilities

### New Capabilities
- `npm-package`: npm wrapper package with bin entry, postinstall script (uv/Python/Chromium auto-setup), and self-update command
- `claude-skill`: Claude Code skill file with CLI commands, trigger conditions, workflow guidance, and pre-check for installation
- `cicd`: GitHub Actions workflow for automated npm publish on tag push, version bumping in package.json + pyproject.toml

### Modified Capabilities

(none)

## Impact

- **New dependencies**: npm (for distribution), uv (bundled for Python management)
- **New files**: `package.json`, `bin/gslide.mjs`, `scripts/postinstall.sh`, `skills/gslide.md`, `skills.sh`, `.github/workflows/release.yml`
- **External systems**: npmjs.com (@ChampPABA scope), GitHub Actions
- **Works with**: Existing `src/gslide/` Python package (unchanged), Claude Code skill system
