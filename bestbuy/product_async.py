import httpx

BESTBUY_API_KEY = "YOUR_BESTBUY_API_KEY"

async def bestbuy_product_async(client, sku):
    url = f"https://api.bestbuy.com/v1/products/{sku}.json"
    params = {"apiKey": BESTBUY_API_KEY}

    r = await client.get(url, params=params)
    r.raise_for_status()
    data = r.json()

    return {
        "merchant": "Best Buy",
        "id": sku,
        "title": data.get("name"),
        "price": data.get("salePrice"),
        "stock": data.get("onlineAvailability"),
        "image": data.get("image"),
        "affiliate_link": f"https://www.bestbuy.com/site/{sku}.p?skuId={sku}&ref=YOUR_IMPACT_ID"
    }
