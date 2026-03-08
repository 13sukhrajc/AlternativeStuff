# pipeline/enhancer_async.py
#
# Orchestrates all retailer lookups concurrently.
# Routes to only the relevant retailers based on product category.
# Each retailer fetch is independent — one failure won't block others.
#
# After all prices are fetched:
#   1. Drops products with no price (group buys, out of stock listings)
#   2. Re-tiers products based on actual prices vs the original
#   3. Trims results down to the counts the user actually requested
#      If a tier is overfull, extras are redistributed to empty tiers
#      instead of being dropped.

import asyncio
import httpx

from rainforest.search_async import get_asin_from_title_async
from rainforest.product_async import get_product_details_async
from walmart.search_async import walmart_search_async
from walmart.product_async import walmart_product_async
from bestbuy.search_async import bestbuy_search_async
from bestbuy.product_async import bestbuy_product_async

from pipeline.schema import build_product_entry, build_response
from pipeline.routing import get_retailers_for_category
from utils.affiliate import build_affiliate_link


# ---------------------------------------------------------------------------
# Per-retailer fetch functions
# ---------------------------------------------------------------------------

async def fetch_amazon(client, title, domain, asin_hint=None):
    try:
        asin = asin_hint or await get_asin_from_title_async(client, title, domain)
        if not asin:
            return None
        details = await get_product_details_async(client, asin, domain)
        return {
            "merchant": "Amazon",
            "id": asin,
            "price": details.get("price"),
            "stock": details.get("is_in_stock"),
            "image": (details.get("images") or [None])[0],
            "affiliate_link": build_affiliate_link("amazon", asin, domain)
        }
    except Exception as e:
        print(f"[Amazon] Failed for '{title}': {e}")
        return None


async def fetch_walmart(client, title):
    try:
        item_id = await walmart_search_async(client, title)
        if not item_id:
            return None
        details = await walmart_product_async(client, item_id)
        if not details:
            return None
        details["affiliate_link"] = build_affiliate_link("walmart", str(item_id))
        return details
    except Exception as e:
        print(f"[Walmart] Failed for '{title}': {e}")
        return None


async def fetch_bestbuy(client, title):
    try:
        sku = await bestbuy_search_async(client, title)
        if not sku:
            return None
        details = await bestbuy_product_async(client, sku)
        if not details:
            return None
        details["affiliate_link"] = build_affiliate_link("bestbuy", str(sku))
        return details
    except Exception as e:
        print(f"[BestBuy] Failed for '{title}': {e}")
        return None


# ---------------------------------------------------------------------------
# Re-tiering by actual price
# ---------------------------------------------------------------------------

def _retier_by_price(products: list, original_price: float, category: str = "") -> list:
    """
    Re-assigns tiers based on actual fetched prices vs the original product price.

    Standard thresholds (ratio = product_price / original_price):
      < 0.75    → budget
      0.75–1.35 → mid
      1.35–2.8  → premium
      > 2.8     → next-gen

    Books thresholds (wider, single books vs box sets vary a lot):
      < 0.25    → budget
      0.25–0.85 → mid
      0.85–1.8  → premium
      > 1.8     → next-gen

    Gaming/music/toys thresholds (prices vary wildly within same category):
      < 0.35    → budget
      0.35–0.85 → mid
      0.85–1.5  → premium
      > 1.5     → next-gen

    Products with no price keep their AI-assigned tier.
    The 'original' product is never re-tiered.
    """
    if not original_price or original_price <= 0:
        print("[Retier] Skipped — no original price available")
        return products

    print(f"[Retier] Original price: ${original_price:.2f}")

    for p in products:
        if p.get("tier") == "original":
            continue

        merchant = (p.get("merchants") or [{}])[0]
        price = merchant.get("price")

        if price is None:
            print(f"[Retier] No price for '{p.get('title', '?')[:40]}' — keeping AI tier '{p.get('tier')}'")
            continue

        ratio = price / original_price
        old_tier = p.get("tier")

        if category == "books":
            if ratio < 0.25:
                new_tier = "budget"
            elif ratio <= 0.85:
                new_tier = "mid"
            elif ratio <= 1.8:
                new_tier = "premium"
            else:
                new_tier = "next-gen"
        elif category in ("gaming", "music", "toys"):
            if ratio < 0.35:
                new_tier = "budget"
            elif ratio <= 0.85:
                new_tier = "mid"
            elif ratio <= 1.5:
                new_tier = "premium"
            else:
                new_tier = "next-gen"
        else:
            if ratio < 0.75:
                new_tier = "budget"
            elif ratio <= 1.35:
                new_tier = "mid"
            elif ratio <= 2.8:
                new_tier = "premium"
            else:
                new_tier = "next-gen"

        p["tier"] = new_tier

        if old_tier != new_tier:
            print(
                f"[Retier] '{p.get('title', '?')[:40]}' "
                f"${price:.2f} (ratio {ratio:.2f}x) {old_tier} → {new_tier}"
            )

    return products


# ---------------------------------------------------------------------------
# Trim to requested counts — redistribute extras to empty tiers
# ---------------------------------------------------------------------------

TIER_ORDER = ["budget", "mid", "premium", "next-gen"]

def _trim_to_counts(products: list, requested_counts: dict) -> list:
    """
    After re-tiering, some tiers may have more products than requested and
    some may be empty. Instead of dropping extras, redistribute them to
    fill empty tiers so the user always sees a full set of results.

    Strategy:
    1. Fill each tier up to its requested count
    2. Collect overflow from overfull tiers
    3. Redistribute overflow into tiers that are still underfull
    'original' is always kept.
    """
    original = [p for p in products if p.get("tier") == "original"]
    substitutes = [p for p in products if p.get("tier") != "original"]

    # Group substitutes by tier
    by_tier = {tier: [] for tier in TIER_ORDER}
    for p in substitutes:
        tier = p.get("tier")
        if tier in by_tier:
            by_tier[tier].append(p)

    kept_by_tier = {tier: [] for tier in TIER_ORDER}
    overflow = []

    # First pass — fill each tier up to requested count, collect overflow
    for tier in TIER_ORDER:
        limit = requested_counts.get(tier, 0)
        candidates = by_tier[tier]
        kept_by_tier[tier] = candidates[:limit]
        overflow.extend(candidates[limit:])

    # Second pass — redistribute overflow into underfull tiers
    for tier in TIER_ORDER:
        limit = requested_counts.get(tier, 0)
        needed = limit - len(kept_by_tier[tier])
        if needed > 0 and overflow:
            filling = overflow[:needed]
            for p in filling:
                old_tier = p.get("tier")
                p["tier"] = tier
                print(f"[Redistribute] '{p.get('title', '?')[:40]}' {old_tier} → {tier} (filling empty slot)")
            kept_by_tier[tier].extend(filling)
            overflow = overflow[needed:]

    # Reassemble in tier order
    result = original[:]
    for tier in TIER_ORDER:
        result.extend(kept_by_tier[tier])

    return result


# ---------------------------------------------------------------------------
# Core enhancer
# ---------------------------------------------------------------------------

async def fetch_product_for_retailers(client, title, domain, active_retailers, asin_hint=None):
    """
    Fires all active retailer lookups concurrently for a single product title.
    Returns list of merchant dicts (None results are filtered out).
    """
    tasks = []
    for retailer in active_retailers:
        if retailer == "amazon":
            tasks.append(fetch_amazon(client, title, domain, asin_hint=asin_hint))
        elif retailer == "walmart":
            tasks.append(fetch_walmart(client, title))
        elif retailer == "bestbuy":
            tasks.append(fetch_bestbuy(client, title))

    results = await asyncio.gather(*tasks)
    return [r for r in results if r is not None]


async def enhance_substitutes_async(
    data: dict,
    domain: str = "amazon.com",
    original_asin: str = None,
    requested_counts: dict = None
) -> dict:
    """
    Args:
        data:             Output from generate_substitutes() — includes original
                          product info and AI-suggested substitute titles.
        domain:           Amazon domain to search (amazon.ca, amazon.com, etc.)
        original_asin:    ASIN from the original URL if available — skips search step.
        requested_counts: The tier counts the user actually wants in the final result.
                          Used for trimming after re-tiering. If None, no trimming.
    """
    original = data["original_product"]
    original_title = original["title"]
    category = original.get("category", "unknown")
    raw_query = original.get("raw_query", original_title)
    substitutes = data.get("substitutes", [])

    active_retailers = get_retailers_for_category(category)
    print(f"[Routing] Category: '{category}' → Retailers: {active_retailers}")
    print(f"[Enhancer] Fetching {len(substitutes)} substitute candidates...")

    async with httpx.AsyncClient(
        timeout=httpx.Timeout(connect=5.0, read=15.0, write=5.0, pool=5.0)
    ) as client:

        # Build all tasks upfront — original + all substitutes — fire all concurrently
        all_tasks = []

        all_tasks.append(
            fetch_product_for_retailers(
                client, original_title, domain, active_retailers,
                asin_hint=original_asin
            )
        )

        for sub in substitutes:
            all_tasks.append(
                fetch_product_for_retailers(
                    client, sub["title"], domain, active_retailers,
                    asin_hint=None
                )
            )

        all_results = await asyncio.gather(*all_tasks)

    # ── Build product entries ──
    products = []

    # Original product
    original_merchants = all_results[0]
    if original_merchants:
        best_image = next((m.get("image") for m in original_merchants if m.get("image")), None)
        products.append(
            build_product_entry(
                title=original_title,
                image=best_image,
                merchants=original_merchants,
                tier="original",
                category=category
            )
        )

    # Substitutes — skip any with no retailer results or no price
    for i, sub in enumerate(substitutes):
        merchants = all_results[i + 1]

        if not merchants:
            print(f"[Skip] No retailer results for: '{sub['title']}'")
            continue

        # Drop products where no retailer returned a price
        has_price = any(m.get("price") is not None for m in merchants)
        if not has_price:
            print(f"[Skip] No price found for: '{sub['title']}' — likely out of stock or group buy")
            continue

        best_image = next((m.get("image") for m in merchants if m.get("image")), None)
        products.append(
            build_product_entry(
                title=sub["title"],
                image=best_image,
                merchants=merchants,
                tier=sub.get("tier"),
                category=category
            )
        )

    # ── Re-tier based on actual prices ──
    original_price = None
    for p in products:
        if p.get("tier") == "original":
            merchant = (p.get("merchants") or [{}])[0]
            original_price = merchant.get("price")
            break

    products = _retier_by_price(products, original_price, category)

    # ── Trim/redistribute to what the user actually requested ──
    if requested_counts:
        products = _trim_to_counts(products, requested_counts)

    return build_response(
        query=raw_query,
        category=category,
        products=products
    )