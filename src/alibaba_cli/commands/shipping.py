"""Shipping calculation commands."""

import json

import click

from alibaba_cli.client import AlibabaClient
from alibaba_cli.output import echo_error, echo_output


@click.group(name="shipping")
def shipping() -> None:
    """Shipping cost calculation commands."""
    pass


@shipping.command(name="calculate")
@click.option(
    "--product-id",
    required=True,
    help="Alibaba product ID",
)
@click.option(
    "--quantity",
    required=True,
    type=int,
    help="Number of items",
)
@click.option(
    "--destination-country",
    required=True,
    help="Destination country code (e.g., US)",
)
@click.option(
    "--zip-code",
    default=None,
    help="Destination ZIP code",
)
@click.option(
    "--dispatch-location",
    default="CN",
    help="Origin location (CN, US, MX). Default: CN",
)
@click.option(
    "--no-fallback",
    is_flag=True,
    help="Disable automatic dispatch location fallback (CN → US → MX)",
)
@click.pass_context
def shipping_calculate(
    ctx: click.Context,
    product_id: str,
    quantity: int,
    destination_country: str,
    zip_code: str | None,
    dispatch_location: str,
    no_fallback: bool,
) -> None:
    """
    Calculate basic shipping cost for a single product.

    If no shipping options are returned, automatically tries fallback
    dispatch locations in order: CN → US → MX (unless --no-fallback is set).

    Example:
        alibaba-cli shipping calculate \\
            --product-id 1600124642247 \\
            --quantity 5 \\
            --destination-country US \\
            --zip-code 90001 \\
            --dispatch-location CN
    """
    from alibaba_cli.output import echo_warning

    config = _get_config(ctx)

    # Define fallback order
    fallback_locations = ["CN", "US", "MX"]

    # If user specified a location, try it first, then fallback from that point
    if dispatch_location in fallback_locations:
        start_index = fallback_locations.index(dispatch_location)
        locations_to_try = fallback_locations[start_index:]
    else:
        locations_to_try = [dispatch_location]

    response = None
    successful_location = None

    for location in locations_to_try:
        params = {
            "product_id": product_id,
            "quantity": str(quantity),
            "destination_country": destination_country,
            "dispatch_location": location,
        }

        if zip_code:
            params["zip_code"] = zip_code

        with AlibabaClient(config) as client:
            try:
                response = client.get("/shipping/freight/calculate", params)
                shipping_options = response.get("value", [])

                # If we got options, this location works
                if shipping_options:
                    successful_location = location
                    break
                elif location == locations_to_try[0]:
                    # First location had no results, try fallback
                    if no_fallback:
                        break
                    continue
            except Exception as e:
                # If this is the first location and no fallback, raise error
                if location == locations_to_try[0] and no_fallback:
                    echo_error(str(e))
                    raise click.ClickException(str(e))
                # Otherwise try next location
                continue

    if response is None:
        echo_error("No shipping options found for any dispatch location")
        raise click.ClickException("No shipping options available")

    shipping_options = response.get("value", [])
    output_data = {
        "product_id": product_id,
        "quantity": quantity,
        "destination": destination_country,
        "dispatch_location": successful_location or locations_to_try[0],
        "fallback_used": successful_location != dispatch_location if len(locations_to_try) > 1 else False,
        "options": shipping_options,
    }

    if successful_location and successful_location != dispatch_location:
        echo_warning(f"Primary location {dispatch_location} had no results. Using {successful_location} instead.")

    echo_output(output_data, pretty=not ctx.obj.get("raw"))


@shipping.command(name="calculate-advanced")
@click.option(
    "--e-company-id",
    required=True,
    help="Supplier company ID from product details",
)
@click.option(
    "--destination-country",
    required=True,
    help="Destination country code",
)
@click.option(
    "--address",
    required=True,
    help="Shipping address as JSON string",
)
@click.option(
    "--logistics-product-list",
    required=True,
    help="Products to ship as JSON array",
)
@click.option(
    "--dispatch-location",
    default="CN",
    help="Origin location (CN, US, MX). Default: CN",
)
@click.pass_context
def shipping_calculate_advanced(
    ctx: click.Context,
    e_company_id: str,
    destination_country: str,
    address: str,
    logistics_product_list: str,
    dispatch_location: str,
) -> None:
    """
    Calculate shipping for multiple products with full address.

    Address JSON format:
        {"zip": "10012", "country": "United States", "country_code": "US",
         "province": "New York", "province_code": "NY", "city": "New York",
         "address": "123 Main Street", "contact_person": "John Doe",
         "telephone": {"country": "+1", "number": "5551234567"}}

    Product list JSON format:
        [{"product_id": "1600191825486", "sku_id": "12321", "quantity": "1"}]

    Example:
        alibaba-cli shipping calculate-advanced \\
            --e-company-id "cVmhg7/xG8q3UQgcH/5Fag==" \\
            --destination-country US \\
            --address '{"zip":"10012","country_code":"US",...}' \\
            --logistics-product-list '[{"product_id":"1600191825486",...}]'
    """
    config = _get_config(ctx)

    # Parse JSON inputs
    try:
        address_obj = json.loads(address) if isinstance(address, str) else address
        products_obj = (
            json.loads(logistics_product_list)
            if isinstance(logistics_product_list, str)
            else logistics_product_list
        )
    except json.JSONDecodeError as e:
        echo_error(f"Invalid JSON: {e}")
        raise click.ClickException("Invalid JSON input")

    params = {
        "e_company_id": e_company_id,
        "destination_country": destination_country,
        "dispatch_location": dispatch_location,
        "address": json.dumps(address_obj),
        "logistics_product_list": json.dumps(products_obj),
    }

    with AlibabaClient(config) as client:
        try:
            response = client.get("/order/freight/calculate", params)
        except Exception as e:
            echo_error(str(e))
            raise click.ClickException(str(e))

    shipping_options = response.get("value", [])
    output_data = {
        "supplier": e_company_id,
        "destination": destination_country,
        "dispatch_location": dispatch_location,
        "products": products_obj,
        "options": shipping_options,
    }

    echo_output(output_data, pretty=not ctx.obj.get("raw"))


def _get_config(ctx: click.Context) -> click.Context:
    """Get config from context, raising error if not available."""
    config = ctx.obj.get("config")
    if not config:
        config_error = ctx.obj.get("config_error", "Credentials not configured")
        echo_error(config_error)
        raise click.ClickException("Configuration required")
    return ctx
