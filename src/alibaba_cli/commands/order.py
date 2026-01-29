"""Order management commands."""

import json

import click

from alibaba_cli.client import AlibabaClient
from alibaba_cli.output import echo_error, echo_output


@click.group(name="order")
def order() -> None:
    """Order management commands."""
    pass


@order.command(name="create")
@click.option(
    "--channel-refer-id",
    required=True,
    help="Your internal order reference ID",
)
@click.option(
    "--product-list",
    required=True,
    help="Products to order as JSON array",
)
@click.option(
    "--logistics-detail",
    required=True,
    help="Shipping details as JSON object",
)
@click.option(
    "--remark",
    default=None,
    help="Order notes",
)
@click.pass_context
def order_create(
    ctx: click.Context,
    channel_refer_id: str,
    product_list: str,
    logistics_detail: str,
    remark: str | None,
) -> None:
    """
    Create a BuyNow dropshipping order.

    Product list format:
        [{"product_id": "100001", "sku_id": "200001", "quantity": "10"}]

    Logistics detail format:
        {"shipment_address": {...}, "dispatch_location": "CN", "carrier_code": "EX_ASP_JYC_FEDEX"}

    Shipment address format:
        {"zip": "10012", "country": "United States", "country_code": "US",
         "province": "New York", "province_code": "NY", "city": "New York",
         "address": "123 Main Street", "contact_person": "John Doe",
         "telephone": {"country": "+1", "number": "5551234567"}}

    Example:
        alibaba-cli order create \\
            --channel-refer-id "ORDER-2026-001" \\
            --product-list '[{"product_id":"100001","sku_id":"200001","quantity":"10"}]' \\
            --logistics-detail '{"shipment_address":{...},"dispatch_location":"CN"}'
    """
    config = _get_config(ctx)

    # Parse JSON inputs
    try:
        products_obj = json.loads(product_list) if isinstance(product_list, str) else product_list
        logistics_obj = json.loads(logistics_detail) if isinstance(logistics_detail, str) else logistics_detail
    except json.JSONDecodeError as e:
        echo_error(f"Invalid JSON: {e}")
        raise click.ClickException("Invalid JSON input")

    params = {
        "channel_refer_id": channel_refer_id,
        "product_list": json.dumps(products_obj),
        "logistics_detail": json.dumps(logistics_obj),
    }

    if remark:
        params["remark"] = remark

    with AlibabaClient(config) as client:
        try:
            response = client.post("/buynow/order/create", params)
        except Exception as e:
            echo_error(str(e))
            raise click.ClickException(str(e))

    output_data = {
        "trade_id": response.get("value", {}).get("trade_id") or response.get("trade_id"),
        "pay_url": response.get("value", {}).get("pay_url") or response.get("pay_url"),
        "channel_refer_id": channel_refer_id,
    }

    echo_output(output_data, pretty=not ctx.obj.get("raw"))

    # Show helpful info
    click.echo("\n" + "=" * 60)
    click.echo("Order created! Next steps:")
    click.echo(f"  1. Pay for order: alibaba-cli order pay --order-id-list '[\"{output_data["trade_id"]}\"]'")
    click.echo(f"  2. Check status: alibaba-cli order get --trade-id {output_data["trade_id"]}")
    if output_data.get("pay_url"):
        click.echo(f"  3. Manual payment: {output_data["pay_url"]}")
    click.echo("=" * 60)


@order.command(name="pay")
@click.option(
    "--order-id-list",
    required=True,
    help="List of order IDs to pay as JSON array",
)
@click.option(
    "--payment-method",
    default="CREDIT_CARD",
    help="Payment method (default: CREDIT_CARD)",
)
@click.option(
    "--user-ip",
    required=True,
    help="User IP address",
)
@click.option(
    "--user-agent",
    required=True,
    help="User agent string",
)
@click.option(
    "--dry-run",
    is_flag=True,
    help="Validate request without actually paying",
)
@click.pass_context
def order_pay(
    ctx: click.Context,
    order_id_list: str,
    payment_method: str,
    user_ip: str,
    user_agent: str,
    dry_run: bool,
) -> None:
    """
    Pay for one or more orders.

    Example:
        alibaba-cli order pay \\
            --order-id-list '["234193410001028893"]' \\
            --payment-method CREDIT_CARD \\
            --user-ip "192.168.1.1" \\
            --user-agent "Mozilla/5.0..."
    """
    if dry_run:
        click.echo("DRY RUN: Request validated, not executing payment.")
        return

    config = _get_config(ctx)

    # Parse order ID list
    try:
        orders = json.loads(order_id_list) if isinstance(order_id_list, str) else order_id_list
    except json.JSONDecodeError as e:
        echo_error(f"Invalid JSON: {e}")
        raise click.ClickException("Invalid JSON input")

    payment_request = {
        "order_id_list": orders,
        "payment_method": payment_method,
        "user_ip": user_ip,
        "user_agent": user_agent,
        "accept_language": "en-US,en;q=0.9",
        "screen_resolution": "1920*1080",
        "is_pc": True,
    }

    params = {"param_order_pay_request": json.dumps(payment_request)}

    with AlibabaClient(config) as client:
        try:
            response = client.post("/alibaba/dropshipping/order/pay", params)
        except Exception as e:
            echo_error(str(e))
            raise click.ClickException(str(e))

    value = response.get("value", response)
    output_data = {
        "status": value.get("status"),
        "order_ids": orders,
        "reason_code": value.get("reason_code"),
        "reason_message": value.get("reason_message"),
        "pay_url": value.get("pay_url"),
    }

    echo_output(output_data, pretty=not ctx.obj.get("raw"))


@order.command(name="list")
@click.option(
    "--role",
    default="buyer",
    type=click.Choice(["buyer", "seller"]),
    help="Role for order list (default: buyer)",
)
@click.option(
    "--status",
    default=None,
    help="Filter by order status",
)
@click.option(
    "--start-page",
    default=0,
    type=int,
    help="Page number (default: 0)",
)
@click.option(
    "--page-size",
    default=20,
    type=int,
    help="Items per page (default: 20)",
)
@click.pass_context
def order_list(
    ctx: click.Context,
    role: str,
    status: str | None,
    start_page: int,
    page_size: int,
) -> None:
    """
    List orders with optional filtering.

    Example:
        alibaba-cli order list --role buyer --status paid --start-page 0
    """
    config = _get_config(ctx)

    params = {"role": role, "start_page": str(start_page), "page_size": str(page_size)}

    if status:
        params["status"] = status

    with AlibabaClient(config) as client:
        try:
            response = client.get("/alibaba/order/list", params)
        except Exception as e:
            echo_error(str(e))
            raise click.ClickException(str(e))

    value = response.get("value", {})
    output_data = {
        "total_count": value.get("total_count"),
        "page": start_page,
        "page_size": page_size,
        "orders": value.get("order_list", []),
    }

    echo_output(output_data, pretty=not ctx.obj.get("raw"))


@order.command(name="get")
@click.option(
    "--trade-id",
    required=True,
    help="Alibaba order ID (trade_id)",
)
@click.option(
    "--language",
    default="en_US",
    help="Response language (default: en_US)",
)
@click.pass_context
def order_get(
    ctx: click.Context,
    trade_id: str,
    language: str,
) -> None:
    """
    Get detailed order information.

    Example:
        alibaba-cli order get --trade-id 234193410001028893
    """
    config = _get_config(ctx)

    params = {"e_trade_id": trade_id, "language": language}

    with AlibabaClient(config) as client:
        try:
            response = client.get("/alibaba/order/get", params)
        except Exception as e:
            echo_error(str(e))
            raise click.ClickException(str(e))

    echo_output(response.get("value", response), pretty=not ctx.obj.get("raw"))


@order.command(name="logistics")
@click.option(
    "--trade-id",
    required=True,
    help="Alibaba order ID",
)
@click.option(
    "--data-select",
    default="logistic_order",
    help="Data selection (default: logistic_order)",
)
@click.pass_context
def order_logistics(
    ctx: click.Context,
    trade_id: str,
    data_select: str,
) -> None:
    """
    Get order logistics status and tracking number.

    Example:
        alibaba-cli order logistics --trade-id 234193410001028893
    """
    config = _get_config(ctx)

    params = {"trade_id": trade_id, "data_select": data_select}

    with AlibabaClient(config) as client:
        try:
            response = client.get("/order/logistics/query", params)
        except Exception as e:
            echo_error(str(e))
            raise click.ClickException(str(e))

    echo_output(response.get("value", response), pretty=not ctx.obj.get("raw"))


@order.command(name="tracking")
@click.option(
    "--trade-id",
    required=True,
    help="Alibaba order ID",
)
@click.pass_context
def order_tracking(
    ctx: click.Context,
    trade_id: str,
) -> None:
    """
    Get tracking events for an order.

    Example:
        alibaba-cli order tracking --trade-id 234193410001028893
    """
    config = _get_config(ctx)

    with AlibabaClient(config) as client:
        try:
            response = client.get("/order/logistics/tracking/get", {"trade_id": trade_id})
        except Exception as e:
            echo_error(str(e))
            raise click.ClickException(str(e))

    tracking_list = response.get("tracking_list", [])
    output_data = {
        "trade_id": trade_id,
        "tracking": tracking_list,
    }

    echo_output(output_data, pretty=not ctx.obj.get("raw"))


@order.command(name="fund")
@click.option(
    "--trade-id",
    required=True,
    help="Alibaba order ID",
)
@click.option(
    "--data-select",
    default="fund_transaction_fee",
    help="Data selection (default: fund_transaction_fee)",
)
@click.pass_context
def order_fund(
    ctx: click.Context,
    trade_id: str,
    data_select: str,
) -> None:
    """
    Get payment and fund details for an order.

    Example:
        alibaba-cli order fund --trade-id 234193410001028893
    """
    config = _get_config(ctx)

    params = {"e_trade_id": trade_id, "data_select": data_select}

    with AlibabaClient(config) as client:
        try:
            response = client.get("/alibaba/order/fund/query", params)
        except Exception as e:
            echo_error(str(e))
            raise click.ClickException(str(e))

    echo_output(response.get("value", response), pretty=not ctx.obj.get("raw"))


@order.command(name="test-flow")
@click.option(
    "--product-id",
    required=True,
    help="Product ID to order",
)
@click.option(
    "--sku-id",
    required=True,
    help="SKU ID to order",
)
@click.option(
    "--quantity",
    default="1",
    help="Quantity to order (default: 1)",
)
@click.option(
    "--address",
    required=True,
    help='Shipping address as JSON. Example: \'{"zip":"10012","country_code":"US",...}\'',
)
@click.option(
    "--dispatch-location",
    default="CN",
    help="Origin location (default: CN)",
)
@click.option(
    "--pay",
    is_flag=True,
    help="Attempt payment after order creation",
)
@click.option(
    "--user-ip",
    default="127.0.0.1",
    help="User IP for payment (only used with --pay)",
)
@click.option(
    "--user-agent",
    default="alibaba-cli-test/1.0",
    help="User agent for payment (only used with --pay)",
)
@click.pass_context
def order_test_flow(
    ctx: click.Context,
    product_id: str,
    sku_id: str,
    quantity: str,
    address: str,
    dispatch_location: str,
    pay: bool,
    user_ip: str,
    user_agent: str,
) -> None:
    """
    Test the complete order flow: calculate shipping → create order → get details → (optionally) pay.

    This is a convenience command for testing the full order lifecycle.

    Address JSON format:
        {"zip": "10012", "country": "United States", "country_code": "US",
         "province": "New York", "province_code": "NY", "city": "New York",
         "address": "123 Main Street", "contact_person": "Test User",
         "telephone": {"country": "+1", "number": "5551234567"}}

    Example:
        alibaba-cli order test-flow \\
            --product-id 1600191825486 \\
            --sku-id 105613018158 \\
            --address '{"zip":"10012","country_code":"US",...}'
    """
    import sys

    from alibaba_cli.output import echo_success, echo_warning

    config = _get_config(ctx)

    click.echo("=" * 60)
    click.echo("ORDER TEST FLOW")
    click.echo("=" * 60)

    flow_results = {
        "steps": [],
        "trade_id": None,
        "errors": [],
    }

    # Step 1: Calculate shipping
    click.echo("\n[Step 1/4] Calculating shipping...", err=True)
    try:
        shipping_params = {
            "product_id": product_id,
            "quantity": quantity,
            "destination_country": json.loads(address).get("country_code", "US"),
            "dispatch_location": dispatch_location,
        }

        with AlibabaClient(config) as client:
            shipping_response = client.get("/shipping/freight/calculate", shipping_params)

        shipping_options = shipping_response.get("value", [])
        if shipping_options:
            flow_results["steps"].append({
                "step": "calculate_shipping",
                "status": "success",
                "options_count": len(shipping_options),
                "first_option": shipping_options[0].get("vendor_name") if shipping_options else None,
            })
            echo_success(f"  Found {len(shipping_options)} shipping options")
            for i, opt in enumerate(shipping_options[:3], 1):
                click.echo(f"    {i}. {opt.get('vendor_name')}: ${opt.get('fee', {}).get('amount', 'N/A')} ({opt.get('delivery_time', 'N/A')} days)")
        else:
            flow_results["steps"].append({
                "step": "calculate_shipping",
                "status": "no_options",
            })
            echo_warning("  No shipping options found")
    except Exception as e:
        flow_results["errors"].append({"step": "calculate_shipping", "error": str(e)})
        echo_error(f"  Failed: {e}")
        return

    # Step 2: Create order
    click.echo("\n[Step 2/4] Creating order...", err=True)
    channel_refer_id = f"TEST-{product_id[:8]}-{quantity}"

    # Build product list
    product_list = json.dumps([{
        "product_id": product_id,
        "sku_id": sku_id,
        "quantity": quantity,
    }])

    # Build logistics detail
    address_obj = json.loads(address) if isinstance(address, str) else address
    logistics_detail_obj = {
        "shipment_address": {
            "zip": address_obj.get("zip", "10012"),
            "country": address_obj.get("country", "United States"),
            "country_code": address_obj.get("country_code", "US"),
            "province": address_obj.get("province", "New York"),
            "province_code": address_obj.get("province_code", "NY"),
            "city": address_obj.get("city", "New York"),
            "address": address_obj.get("address", "123 Main Street"),
            "contact_person": address_obj.get("contact_person", "Test User"),
            "telephone": address_obj.get("telephone", {"country": "+1", "number": "5551234567"}),
        },
        "dispatch_location": dispatch_location,
        "carrier_code": "EX_ASP_JYC_FEDEX",  # Default carrier
    }

    try:
        order_params = {
            "channel_refer_id": channel_refer_id,
            "product_list": product_list,
            "logistics_detail": json.dumps(logistics_detail_obj),
        }

        with AlibabaClient(config) as client:
            order_response = client.post("/buynow/order/create", order_params)

        trade_id = order_response.get("value", {}).get("trade_id") or order_response.get("trade_id")
        pay_url = order_response.get("value", {}).get("pay_url") or order_response.get("pay_url")

        if trade_id:
            flow_results["trade_id"] = trade_id
            flow_results["steps"].append({
                "step": "create_order",
                "status": "success",
                "trade_id": trade_id,
                "channel_refer_id": channel_refer_id,
            })
            echo_success(f"  Order created: {trade_id}")
            if pay_url:
                click.echo(f"  Pay URL: {pay_url}")
        else:
            flow_results["errors"].append({"step": "create_order", "error": "No trade_id returned"})
            echo_error("  Failed: No trade_id returned")
            return
    except Exception as e:
        flow_results["errors"].append({"step": "create_order", "error": str(e)})
        echo_error(f"  Failed: {e}")
        return

    # Step 3: Get order details
    click.echo("\n[Step 3/4] Getting order details...", err=True)
    try:
        with AlibabaClient(config) as client:
            details_response = client.get(
                "/alibaba/order/get",
                {"e_trade_id": trade_id, "language": "en_US"}
            )

        order_details = details_response.get("value", {})
        flow_results["steps"].append({
            "step": "get_order",
            "status": "success",
            "order_status": order_details.get("trade_status"),
            "total_amount": order_details.get("total_amount", {}),
        })
        echo_success(f"  Order status: {order_details.get('trade_status')}")
        click.echo(f"  Total amount: {order_details.get('total_amount', {}).get('amount', 'N/A')} {order_details.get('total_amount', {}).get('currency', 'N/A')}")
    except Exception as e:
        flow_results["errors"].append({"step": "get_order", "error": str(e)})
        echo_error(f"  Failed: {e}")

    # Step 4: Optional payment
    if pay:
        click.echo("\n[Step 4/4] Attempting payment...", err=True)
        click.echo("  WARNING: This will attempt to charge your payment method!", err=True)

        payment_request = {
            "order_id_list": [trade_id],
            "payment_method": "CREDIT_CARD",
            "user_ip": user_ip,
            "user_agent": user_agent,
            "accept_language": "en-US,en;q=0.9",
            "screen_resolution": "1920*1080",
            "is_pc": True,
        }

        try:
            with AlibabaClient(config) as client:
                pay_response = client.post(
                    "/alibaba/dropshipping/order/pay",
                    {"param_order_pay_request": json.dumps(payment_request)}
                )

            pay_value = pay_response.get("value", pay_response)
            payment_status = pay_value.get("status")

            flow_results["steps"].append({
                "step": "payment",
                "status": payment_status,
                "reason_code": pay_value.get("reason_code"),
                "reason_message": pay_value.get("reason_message"),
            })

            if payment_status == "PAY_SUCCESS":
                echo_success(f"  Payment successful!")
            else:
                echo_warning(f"  Payment status: {payment_status}")
                if pay_value.get("reason_message"):
                    click.echo(f"  Reason: {pay_value.get('reason_message')}")
        except Exception as e:
            flow_results["errors"].append({"step": "payment", "error": str(e)})
            echo_error(f"  Failed: {e}")
    else:
        click.echo("\n[Step 4/4] Payment skipped (--pay flag not set)")

    # Summary
    click.echo("\n" + "=" * 60)
    click.echo("TEST FLOW SUMMARY")
    click.echo("=" * 60)
    click.echo(f"Steps completed: {len(flow_results['steps'])}")
    if flow_results["errors"]:
        click.echo(f"Errors: {len(flow_results['errors'])}")
    if flow_results["trade_id"]:
        click.echo(f"Trade ID: {flow_results['trade_id']}")
        click.echo(f"\nTo check status later:")
        click.echo(f"  alibaba-cli order get --trade-id {flow_results['trade_id']}")
        click.echo(f"  alibaba-cli order tracking --trade-id {flow_results['trade_id']}")
    click.echo("=" * 60)

    echo_output(flow_results, pretty=not ctx.obj.get("raw"))


def _get_config(ctx: click.Context) -> click.Context:
    """Get config from context, raising error if not available."""
    config = ctx.obj.get("config")
    if not config:
        config_error = ctx.obj.get("config_error", "Credentials not configured")
        echo_error(config_error)
        raise click.ClickException("Configuration required")
    return ctx
