# bestbuy/search_async.py

import os
from dotenv import load_dotenv

load_dotenv()

BESTBUY_API_KEY = os.getenv("BESTBUY_API_KEY")
BASE_URL = "https://api.bestbuy.com/v1/products"


async def bestbuy_search_async(client, query: str) -> str | None:
    params = {
        "apiKey": BESTBUY_API_KEY,
        "format": "json",
        "show": "sku,name,salePrice,image,onlineAvailability,url",
        "search": query
    }

    r = await client.get(BASE_URL, params=params)
    r.raise_for_status()
    data = r.json()

    products = data.get("products")
    if not products:
        return None

    return str(products[0]["sku"])