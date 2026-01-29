"""Output formatting utilities."""

import json
from typing import Any

import click


def format_output(
    data: dict[str, Any],
    *,
    pretty: bool = True,
    raw: bool = False,
) -> str:
    """
    Format API response for CLI output.

    Args:
        data: Response data from API
        pretty: Pretty-print JSON with indentation
        raw: Output raw response without any formatting

    Returns:
        Formatted string for output
    """
    if raw:
        # Return raw JSON without pretty-printing
        return json.dumps(data, ensure_ascii=False)

    if pretty:
        return json.dumps(data, indent=2, ensure_ascii=False)

    return json.dumps(data, ensure_ascii=False)


def echo_output(
    data: dict[str, Any],
    *,
    pretty: bool = True,
    raw: bool = False,
) -> None:
    """
    Echo formatted output to CLI.

    Args:
        data: Response data from API
        pretty: Pretty-print JSON with indentation
        raw: Output raw response without any formatting
    """
    click.echo(format_output(data, pretty=pretty, raw=raw))


def echo_success(message: str) -> None:
    """Echo success message."""
    click.echo(click.style(message, fg="green"))


def echo_error(message: str) -> None:
    """Echo error message."""
    click.echo(click.style(message, fg="red"), err=True)


def echo_warning(message: str) -> None:
    """Echo warning message."""
    click.echo(click.style(message, fg="yellow"), err=True)
