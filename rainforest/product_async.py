import httpx
from .client import BASE_URL, API_KEY

async def get_product_details_async(client, asin, domain="amazon.com"):
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

    return {
        "title": product.get("title"),
        "price": product.get("buybox_winner", {}).get("price", {}).get("value"),
        "stock": product.get("buybox_winner", {}).get("availability", {}).get("raw"),
        "images": product.get("images", [])
    }
