from .client import rainforest_request

def get_asin_from_title(title, domain="amazon.com"):
    params = {
        "type": "search",
        "amazon_domain": domain,
        "search_term": title
    }

    data = rainforest_request(params)
    results = data.get("search_results", [])

    if not results:
        return None

    return results[0].get("asin")
