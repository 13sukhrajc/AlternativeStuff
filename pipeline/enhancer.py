from rainforest.search import get_asin_from_title
from rainforest.product import get_product_details
from utils.affiliate import build_affiliate_link


def enhance_substitutes(data):
    """
    Enhances:
    - original product
    - substitutes
    with ASIN, price, and affiliate link
    """

    original_title = data["original_product"]["title"]

    # --- ORIGINAL PRODUCT ---
    original_asin = get_asin_from_title(original_title)
    original_details = get_product_details(original_asin) if original_asin else {}

    enhanced = {
        "original_product": {
            "title": original_title,
            "asin": original_asin,
            "price": original_details.get("price"),
            "affiliate_link": build_affiliate_link(original_asin) if original_asin else None
        },
        "substitutes": []
    }

    # --- SUBSTITUTES ---
    for item in data["substitutes"]:
        title = item["title"]

        asin = get_asin_from_title(title)
        details = get_product_details(asin) if asin else {}

        enhanced["substitutes"].append({
            "title": title,
            "asin": asin,
            "price": details.get("price"),
            "affiliate_link": build_affiliate_link(asin) if asin else None
        })

    return enhanced
