"""Main CLI entry point."""

import sys

import click

from alibaba_cli import __version__
from alibaba_cli.config import Config
from alibaba_cli.output import echo_error, echo_output


@click.group()
@click.version_option(version=__version__)
@click.option(
    "--app-key",
    envvar="ALIBABA_APP_KEY",
    help="Application key (or set ALIBABA_APP_KEY env var)",
)
@click.option(
    "--app-secret",
    envvar="ALIBABA_APP_SECRET",
    help="Application secret (or set ALIBABA_APP_SECRET env var)",
)
@click.option(
    "--access-token",
    envvar="ALIBABA_ACCESS_TOKEN",
    help="OAuth access token (or set ALIBABA_ACCESS_TOKEN env var)",
)
@click.option(
    "--refresh-token",
    envvar="ALIBABA_REFRESH_TOKEN",
    help="OAuth refresh token (or set ALIBABA_REFRESH_TOKEN env var)",
)
@click.option(
    "--sandbox/--no-sandbox",
    envvar="ALIBABA_USE_SANDBOX",
    default=False,
    help="Use sandbox environment",
)
@click.option(
    "--timeout",
    envvar="ALIBABA_TIMEOUT",
    default=30,
    type=int,
    help="Request timeout in seconds (default: 30)",
)
@click.option(
    "--raw",
    is_flag=True,
    help="Output raw JSON without pretty-printing",
)
@click.option(
    "--verbose", "-v",
    is_flag=True,
    help="Enable verbose output",
)
@click.pass_context
def main(
    ctx: click.Context,
    app_key: str | None,
    app_secret: str | None,
    access_token: str | None,
    refresh_token: str | None,
    sandbox: bool,
    timeout: int,
    raw: bool,
    verbose: bool,
) -> None:
    """
    Alibaba API CLI - Tool for validating Alibaba.com Open Platform API v2 documentation.

    Example:
        alibaba-cli auth token create --code YOUR_CODE
        alibaba-cli product list --scene-id 906124611
    """
    # Store config in context for subcommands
    ctx.ensure_object(dict)

    # Build config overrides from CLI flags
    overrides: dict[str, str | bool] = {}
    if app_key:
        overrides["app_key"] = app_key
    if app_secret:
        overrides["app_secret"] = app_secret
    if access_token:
        overrides["access_token"] = access_token
    if refresh_token:
        overrides["refresh_token"] = refresh_token
    if sandbox:
        overrides["use_sandbox"] = True
    if timeout != 30:
        overrides["timeout"] = timeout

    # Try to load config - don't fail if credentials not provided yet
    # (some commands like 'auth status' work without credentials)
    try:
        config = Config.from_env(**overrides)
        ctx.obj["config"] = config
    except ValueError as e:
        # Store error for subcommands to handle if needed
        ctx.obj["config_error"] = str(e)

    # Store other options
    ctx.obj["raw"] = raw
    ctx.obj["verbose"] = verbose


@main.command()
@click.pass_context
def status(ctx: click.Context) -> None:
    """Show authentication and configuration status."""
    from alibaba_cli.output import echo_success, echo_warning

    config_error = ctx.obj.get("config_error")
    config = ctx.obj.get("config")

    status_info = {
        "configured": config is not None,
        "environment": "sandbox" if config and config.use_sandbox else "production",
        "has_access_token": bool(config and config.access_token),
        "has_refresh_token": bool(config and config.refresh_token),
        "timeout": config.timeout if config else 30,
    }

    if config_error:
        echo_warning(f"Not configured: {config_error}")
        echo_output(status_info)
        sys.exit(1)

    echo_success("Configuration loaded")
    echo_output(status_info)

    if config and not config.access_token:
        echo_warning("No access token - run 'auth token create' first")


# Import command groups
from alibaba_cli.commands import auth, order, product, shipping

# Register command groups
main.add_command(auth.auth)
main.add_command(product.product)
main.add_command(shipping.shipping)
main.add_command(order.order)


if __name__ == "__main__":
    main()
