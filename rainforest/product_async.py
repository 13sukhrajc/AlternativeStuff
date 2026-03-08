# rainforest/product_async.py

import re
from rainforest.client import BASE_URL, API_KEY


async def get_product_details_async(client, asin: str, domain: str = "amazon.com") -> dict:
    params = {
        "type": "product",
        "amazon_domain": domain,
        "asin": asin,
        "api_key": API_KEY
    }

    r = await client.get(BASE_URL, params=params)
    r.raise_for_status()
    data = r.json()

    product = data.get("product", {})
    buybox = product.get("buybox_winner", {})

    availability_raw = buybox.get("availability", {}).get("raw", "")
    availability_msg = buybox.get("availability_message", "")
    is_in_stock = buybox.get("is_in_stock", None)

    stock_left = None
    match = re.search(r"Only (\d+) left", availability_raw)
    if match:
        stock_left = int(match.group(1))

    return {
        "title": product.get("title"),
        "price": buybox.get("price", {}).get("value"),
        "stock_raw": availability_raw or availability_msg,
        "stock_left": stock_left,
        "is_in_stock": is_in_stock,
        "images": product.get("images") or [None]
    }
