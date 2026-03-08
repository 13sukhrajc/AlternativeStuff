import asyncio
import json
import re

from ai.substitutes import generate_substitutes
from pipeline.enhancer_async import enhance_substitutes_async


def extract_asin_and_domain(query: str):
    asin_match = re.search(r'/dp/([A-Z0-9]{10})', query)
    if asin_match:
        asin = asin_match.group(1)
        domain = "amazon.ca" if "amazon.ca" in query else "amazon.com"
        return asin, domain
    return None, "amazon.com"


def run(query: str, tier_counts: dict = None, budget_range: tuple = None):
    """
    Args:
        query:        Amazon URL or keyword search
        tier_counts:  How many of each tier to return.
                      Keys: "budget", "mid", "premium", "next-gen"
                      Example: {"budget": 2, "mid": 2, "premium": 1, "next-gen": 0}
                      Default: {"budget": 1, "mid": 2, "premium": 1, "next-gen": 1}
        budget_range: (min_price, max_price) tuple. All results filtered to this range.
                      Example: (20, 100) for $20-$100 products only.
                      Default: None (no filter)
    """
    asin_hint, domain = extract_asin_and_domain(query)

    if asin_hint:
        print(f"[main] Domain: {domain} | ASIN: {asin_hint}")
    else:
        print(f"[main] Keyword search on {domain}")

    if budget_range:
        print(f"[main] Budget filter: ${budget_range[0]} - ${budget_range[1]}")

    base_data = generate_substitutes(
        query,
        asin_hint=asin_hint,
        tier_counts=tier_counts,
        budget_range=budget_range
    )

    final_output = asyncio.run(
        enhance_substitutes_async(
            base_data,
            domain=domain,
            original_asin=asin_hint
        )
    )

    print(json.dumps(final_output, indent=4))


if __name__ == "__main__":

    # --- Example 1: Default (1 budget, 2 mid, 1 premium, 1 next-gen) ---
    run(
        "https://www.amazon.ca/Corsair-Vengeance-a8200-Gaming-Dominator/dp/B0FB9PBL4X/ref=mp_s_a_1_7?crid=36NZRUPGWYZ2N&dib=eyJ2IjoiMSJ9.60Cq7B6epq0sX5O0YSl6gpnHqHHnwauj-0_AjWOT5qkph4oUoXc8fZUs87FfEO_boJ6_xpoeAtBlyDknOYboulM2JllOrdkYjRYBWi846glCL88th7cu7ZFpsF9LA9knOJMjOEukG7h0DLhu2JyxBrEEiA9W0sr_maSwutNToD50Nr2PdKYrm1qFxxv3czXrWK4NxxmVSifUxo_a-gbRSA.GEAmBGQuLPxmXIw1Glazhjhst8ZJwNg2OO_r6vtoJ4I&dib_tag=se&keywords=5090+pc&qid=1772668743&sprefix=5090+%2Caps%2C188&sr=8-7",
        tier_counts={"budget":5, "mid": 10, "premium":10, "next-gen":0},
        budget_range=(10000, 13000),
    )

    # --- Example 2: Budget-focused, price capped at $80 CAD ---
    # run(
    #     "https://www.amazon.ca/ATTACK-SHARK-DPI-PAW3950-Lightweight-Programmable/dp/B0FMRZF662",
    #     tier_counts={"budget": 3, "mid": 2, "premium": 0, "next-gen": 0},
    #     budget_range=(0, 80)
    # )

    # --- Example 3: Premium-only, no budget limit ---
    # run(
    #     "gaming mouse",
    #     tier_counts={"budget": 0, "mid": 1, "premium": 3, "next-gen": 1},
    # )

    # --- Example 4: Keyword search with tight budget ---
    # run(
    #     "mechanical keyboard",
    #     tier_counts={"budget": 2, "mid": 3, "premium": 0, "next-gen": 0},
    #     budget_range=(30, 120)
    # )