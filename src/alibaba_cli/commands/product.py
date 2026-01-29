"""Product commands."""

import json

import click

from alibaba_cli.client import AlibabaClient
from alibaba_cli.output import echo_error, echo_output


@click.group(name="product")
def product() -> None:
    """Product discovery and detail commands."""
    pass


@product.command(name="list")
@click.option(
    "--scene-id",
    required=True,
    help="Scene ID for product list (e.g., 906124611)",
)
@click.option(
    "--page",
    default=0,
    type=int,
    help="Page number (default: 0)",
)
@click.option(
    "--page-size",
    default=50,
    type=int,
    help="Items per page (default: 50, max 100)",
)
@click.pass_context
def product_list(ctx: click.Context, scene_id: str, page: int, page_size: int) -> None:
    """
    Get product list by scene ID.

    Common scene IDs:
      906124611  Standard US-based fulfillment
      906168847  Cross-border fulfillment (China to US)
      907135637  Fast fulfillment from US (within 48 hours)
      907732810  Dropshipping-eligible products from Mexico
      907180667  Top-selling products from the US
      907180664  Top-selling products from Mexico

    Example:
        alibaba-cli product list --scene-id 906124611 --page 0 --page-size 10
    """
    config = _get_config(ctx)

    query_req = json.dumps({
        "scene_id": scene_id,
        "index": page,  # API uses 'index' not 'page'
        "size": min(page_size, 100),  # Required by API (not documented)
        "product_type": "common",  # Required by API (not documented)
    })

    with AlibabaClient(config) as client:
        try:
            response = client.get("/eco/buyer/product/check", {"query_req": query_req})
        except Exception as e:
            echo_error(str(e))
            raise click.ClickException(str(e))

    result = response.get("result", {})
    output_data = {
        "product_ids": result.get("result_data", []),
        "total": result.get("result_total"),
        "page": page,
        "page_size": page_size,
    }

    echo_output(output_data, pretty=not ctx.obj.get("raw"))


@product.command(name="get")
@click.option(
    "--product-id",
    required=True,
    help="Alibaba product ID",
)
@click.option(
    "--country",
    default="US",
    help="Country code for product details (default: US)",
)
@click.pass_context
def product_get(ctx: click.Context, product_id: str, country: str) -> None:
    """
    Get detailed product information.

    Example:
        alibaba-cli product get --product-id 1601206892606
    """
    config = _get_config(ctx)

    # Use product_id as number and include country parameter
    query_req = json.dumps({"product_id": int(product_id), "country": country})

    with AlibabaClient(config) as client:
        try:
            response = client.get("/eco/buyer/product/description", {"query_req": query_req})
        except Exception as e:
            echo_error(str(e))
            raise click.ClickException(str(e))

    result = response.get("result", {}).get("result_data", {})
    echo_output(result, pretty=not ctx.obj.get("raw"))


@product.command(name="inventory")
@click.option(
    "--product-id",
    required=True,
    help="Alibaba product ID",
)
@click.option(
    "--sku-id",
    default=None,
    help="Specific SKU ID to check",
)
@click.option(
    "--shipping-from",
    default=None,
    help="Origin country code (CN, US, MX)",
)
@click.pass_context
def product_inventory(
    ctx: click.Context,
    product_id: str,
    sku_id: str | None,
    shipping_from: str | None,
) -> None:
    """
    Check product inventory levels.

    Example:
        alibaba-cli product inventory --product-id 1600927952535 --shipping-from CN
    """
    config = _get_config(ctx)

    inv_req = {"product_id": product_id}
    if sku_id:
        inv_req["sku_id"] = sku_id
    if shipping_from:
        inv_req["shipping_from"] = shipping_from

    with AlibabaClient(config) as client:
        try:
            response = client.get("/eco/buyer/product/inventory", {"inv_req": json.dumps(inv_req)})
        except Exception as e:
            echo_error(str(e))
            raise click.ClickException(str(e))

    result = response.get("result", {}).get("result_data", [])
    echo_output(result, pretty=not ctx.obj.get("raw"))


@product.command(name="local")
@click.option(
    "--country",
    required=True,
    help="Warehouse country code (e.g., US, MX)",
)
@click.option(
    "--page",
    default=0,
    type=int,
)
@click.option(
    "--page-size",
    default=50,
    type=int,
)
@click.pass_context
def product_local(
    ctx: click.Context,
    country: str,
    page: int,
    page_size: int,
) -> None:
    """
    Get products from local warehouse inventory.

    Example:
        alibaba-cli product local --country US --page 0 --page-size 10
    """
    config = _get_config(ctx)

    req = json.dumps({
        "index": page,  # API uses 'index' not 'page'
        "size": page_size,
        "country": country,
    })

    with AlibabaClient(config) as client:
        try:
            response = client.get("/eco/buyer/local/product/check", {"req": req})
        except Exception as e:
            echo_error(str(e))
            raise click.ClickException(str(e))

    result = response.get("result", {})
    output_data = {
        "product_ids": result.get("result_data", []),
        "country": country,
    }

    echo_output(output_data, pretty=not ctx.obj.get("raw"))


@product.command(name="crossborder")
@click.option(
    "--page",
    default=0,
    type=int,
)
@click.option(
    "--page-size",
    default=50,
    type=int,
)
@click.pass_context
def product_crossborder(
    ctx: click.Context,
    page: int,
    page_size: int,
) -> None:
    """
    Get cross-border products (shipping from China).

    Example:
        alibaba-cli product crossborder --page 0 --page-size 10
    """
    config = _get_config(ctx)

    param0 = json.dumps({
        "index": page,  # API uses 'index' not 'page'
        "size": page_size,
    })

    with AlibabaClient(config) as client:
        try:
            response = client.get("/eco/buyer/crossborder/product/check", {"param0": param0})
        except Exception as e:
            echo_error(str(e))
            raise click.ClickException(str(e))

    result = response.get("result", {})
    output_data = {
        "product_ids": result.get("result_data", []),
    }

    echo_output(output_data, pretty=not ctx.obj.get("raw"))


@product.command(name="search")
@click.option(
    "--scene-id",
    default="906124611",
    help="Scene ID for product list (default: 906124611)",
)
@click.option(
    "--limit",
    default=5,
    type=int,
    help="Number of products to fetch details for (default: 5)",
)
@click.pass_context
def product_search(ctx: click.Context, scene_id: str, limit: int) -> None:
    """
    Search for products and get full details.

    This convenience command fetches product IDs from a scene list,
    then retrieves full details for each product.

    Example:
        alibaba-cli product search --scene-id 906124611 --limit 3
    """
    import sys

    from alibaba_cli.output import echo_warning

    config = _get_config(ctx)

    # Step 1: Get product IDs
    click.echo(f"Fetching product list from scene {scene_id}...", err=True)
    query_req = json.dumps({
        "scene_id": scene_id,
        "page": 0,
        "page_size": limit,
        "size": limit,  # Required by API (not documented)
        "index": 0,  # Required by API (not documented)
    })

    with AlibabaClient(config) as client:
        try:
            response = client.get("/eco/buyer/product/check", {"query_req": query_req})
        except Exception as e:
            echo_error(str(e))
            raise click.ClickException(str(e))

    result = response.get("result", {})
    product_ids = result.get("result_data", [])

    if not product_ids:
        echo_warning("No products found")
        return

    click.echo(f"Found {len(product_ids)} product IDs. Fetching details...", err=True)

    # Step 2: Get details for each product
    products = []
    for i, product_id in enumerate(product_ids, 1):
        product_id_str = str(product_id)
        click.echo(f"  [{i}/{len(product_ids)}] Fetching product {product_id_str}...", err=True)

        try:
            response = client.get(
                "/eco/buyer/product/description",
                {"query_req": json.dumps({"product_id": product_id_str, "size": 10, "index": 0})}
            )
            product_data = response.get("result", {}).get("result_data", {})
            if product_data:
                products.append(product_data)
        except Exception as e:
            click.echo(f"    Warning: Failed to load product {product_id_str}: {e}", err=True)

    click.echo(f"Successfully loaded {len(products)}/{len(product_ids)} products", err=True)

    output_data = {
        "scene_id": scene_id,
        "total_found": len(product_ids),
        "successfully_loaded": len(products),
        "products": products,
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
