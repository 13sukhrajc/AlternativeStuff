import httpx

WALMART_API_KEY = "YOUR_WALMART_API_KEY"

async def walmart_search_async(client, query):
    url = "https://developer.api.walmart.com/api-proxy/service/affil/product/v2/search"
    params = {
        "query": query,
        "apiKey": WALMART_API_KEY
    }

    r = await client.get(url, params=params)
    r.raise_for_status()
    data = r.json()

    items = data.get("items")
    if not items:
        return None

    return items[0]["itemId"]
