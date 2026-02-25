import asyncio
import httpx
from rainforest.search_async import get_asin_from_title_async
from rainforest.product_async import get_product_details_async
from utils.affiliate import build_affiliate_link


async def enhance_substitutes_async(data):
    original_title = data["original_product"]["title"]

    async with httpx.AsyncClient(timeout=20) as client:

        # --- ORIGINAL PRODUCT ---
        original_asin_task = get_asin_from_title_async(client, original_title)

        # substitute ASIN tasks
        asin_tasks = [
            get_asin_from_title_async(client, item["title"])
            for item in data["substitutes"]
        ]

        # run all ASIN lookups in parallel
        original_asin, *substitute_asins = await asyncio.gather(
            original_asin_task, *asin_tasks
        )

        # product detail tasks
        detail_tasks = [
            get_product_details_async(client, asin)
            for asin in [original_asin] + substitute_asins
        ]

        details = await asyncio.gather(*detail_tasks)

    original_details = details[0]
    substitute_details = details[1:]

    return {
        "original_product": {
            "title": original_title,
            "asin": original_asin,
            "price": original_details.get("price"),
            "affiliate_link": build_affiliate_link(original_asin)
        },
        "substitutes": [
            {
                "title": item["title"],
                "asin": asin,
                "price": detail.get("price"),
                "affiliate_link": build_affiliate_link(asin)
            }
            for item, asin, detail in zip(
                data["substitutes"], substitute_asins, substitute_details
            )
        ]
    }
