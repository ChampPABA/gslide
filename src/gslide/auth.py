"""Authentication session management — file I/O and browser operations."""

import json
import sys
from pathlib import Path
from typing import Any

import click

SLIDES_URL = "https://docs.google.com/presentation/"


def get_storage_path() -> Path:
    return Path.home() / ".gslide" / "storage_state.json"


def is_logged_in() -> bool:
    return get_storage_path().exists()


def save_storage_state(data: dict[str, Any]) -> None:
    path = get_storage_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2))


def delete_storage_state() -> None:
    get_storage_path().unlink(missing_ok=True)


def login() -> None:
    """Launch headed browser for Google login, save storage state on success."""
    from gslide.browser import BrowserSession, save_session

    click.echo("Opening browser for Google login...")
    click.echo("")
    click.echo("Instructions:")
    click.echo("1. Complete the Google login in the browser window")
    click.echo("2. Wait until you see Google Slides homepage")
    click.echo("3. Press ENTER here to save and close")
    click.echo("")

    with BrowserSession(headed=True) as context:
        page = context.new_page()
        page.goto(SLIDES_URL)

        try:
            input("[Press ENTER when logged in] ")
        except (KeyboardInterrupt, EOFError):
            click.echo("\nAborted.", err=True)
            sys.exit(1)

        save_session(context, get_storage_path())
        click.echo("Session saved.")


def status() -> None:
    """Check if saved session is still valid."""
    path = get_storage_path()

    if not path.exists():
        click.echo("Not logged in. Run: gslide auth login")
        sys.exit(1)

    from gslide.browser import BrowserSession

    with BrowserSession(headed=False, storage_state=path) as context:
        page = context.new_page()
        page.goto(SLIDES_URL, wait_until="domcontentloaded")
        # Google Slides never reaches networkidle — wait for redirect or UI instead
        page.wait_for_timeout(5000)

        if "accounts.google.com" in page.url:
            click.echo("Session expired. Run: gslide auth login")
            sys.exit(1)

        click.echo("Session valid.")


def logout() -> None:
    """Delete saved session."""
    if not is_logged_in():
        click.echo("Not logged in.")
        return

    delete_storage_state()
    click.echo("Logged out.")
