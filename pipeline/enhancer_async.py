import asyncio
import httpx

from rainforest.search_async import get_asin_from_title_async
from rainforest.product_async import get_product_details_async

from walmart.search_async import walmart_search_async
from walmart.product_async import walmart_product_async

from bestbuy.search_async import bestbuy_search_async
from bestbuy.product_async import bestbuy_product_async

from pipeline.schema import build_product_entry
from utils.affiliate import build_affiliate_link


async def enhance_substitutes_async(data, domain="amazon.com"):
    original_title = data["original_product"]["title"]

    async with httpx.AsyncClient(timeout=20) as client:

        # Amazon ASIN lookup
        amazon_asin = await get_asin_from_title_async(client, original_title, domain)

        # Amazon product details
        amazon_details = await get_product_details_async(client, amazon_asin, domain)

        # Walmart + Best Buy lookups
        walmart_id = await walmart_search_async(client, original_title)
        bestbuy_id = await bestbuy_search_async(client, original_title)

        walmart_details = (
            await walmart_product_async(client, walmart_id)
            if walmart_id else None
        )

        bestbuy_details = (
            await bestbuy_product_async(client, bestbuy_id)
            if bestbuy_id else None
        )

    merchants = []

    # Amazon
    merchants.append({
        "merchant": "Amazon",
        "id": amazon_asin,
        "price": amazon_details.get("price"),
        "stock": amazon_details.get("is_in_stock"),
        "affiliate_link": build_affiliate_link(amazon_asin, domain)
    })

    # Walmart
    if walmart_details:
        merchants.append(walmart_details)

    # Best Buy
    if bestbuy_details:
        merchants.append(bestbuy_details)

    # Unified product entry
    product = build_product_entry(
        title=original_title,
        image=amazon_details.get("images")[0] if amazon_details.get("images") else None,
        merchants=merchants
    )

    return {"products": [product]}
