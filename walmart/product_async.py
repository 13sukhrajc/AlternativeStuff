# walmart/product_async.py

import os
from dotenv import load_dotenv

load_dotenv()

WALMART_API_KEY = os.getenv("WALMART_API_KEY")
BASE_URL = "https://developer.api.walmart.com/api-proxy/service/affil/product/v2/items"


async def walmart_product_async(client, item_id: str) -> dict | None:
    url = f"{BASE_URL}/{item_id}"
    params = {"apiKey": WALMART_API_KEY}

    r = await client.get(url, params=params)
    r.raise_for_status()
    data = r.json()

    if not data:
        return None

    return {
        "merchant": "Walmart",
        "id": item_id,
        "title": data.get("name"),
        "price": data.get("salePrice"),
        "stock": data.get("stock"),
        "image": data.get("largeImage"),
        "affiliate_link": None  # Set by utils/affiliate.py in enhancer
    }
