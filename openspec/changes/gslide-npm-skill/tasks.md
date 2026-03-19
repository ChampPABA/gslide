## 1. npm Package Setup

- [x] 1.1 Create `package.json` with name `@champpaba/gslide`, bin entry `bin/gslide.mjs`, postinstall script, files array
- [x] 1.2 Create `bin/gslide.mjs` — Node script that finds Python venv and spawns `gslide` CLI with forwarded args
- [x] 1.3 Create `scripts/postinstall.sh` — auto-setup: check/install uv → check/install Python → create venv → pip install → playwright install chromium with progress output
- [x] 1.4 Test: `npm pack` creates valid tarball
- [x] 1.5 Test: `npm install -g .` installs locally and `gslide --help` works

## 2. Self-Update Command

- [x] 2.1 Add `gslide update` CLI command in `src/gslide/cli.py`
- [x] 2.2 Implement update logic: check npm registry for latest version, compare with current, run `npm update -g @champpaba/gslide`
- [x] 2.3 Write test for update command (mock subprocess)

## 3. Claude Code Skill

- [x] 3.1 Create `skills/gslide/SKILL.md` with frontmatter (name, description with trigger keywords)
- [x] 3.2 Write CLI command reference section with all commands and usage examples
- [x] 3.3 Write workflow section (pre-check → auth → plan slides → generate)
- [x] 3.4 Write pre-check section (verify gslide installed, verify auth)

## 4. Installer Script

- [x] 4.1 Create `skills.sh` — installs npm package + copies skill to `~/.claude/skills/gslide/SKILL.md`
- [x] 4.2 Test: `bash skills.sh` installs CLI and skill file exists

## 5. CI/CD

- [x] 5.1 Create `.github/workflows/release.yml` — trigger on `v*` tag push
- [x] 5.2 Add npm publish step with `NODE_AUTH_TOKEN` secret
- [x] 5.3 Add version sync step: extract version from tag, update package.json + pyproject.toml
- [x] 5.4 Create `.npmrc` with scope registry config

## 6. Integration Test

- [x] 6.1 Test full flow: `npm install -g .` → `gslide --help` → `gslide auth login` → `gslide update`
- [x] 6.2 Verify skill file loads correctly in Claude Code
