"""Authentication commands."""

import json

import click

from alibaba_cli.client import AlibabaClient
from alibaba_cli.output import echo_error, echo_output


@click.group(name="auth")
def auth() -> None:
    """Authentication commands for OAuth token management."""
    pass


@auth.command(name="token-create")
@click.option(
    "--code",
    required=True,
    help="OAuth authorization code from Alibaba",
)
@click.pass_context
def token_create(ctx: click.Context, code: str) -> None:
    """
    Exchange OAuth authorization code for access token.

    First, visit the authorization URL in your browser:
    https://openapi-auth.alibaba.com/oauth/authorize?response_type=code&client_id={app_key}&redirect_uri={callback_url}

    Example:
        alibaba-cli auth token create --code 3_500102_JxZ05Ux3cnnSSUm6dCxYg6Q26
    """
    config = _get_config(ctx)

    with AlibabaClient(config) as client:
        try:
            response = client.get("/auth/token/create", {"code": code})
        except Exception as e:
            echo_error(str(e))
            raise click.ClickException(str(e))

    # Extract token data
    token_data = {
        "access_token": response.get("access_token"),
        "refresh_token": response.get("refresh_token"),
        "expires_in": response.get("expires_in"),
        "refresh_expires_in": response.get("refresh_expires_in"),
        "user_info": response.get("user_info", {}),
        "account_platform": response.get("account_platform"),
    }

    echo_output(token_data, pretty=not ctx.obj.get("raw"))

    # Show helpful next steps
    click.echo("\n" + "=" * 60)
    click.echo("Next steps:")
    click.echo("  export ALIBABA_ACCESS_TOKEN='%s'" % token_data["access_token"])
    click.echo("  export ALIBABA_REFRESH_TOKEN='%s'" % token_data["refresh_token"])
    click.echo("=" * 60)


@auth.command(name="token-refresh")
@click.option(
    "--refresh-token",
    envvar="ALIBABA_REFRESH_TOKEN",
    help="OAuth refresh token",
)
@click.pass_context
def token_refresh(ctx: click.Context, refresh_token: str | None) -> None:
    """
    Refresh access token using refresh token.

    Example:
        alibaba-cli auth token refresh --refresh-token YOUR_REFRESH_TOKEN
    """
    config = _get_config(ctx)

    # Use provided token or from config
    token = refresh_token or config.refresh_token
    if not token:
        echo_error("No refresh token available. Use --refresh-token or set ALIBABA_REFRESH_TOKEN.")
        raise click.ClickException("Refresh token required")

    with AlibabaClient(config) as client:
        try:
            response = client.get("/auth/token/refresh", {"refresh_token": token})
        except Exception as e:
            echo_error(str(e))
            raise click.ClickException(str(e))

    token_data = {
        "access_token": response.get("access_token"),
        "refresh_token": response.get("refresh_token"),
        "expires_in": response.get("expires_in"),
        "refresh_expires_in": response.get("refresh_expires_in"),
    }

    echo_output(token_data, pretty=not ctx.obj.get("raw"))

    click.echo("\n" + "=" * 60)
    click.echo("Updated tokens:")
    click.echo("  export ALIBABA_ACCESS_TOKEN='%s'" % token_data["access_token"])
    click.echo("  export ALIBABA_REFRESH_TOKEN='%s'" % token_data["refresh_token"])
    click.echo("=" * 60)


@auth.command(name="status")
@click.pass_context
def auth_status(ctx: click.Context) -> None:
    """Show current authentication status."""
    from alibaba_cli.output import echo_success, echo_warning

    config = ctx.obj.get("config")
    if not config:
        config_error = ctx.obj.get("config_error", "Unknown error")
        echo_error(f"Not configured: {config_error}")
        raise click.ClickException("Configuration required")

    status_info = {
        "environment": "sandbox" if config.use_sandbox else "production",
        "app_key": config.app_key[:8] + "..." if config.app_key else None,
        "has_access_token": bool(config.access_token),
        "has_refresh_token": bool(config.refresh_token),
    }

    if config.access_token:
        echo_success("Authentication configured")
    else:
        echo_warning("No access token - run 'auth token create' first")

    echo_output(status_info, pretty=not ctx.obj.get("raw"))


def _get_config(ctx: click.Context) -> click.Context:
    """Get config from context, raising error if not available."""
    config = ctx.obj.get("config")
    if not config:
        config_error = ctx.obj.get("config_error", "Credentials not configured")
        echo_error(config_error)
        raise click.ClickException("Configuration required")
    ctx.obj["config"] = config
    return ctx
