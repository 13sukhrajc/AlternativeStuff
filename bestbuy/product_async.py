# bestbuy/product_async.py

import os
from dotenv import load_dotenv

load_dotenv()

BESTBUY_API_KEY = os.getenv("BESTBUY_API_KEY")
BASE_URL = "https://api.bestbuy.com/v1/products"


async def bestbuy_product_async(client, sku: str) -> dict | None:
    url = f"{BASE_URL}/{sku}.json"
    params = {"apiKey": BESTBUY_API_KEY}

    r = await client.get(url, params=params)
    r.raise_for_status()
    data = r.json()

    if not data:
        return None

    return {
        "merchant": "Best Buy",
        "id": sku,
        "title": data.get("name"),
        "price": data.get("salePrice"),
        "stock": data.get("onlineAvailability"),
        "image": data.get("image"),
        "affiliate_link": None  # Set by utils/affiliate.py in enhancer
    }