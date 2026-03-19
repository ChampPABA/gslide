## ADDED Requirements

### Requirement: npm package structure
The system SHALL provide an npm package `@champpaba/gslide` with a bin entry that delegates to the Python CLI.

#### Scenario: package.json configured correctly
- **WHEN** user inspects package.json
- **THEN** name is `@champpaba/gslide`
- **THEN** bin entry points to `bin/gslide.mjs`
- **THEN** postinstall script points to `scripts/postinstall.sh`
- **THEN** files array includes `bin/`, `scripts/`, `src/`, `pyproject.toml`

#### Scenario: Global install via npm
- **WHEN** user runs `npm install -g @champpaba/gslide`
- **THEN** `gslide` command becomes available in PATH
- **THEN** postinstall runs automatically

### Requirement: Bin script delegates to Python CLI
The system SHALL provide a Node.js bin script that spawns the Python gslide CLI with all arguments forwarded.

#### Scenario: Command forwarding
- **WHEN** user runs `gslide auth login`
- **THEN** bin script spawns Python CLI with args `["auth", "login"]`
- **THEN** exit code from Python process is forwarded to caller

#### Scenario: Python not available
- **WHEN** bin script cannot find Python or gslide package
- **THEN** system prints error with install instructions

### Requirement: Postinstall auto-setup
The system SHALL automatically install uv, Python, and Playwright Chromium during npm postinstall.

#### Scenario: Fresh install on clean system
- **WHEN** postinstall runs and uv is not installed
- **THEN** system downloads uv binary from astral.sh
- **THEN** system uses uv to install Python 3.10+ if not present
- **THEN** system creates venv and installs gslide Python package
- **THEN** system runs `playwright install chromium`
- **THEN** system prints progress for each step

#### Scenario: System already has Python and uv
- **WHEN** postinstall runs and uv + Python already exist
- **THEN** system skips download steps
- **THEN** system only installs gslide package and Playwright if missing

### Requirement: Self-update command
The system SHALL provide a `gslide update` CLI command.

#### Scenario: Update available
- **WHEN** user runs `gslide update` and a newer version exists on npm
- **THEN** system shows current and latest version
- **THEN** system runs `npm update -g @champpaba/gslide`
- **THEN** system confirms update success

#### Scenario: Already up to date
- **WHEN** user runs `gslide update` and current version is latest
- **THEN** system prints "Already up to date (vX.Y.Z)"
