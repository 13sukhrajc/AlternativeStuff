# pipeline/routing.py
#
# Single source of truth for which retailers to query per product category.
# To add a new retailer: add it to the relevant categories below, then
# create its search_async.py and product_async.py files.

ENABLE_WALMART = False
ENABLE_BESTBUY = False

RETAILER_MAP = {
    "technology":   ["amazon", "walmart", "bestbuy"],
    "gaming":       ["amazon", "walmart", "bestbuy"],
    "appliances":   ["amazon", "walmart", "bestbuy"],
    "office":       ["amazon", "walmart", "bestbuy"],
    "toys":         ["amazon", "walmart", "bestbuy"],
    "music":        ["amazon", "bestbuy"],
    "books":        ["amazon"],
    "food":         ["walmart"],
    "grocery":      ["walmart"],
    "furniture":    ["walmart", "amazon"],
    "clothing":     ["walmart", "amazon"],
    "sports":       ["amazon", "walmart"],
    "health":       ["amazon", "walmart"],
    "beauty":       ["amazon", "walmart"],
    "automotive":   ["amazon", "walmart"],
    "unknown":      ["amazon", "walmart", "bestbuy"],  # Fallback — try all
}

# Normalizes inconsistent LLM category outputs to the keys above
CATEGORY_ALIASES = {
    "electronics":      "technology",
    "computers":        "technology",
    "peripherals":      "technology",
    "mice":             "gaming",
    "keyboards":        "gaming",
    "headphones":       "technology",
    "audio":            "technology",
    "video games":      "gaming",
    "consoles":         "gaming",
    "game":             "gaming",
    "snacks":           "food",
    "beverages":        "food",
    "drinks":           "food",
    "produce":          "grocery",
    "pantry":           "grocery",
    "apparel":          "clothing",
    "shoes":            "clothing",
    "footwear":         "clothing",
    "home appliances":  "appliances",
    "kitchen":          "appliances",
}


def get_retailers_for_category(category: str) -> list[str]:
    normalized = category.lower().strip()
    resolved = CATEGORY_ALIASES.get(normalized, normalized)
    retailers = RETAILER_MAP.get(resolved, RETAILER_MAP["unknown"])

    if not ENABLE_WALMART:
        retailers = [r for r in retailers if r != "walmart"]
    if not ENABLE_BESTBUY:
        retailers = [r for r in retailers if r != "bestbuy"]

    return retailers
