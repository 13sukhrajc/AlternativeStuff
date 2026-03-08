# api.py
# Run with: python -m uvicorn api:app --reload

import re
import requests
from urllib.parse import urlparse
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional

from ai.substitutes import generate_substitutes
from pipeline.enhancer_async import enhance_substitutes_async

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------------------------------
# Region → Amazon domain mapping
# ---------------------------------------------------------------------------
REGION_DOMAINS = {
    "CA": "amazon.ca",
    "US": "amazon.com",
    # Future:
    # "UK": "amazon.co.uk",
    # "DE": "amazon.de",
    # "AU": "amazon.com.au",
    # "JP": "amazon.co.jp",
}

# How many extra substitutes to request from the AI per slot
PADDING_MULTIPLIER = 2


class SearchRequest(BaseModel):
    query: str
    region: str = "CA"
    budget_min: Optional[float] = None
    budget_max: Optional[float] = None
    count_budget: int = 1
    count_mid: int = 2
    count_premium: int = 1
    count_next_gen: int = 1


def resolve_url(url: str) -> str:
    """Follows redirects on shortened URLs like amzn.to to get the full URL."""
    try:
        r = requests.head(url, allow_redirects=True, timeout=5)
        return r.url
    except Exception:
        return url


def extract_asin(url: str) -> Optional[str]:
    """Extracts ASIN from a full Amazon URL."""
    match = re.search(r'/dp/([A-Z0-9]{10})', url)
    return match.group(1) if match else None


def extract_name_from_url(url: str) -> str:
    """
    Extracts a clean product name from an Amazon URL path.
    e.g. https://amazon.ca/YMDK-Keyset-Profile-Keyboard/dp/B079...
         → "YMDK Keyset Profile Keyboard"
    """
    try:
        path = urlparse(url).path
        parts = path.split("/")
        for i, part in enumerate(parts):
            if part == "dp":
                # Product name slug is the segment before /dp/
                name_slug = parts[i - 1] if i > 0 else ""
                if name_slug:
                    return name_slug.replace("-", " ").strip()
    except Exception:
        pass
    return url


@app.post("/search")
async def search(req: SearchRequest):
    total = req.count_budget + req.count_mid + req.count_premium + req.count_next_gen
    if total == 0:
        raise HTTPException(status_code=400, detail="Select at least 1 substitute")
    if total > 15:
        raise HTTPException(status_code=400, detail="Maximum 15 substitutes total")

    region = req.region.upper()
    domain = REGION_DOMAINS.get(region, "amazon.com")
    query = req.query

    # Resolve shortened URLs (amzn.to etc.) to full URLs first
    if "amzn.to" in query or "amzn.com/d" in query:
        print(f"[URL] Resolving shortened URL: {query}")
        query = resolve_url(query)
        print(f"[URL] Resolved to: {query}")

    # Extract ASIN from URL before converting to name
    asin_hint = extract_asin(query) if query.startswith("http") else None

    # Convert URL to clean product name for the AI prompt
    # Makes URL input behave exactly like a keyword search
    if query.startswith("http"):
        product_name = extract_name_from_url(query)
        print(f"[URL] Extracted product name: '{product_name}'")
        query = product_name

    # What the user actually wants — used for trimming after fetch
    requested_counts = {
        "budget":   req.count_budget,
        "mid":      req.count_mid,
        "premium":  req.count_premium,
        "next-gen": req.count_next_gen,
    }

    # Ask AI for more candidates than needed so dropouts don't
    # leave the user with empty slots
    padded_counts = {
        k: v * PADDING_MULTIPLIER for k, v in requested_counts.items() if v > 0
    }

    budget_range = None
    if req.budget_min is not None or req.budget_max is not None:
        budget_range = (
            req.budget_min if req.budget_min is not None else 0,
            req.budget_max if req.budget_max is not None else 999999
        )

    try:
        base_data = generate_substitutes(
            query,
            asin_hint=asin_hint,
            tier_counts=padded_counts,
            budget_range=budget_range
        )

        result = await enhance_substitutes_async(
            base_data,
            domain=domain,
            original_asin=asin_hint,
            requested_counts=requested_counts
        )

        return result

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/health")
async def health():
    return {"status": "ok"}