# walmart/search_async.py

import os
from dotenv import load_dotenv

load_dotenv()

WALMART_API_KEY = os.getenv("WALMART_API_KEY")
BASE_URL = "https://developer.api.walmart.com/api-proxy/service/affil/product/v2/search"


async def walmart_search_async(client, query: str) -> str | None:
    params = {
        "query": query,
        "apiKey": WALMART_API_KEY
    }

    r = await client.get(BASE_URL, params=params)
    r.raise_for_status()
    data = r.json()

    items = data.get("items")
    if not items:
        return None

    return str(items[0]["itemId"])
