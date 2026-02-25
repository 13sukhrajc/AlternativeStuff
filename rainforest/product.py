from .client import rainforest_request

def get_product_details(asin, domain="amazon.com"):
    params = {
        "type": "product",
        "amazon_domain": domain,
        "asin": asin
    }

    data = rainforest_request(params)
    product = data.get("product", {})

    return {
        "title": product.get("title"),
        "price": product.get("buybox_winner", {}).get("price", {}).get("value"),
        "stock": product.get("buybox_winner", {}).get("availability", {}).get("raw"),
        "images": product.get("images", [])
    }
