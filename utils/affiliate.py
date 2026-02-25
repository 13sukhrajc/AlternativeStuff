import os
from dotenv import load_dotenv

load_dotenv()

TAG = os.getenv("AMAZON_PARTNER_TAG_USA")


def build_affiliate_link(asin, domain="www.amazon.com"):
    return f"https://{domain}/dp/{asin}/?tag={TAG}"
