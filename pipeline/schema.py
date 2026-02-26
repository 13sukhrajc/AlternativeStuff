def build_merchant_entry(
    merchant: str,
    merchant_id: str,
    price: float,
    stock,
    affiliate_link: str,
    image: str = None
):
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
    merchants: list
):
    return {
        "title": title,
        "image": image,
        "merchants": merchants
    }


def build_response(query: str, products: list):
    return {
        "query": query,
        "products": products
    }
