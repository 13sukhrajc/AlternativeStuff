# pipeline/schema.py
#
# Defines the shape of all data objects flowing through the pipeline.
# All retailer modules should return dicts matching build_merchant_entry.


def build_merchant_entry(
    merchant: str,
    merchant_id: str,
    price: float,
    stock,
    affiliate_link: str,
    image: str = None
) -> dict:
    return {
        "merchant": merchant,
        "id": merchant_id,
        "price": price,
        "stock": stock,
        "affiliate_link": affiliate_link,
        "image": image
    }


def build_product_entry(
    title: str,
    image: str,
    merchants: list,
    tier: str = None,
    category: str = None
) -> dict:
    return {
        "title": title,
        "image": image,
        "tier": tier,
        "category": category,
        "merchants": merchants
    }


def build_response(query: str, category: str, products: list) -> dict:
    return {
        "query": query,
        "category": category,
        "products": products
    }
