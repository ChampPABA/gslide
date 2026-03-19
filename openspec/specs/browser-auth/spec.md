## Purpose

Manages Google account authentication via a headed browser login flow, persisting session cookies as a Playwright storage state file for use by other commands.

## Requirements

### Requirement: Headed browser login flow
The system SHALL launch a headed (visible) Chromium browser, navigate to Google Slides, and wait for the user to manually complete Google login. After the user presses ENTER, the system SHALL extract all cookies (including httpOnly) and save them as a Playwright storage state file.

#### Scenario: First-time login
- **WHEN** user runs `gslide auth login`
- **THEN** system launches headed browser navigating to `https://docs.google.com/presentation/`
- **THEN** system prints instructions and waits for the user to press ENTER
- **THEN** system saves storage state to `~/.gslide/storage_state.json`
- **THEN** system prints confirmation with authenticated email if detectable

#### Scenario: User aborts with Ctrl+C
- **WHEN** user presses Ctrl+C during login
- **THEN** system closes browser and exits cleanly without saving storage state

### Requirement: Session persistence via storage state
The system SHALL persist browser session as a Playwright storage state JSON file at `~/.gslide/storage_state.json`. This file contains cookies for `.google.com`, `docs.google.com`, and `accounts.google.com` domains.

#### Scenario: Storage state file created
- **WHEN** login completes successfully
- **THEN** `~/.gslide/storage_state.json` exists and contains valid JSON with cookies array

#### Scenario: Storage state directory auto-created
- **WHEN** `~/.gslide/` directory does not exist
- **THEN** system creates the directory before saving storage state

### Requirement: Session status check
The system SHALL verify if a saved session is still valid by loading storage state into a headless browser and checking if Google Slides loads without redirecting to login.

#### Scenario: Valid session
- **WHEN** user runs `gslide auth status` and storage state exists with valid cookies
- **THEN** system prints "Session valid" and exits with code 0

#### Scenario: Expired session
- **WHEN** user runs `gslide auth status` and cookies have expired
- **THEN** system prints "Session expired. Run: gslide auth login" and exits with code 1

#### Scenario: No session file
- **WHEN** user runs `gslide auth status` and `~/.gslide/storage_state.json` does not exist
- **THEN** system prints "Not logged in. Run: gslide auth login" and exits with code 1

### Requirement: Logout
The system SHALL delete the storage state file when user logs out.

#### Scenario: Logout with existing session
- **WHEN** user runs `gslide auth logout`
- **THEN** system deletes `~/.gslide/storage_state.json`
- **THEN** system prints "Logged out"

#### Scenario: Logout without session
- **WHEN** user runs `gslide auth logout` and no storage state file exists
- **THEN** system prints "Not logged in" and exits normally
