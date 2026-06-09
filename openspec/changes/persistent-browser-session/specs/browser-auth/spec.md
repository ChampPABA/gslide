## MODIFIED Requirements

### Requirement: Headed browser login flow
The system SHALL launch a headed (visible) Chromium browser using a persistent user-data directory, navigate to Google Slides, and wait for the user to manually complete Google login. After the user presses ENTER, the system SHALL close the browser; the Chromium profile persists the session automatically (no manual cookie extraction).

#### Scenario: First-time login
- **WHEN** user runs `gslide auth login`
- **THEN** system launches headed browser with persistent profile at `~/.gslide/profile`, navigating to `https://docs.google.com/presentation/`
- **THEN** system prints instructions and waits for the user to press ENTER
- **THEN** on ENTER, system closes the browser and the session is persisted in the profile directory
- **THEN** system prints confirmation

#### Scenario: Migration from legacy storage state
- **WHEN** user runs `gslide auth login` and a legacy `~/.gslide/storage_state.json` exists
- **THEN** system prints a one-time notice that re-login is required for the new persistent-profile format
- **THEN** system proceeds with the persistent-profile login flow

#### Scenario: User aborts with Ctrl+C
- **WHEN** user presses Ctrl+C during login
- **THEN** system closes browser and exits cleanly

### Requirement: Session persistence via persistent profile
The system SHALL persist the browser session as a Chromium persistent user-data directory at `~/.gslide/profile`, launched via Playwright `launch_persistent_context`. Chromium natively persists and rotates Google session cookies (including `__Secure-1PSIDTS`) across runs. The launch SHALL include the argument `--disable-blink-features=AutomationControlled` to reduce automation detection.

#### Scenario: Profile directory created on login
- **WHEN** login completes successfully
- **THEN** `~/.gslide/profile` exists and contains a Chromium profile (cookies, local storage)

#### Scenario: Session reused across runs without re-login
- **WHEN** a command runs after a prior successful login, in a new process
- **THEN** system reuses the persistent profile and does not require re-login while the Google session remains valid

#### Scenario: Headed override via environment
- **WHEN** `GSLIDE_HEADED=1` is set for any command
- **THEN** the browser launches headed (visible) regardless of the command default

#### Scenario: Profile in use by another process
- **WHEN** another gslide process holds the profile lock
- **THEN** system prints a clear error indicating the profile is in use and exits non-zero (no confusing crash)

### Requirement: Session status check
The system SHALL verify if the saved session is still valid by launching the persistent profile in a headless browser and checking if Google Slides loads without redirecting to login.

#### Scenario: Valid session
- **WHEN** user runs `gslide auth status` and the profile holds a valid session
- **THEN** system prints "Session valid" and exits with code 0

#### Scenario: Expired session
- **WHEN** user runs `gslide auth status` and the session redirects to `accounts.google.com`
- **THEN** system prints "Session expired. Run: gslide auth login" and exits with code 1

#### Scenario: No profile
- **WHEN** user runs `gslide auth status` and `~/.gslide/profile` does not exist
- **THEN** system prints "Not logged in. Run: gslide auth login" and exits with code 1

### Requirement: Logout
The system SHALL delete the persistent profile directory when the user logs out.

#### Scenario: Logout with existing session
- **WHEN** user runs `gslide auth logout`
- **THEN** system deletes `~/.gslide/profile`
- **THEN** system prints "Logged out"

#### Scenario: Logout without session
- **WHEN** user runs `gslide auth logout` and no profile exists
- **THEN** system prints "Not logged in" and exits normally
