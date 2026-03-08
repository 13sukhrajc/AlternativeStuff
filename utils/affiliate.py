# utils/affiliate.py
#
# All affiliate link construction lives here.
# Add new retailers by adding a new elif block and a corresponding .env key.

import os
from dotenv import load_dotenv

load_dotenv()

_TAGS = {
    "amazon.com": os.getenv("AMAZON_PARTNER_TAG_USA"),
    "amazon.ca":  os.getenv("AMAZON_PARTNER_TAG_CA"),
    "walmart":    os.getenv("WALMART_AFFILIATE_TAG"),
    "bestbuy":    os.getenv("BESTBUY_IMPACT_ID"),
}


def build_affiliate_link(merchant: str, item_id: str, domain: str = "amazon.com") -> str | None:
    """
    Builds a tracked affiliate link for the given merchant and item.

    Args:
        merchant:  "amazon" | "walmart" | "bestbuy"
        item_id:   ASIN for Amazon, item ID for Walmart, SKU for Best Buy
        domain:    Amazon domain — "amazon.com" or "amazon.ca" (ignored for other merchants)

    Returns:
        Affiliate URL string, or None if the tag is missing from .env
    """
    if merchant == "amazon":
        tag = _TAGS.get(domain, _TAGS["amazon.com"])
        if not tag:
            print(f"[Affiliate] Warning: No Amazon tag found for domain '{domain}'")
            return f"https://{domain}/dp/{item_id}/"  # Untracked fallback
        return f"https://{domain}/dp/{item_id}/?tag={tag}"

    elif merchant == "walmart":
        tag = _TAGS["walmart"]
        if not tag:
            print("[Affiliate] Warning: No Walmart affiliate tag in .env")
            return f"https://www.walmart.com/ip/{item_id}"
        return f"https://www.walmart.com/ip/{item_id}?affp1={tag}"

    elif merchant == "bestbuy":
        impact_id = _TAGS["bestbuy"]
        if not impact_id:
            print("[Affiliate] Warning: No Best Buy Impact ID in .env")
            return f"https://www.bestbuy.com/site/{item_id}.p?skuId={item_id}"
        return f"https://www.bestbuy.com/site/{item_id}.p?skuId={item_id}&ref={impact_id}"

    print(f"[Affiliate] Unknown merchant: '{merchant}'")
    return None
