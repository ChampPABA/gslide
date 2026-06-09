"""Authentication session management — persistent Chromium profile."""

import shutil
import sys
from pathlib import Path

import click

SLIDES_URL = "https://docs.google.com/presentation/"


def get_profile_dir() -> Path:
    return Path.home() / ".gslide" / "profile"


def _legacy_storage_state() -> Path:
    return Path.home() / ".gslide" / "storage_state.json"


def is_logged_in() -> bool:
    return get_profile_dir().exists()


def require_login() -> Path:
    """Return profile dir or exit if not logged in."""
    profile_dir = get_profile_dir()
    if not profile_dir.exists():
        click.echo("Not logged in. Run: gslide auth login", err=True)
        sys.exit(1)
    return profile_dir


def delete_profile() -> None:
    shutil.rmtree(get_profile_dir(), ignore_errors=True)


def login() -> None:
    """Launch headed browser for Google login; the persistent profile saves the session."""
    from gslide.browser import BrowserSession

    if _legacy_storage_state().exists():
        click.echo(
            "Note: gslide now uses a persistent browser profile. "
            "A one-time re-login is required (your old session file is no longer used)."
        )
        click.echo("")

    click.echo("Opening browser for Google login...")
    click.echo("")
    click.echo("Instructions:")
    click.echo("1. Complete the Google login in the browser window")
    click.echo("2. Wait until you see Google Slides homepage")
    click.echo("3. Press ENTER here to save and close")
    click.echo("")

    profile_existed = get_profile_dir().exists()

    with BrowserSession(get_profile_dir(), headed=True) as context:
        page = context.new_page()
        page.goto(SLIDES_URL)

        try:
            input("[Press ENTER when logged in] ")
        except (KeyboardInterrupt, EOFError):
            click.echo("\nAborted.", err=True)
            # The launch freshly created the profile dir; remove it so a
            # cancelled login doesn't masquerade as a logged-in session.
            if not profile_existed:
                delete_profile()
            sys.exit(1)

    click.echo("Session saved.")


def status() -> None:
    """Check if the saved session is still valid."""
    profile_dir = require_login()

    from gslide.browser import BrowserSession

    with BrowserSession(profile_dir, headed=False) as context:
        page = context.new_page()
        page.goto(SLIDES_URL, wait_until="domcontentloaded")
        # Google Slides never reaches networkidle — wait for redirect or UI instead
        page.wait_for_timeout(5000)

        if "accounts.google.com" in page.url:
            click.echo("Session expired. Run: gslide auth login")
            sys.exit(1)

        click.echo("Session valid.")


def logout() -> None:
    """Delete the persistent profile."""
    if not is_logged_in():
        click.echo("Not logged in.")
        return

    delete_profile()
    click.echo("Logged out.")
