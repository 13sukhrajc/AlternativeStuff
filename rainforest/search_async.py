import httpx
from .client import BASE_URL, API_KEY

async def get_asin_from_title_async(client, title, domain="amazon.com"):
    params = {
        "type": "search",
        "amazon_domain": domain,
        "search_term": title,
        "api_key": API_KEY
    }

    r = await client.get(BASE_URL, params=params)
    r.raise_for_status()
    data = r.json()

    results = data.get("search_results", [])
    if not results:
        return None

    return results[0].get("asin")
