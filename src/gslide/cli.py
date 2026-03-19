"""Click CLI entry point for gslide."""

import sys
from pathlib import Path

import click


@click.group()
def cli() -> None:
    """gslide — Automate Google Slides 'Help me visualize' feature."""


@cli.command()
def update() -> None:
    """Check for updates and self-update via npm."""
    import subprocess

    from gslide import __version__

    click.echo(f"Current version: v{__version__}")
    click.echo("Checking for updates...")

    try:
        result = subprocess.run(
            ["npm", "view", "@champpaba/gslide", "version"],
            capture_output=True,
            text=True,
            timeout=15,
        )
        latest = result.stdout.strip()
    except (subprocess.TimeoutExpired, FileNotFoundError):
        click.echo("Could not check npm registry.", err=True)
        sys.exit(1)

    if not latest:
        click.echo("Could not determine latest version.", err=True)
        sys.exit(1)

    if latest == __version__:
        click.echo(f"Already up to date (v{__version__}).")
        return

    click.echo(f"Latest version: v{latest}")
    click.echo("Updating...")

    proc = subprocess.run(
        ["npm", "update", "-g", "@champpaba/gslide"],
        timeout=120,
    )
    if proc.returncode == 0:
        click.echo(f"Updated to v{latest}.")
    else:
        click.echo("Update failed.", err=True)
        sys.exit(1)


# --- Auth commands ---


@cli.group()
def auth() -> None:
    """Manage Google authentication session."""


@auth.command()
def login() -> None:
    """Launch browser for Google login."""
    from gslide.auth import login as do_login

    do_login()


@auth.command()
def status() -> None:
    """Check if saved session is valid."""
    from gslide.auth import status as do_status

    do_status()


@auth.command()
def logout() -> None:
    """Delete saved session."""
    from gslide.auth import logout as do_logout

    do_logout()


# --- Gen commands ---


@cli.group()
def gen() -> None:
    """Generate slides, infographics, and images."""


def _common_gen_options(f):
    """Shared options for single-gen commands."""
    f = click.option("--presentation", required=True, help="Presentation ID or URL")(f)
    f = click.option("--prompt", required=True, help="Generation prompt")(f)
    f = click.option("--timeout", default=120, type=int, help="Timeout in seconds")(f)
    return f


@gen.command()
@_common_gen_options
def infographic(presentation: str, prompt: str, timeout: int) -> None:
    """Generate an infographic slide."""
    from gslide.gen import gen_single

    gen_single(presentation, "infographic", prompt, timeout=timeout)


@gen.command()
@_common_gen_options
def slide(presentation: str, prompt: str, timeout: int) -> None:
    """Generate a slide."""
    from gslide.gen import gen_single

    gen_single(presentation, "slide", prompt, timeout=timeout)


@gen.command()
@_common_gen_options
@click.option("--slide-index", required=True, type=int, help="Target slide index")
@click.option(
    "--insert-as",
    default="image",
    type=click.Choice(["image", "background"]),
    help="Insert as image or background",
)
def image(
    presentation: str,
    prompt: str,
    timeout: int,
    slide_index: int,
    insert_as: str,
) -> None:
    """Generate and insert an image on a slide."""
    from gslide.gen import gen_single

    gen_single(
        presentation,
        "image",
        prompt,
        timeout=timeout,
        slide_index=slide_index,
        insert_as=insert_as,
    )


@gen.command()
@click.option("--file", "file_path", required=True, type=click.Path(exists=True), help="Path to prompts.json")
@click.option("--continue-on-error", is_flag=True, help="Continue on individual slide errors")
@click.option("--dry-run", is_flag=True, help="Validate and show summary without generating")
@click.option("--timeout", default=60, type=int, help="Timeout per slide in seconds")
def batch(file_path: str, continue_on_error: bool, dry_run: bool, timeout: int) -> None:
    """Generate slides from a prompts.json file."""
    from gslide.prompts import load_prompts, ValidationError

    try:
        prompts_data = load_prompts(Path(file_path))
    except ValidationError as e:
        click.echo(f"Validation error: {e}", err=True)
        sys.exit(1)

    if dry_run:
        tabs_used = {s.tab for s in prompts_data.slides}
        click.echo(f"Presentation: {prompts_data.presentation_id}")
        click.echo(f"Slides: {len(prompts_data.slides)}")
        click.echo(f"Images: {len(prompts_data.images)}")
        click.echo(f"Tabs: {', '.join(sorted(tabs_used))}")
        return

    from gslide.gen import gen_batch

    gen_batch(prompts_data, continue_on_error=continue_on_error, timeout=timeout)
