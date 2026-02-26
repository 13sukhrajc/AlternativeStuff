import httpx

BESTBUY_API_KEY = "YOUR_BESTBUY_API_KEY"

async def bestbuy_search_async(client, query):
    url = "https://api.bestbuy.com/v1/products"
    params = {
        "apiKey": BESTBUY_API_KEY,
        "format": "json",
        "show": "sku,name,salePrice,image,onlineAvailability,url",
        "search": query
    }

    r = await client.get(url, params=params)
    r.raise_for_status()
    data = r.json()

    products = data.get("products")
    if not products:
        return None

    return products[0]["sku"]
