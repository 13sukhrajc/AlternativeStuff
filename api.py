# api.py
# Run with: python -m uvicorn api:app --reload

import re
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
# Add new regions here when expanding internationally
# ---------------------------------------------------------------------------
REGION_DOMAINS = {
    "CA": "amazon.ca",
    "US": "amazon.com",
    # Future:
    # "UK": "amazon.co.uk",
    # "DE": "amazon.de",
    # "AU": "amazon.com.au",
    # "JP": "amazon.co.jp",
    # "FR": "amazon.fr",
    # "IT": "amazon.it",
    # "ES": "amazon.es",
    # "MX": "amazon.com.mx",
    # "IN": "amazon.in",
}

# How many extra substitutes to request from the AI per slot, to account
# for products that come back with no price (group buys, out of stock, etc.)
# e.g. user wants 1 budget → AI is asked for 2 budget candidates
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


def extract_asin(query: str):
    match = re.search(r'/dp/([A-Z0-9]{10})', query)
    return match.group(1) if match else None


@app.post("/search")
async def search(req: SearchRequest):
    total = req.count_budget + req.count_mid + req.count_premium + req.count_next_gen
    if total == 0:
        raise HTTPException(status_code=400, detail="Select at least 1 substitute")
    if total > 15:
        raise HTTPException(status_code=400, detail="Maximum 15 substitutes total")

    region = req.region.upper()
    domain = REGION_DOMAINS.get(region, "amazon.com")
    asin_hint = extract_asin(req.query)

    # What the user actually wants — used for trimming after fetch
    requested_counts = {
        "budget":   req.count_budget,
        "mid":      req.count_mid,
        "premium":  req.count_premium,
        "next-gen": req.count_next_gen,
    }

    # Ask the AI for more candidates than needed so dropouts (no price,
    # out of stock, group buys) don't leave the user with empty slots
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
        # Generate substitutes with padded counts
        base_data = generate_substitutes(
            req.query,
            asin_hint=asin_hint,
            tier_counts=padded_counts,
            budget_range=budget_range
        )

        # Fetch real prices + re-tier + trim to requested counts
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