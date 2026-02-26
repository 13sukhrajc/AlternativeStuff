import httpx

WALMART_API_KEY = "YOUR_WALMART_API_KEY"

async def walmart_product_async(client, item_id):
    url = f"https://developer.api.walmart.com/api-proxy/service/affil/product/v2/items/{item_id}"
    params = {"apiKey": WALMART_API_KEY}

    r = await client.get(url, params=params)
    r.raise_for_status()
    data = r.json()

    return {
        "merchant": "Walmart",
        "id": item_id,
        "title": data.get("name"),
        "price": data.get("salePrice"),
        "stock": data.get("stock"),
        "image": data.get("largeImage"),
        "affiliate_link": f"https://www.walmart.com/ip/{item_id}?affp1=YOUR_TAG"
    }
