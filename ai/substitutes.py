import os
import json
import re
import requests
from dotenv import load_dotenv

load_dotenv()

# ---------------------------------------------------------------------------
# Model configuration — set these in your .env file
#
# Best quality (searches web in real time):
#   MODEL_PROVIDER=perplexity
#   MODEL_NAME=sonar-pro
#
# Recommended (fast + cheap):
#   MODEL_PROVIDER=anthropic
#   MODEL_NAME=claude-haiku-4-5-20251001
#
# Best quality without web search:
#   MODEL_NAME=claude-sonnet-4-6
#
# OpenAI:
#   MODEL_PROVIDER=openai
#   MODEL_NAME=gpt-4o-mini
#
# Groq (free, weaker):
#   MODEL_PROVIDER=groq
#   MODEL_NAME=llama-3.3-70b-versatile
# ---------------------------------------------------------------------------

MODEL_PROVIDER = os.getenv("MODEL_PROVIDER", "perplexity")
MODEL_NAME     = os.getenv("MODEL_NAME", "sonar-pro")

GROQ_API_KEY        = os.getenv("GROQ_API_KEY")
OPENAI_API_KEY      = os.getenv("OPENAI_API_KEY")
ANTHROPIC_API_KEY   = os.getenv("ANTHROPIC_API_KEY")
PERPLEXITY_API_KEY  = os.getenv("PERPLEXITY_API_KEY")

GROQ_URL        = "https://api.groq.com/openai/v1/chat/completions"
OPENAI_URL      = "https://api.openai.com/v1/chat/completions"
ANTHROPIC_URL   = "https://api.anthropic.com/v1/messages"
PERPLEXITY_URL  = "https://api.perplexity.ai/chat/completions"


def extract_json(text: str) -> dict:
    """Strips markdown fences and extracts the first JSON object found."""
    text = text.replace("```json", "").replace("```", "").strip()
    match = re.search(r"\{.*\}", text, re.DOTALL)
    if not match:
        raise ValueError("No JSON object found in model output")
    return json.loads(match.group(0))


def _call_model(prompt: str) -> str:
    """Routes to the correct AI provider. Returns raw text response."""

    if MODEL_PROVIDER == "perplexity":
        if not PERPLEXITY_API_KEY:
            raise ValueError("PERPLEXITY_API_KEY is not set in your .env file")
        payload = {
            "model": MODEL_NAME,
            "messages": [
                {
                    "role": "system",
                    "content": (
                        "You are a product research assistant. You search the web to find "
                        "real products currently listed on Amazon. Only suggest products you "
                        "can confirm exist and are actively sold on Amazon right now. "
                        "Return only valid JSON, no explanation, no markdown."
                    )
                },
                {"role": "user", "content": prompt}
            ],
            "max_tokens": 2500,
            "temperature": 0.1,
            "return_citations": False,
        }
        headers = {
            "Authorization": f"Bearer {PERPLEXITY_API_KEY}",
            "Content-Type": "application/json"
        }
        r = requests.post(PERPLEXITY_URL, json=payload, headers=headers)
        r.raise_for_status()
        return r.json()["choices"][0]["message"]["content"]

    elif MODEL_PROVIDER == "anthropic":
        if not ANTHROPIC_API_KEY:
            raise ValueError("ANTHROPIC_API_KEY is not set in your .env file")
        payload = {
            "model": MODEL_NAME,
            "max_tokens": 2500,
            "messages": [{"role": "user", "content": prompt}]
        }
        headers = {
            "x-api-key": ANTHROPIC_API_KEY,
            "anthropic-version": "2023-06-01",
            "Content-Type": "application/json"
        }
        r = requests.post(ANTHROPIC_URL, json=payload, headers=headers)
        r.raise_for_status()
        return r.json()["content"][0]["text"]

    elif MODEL_PROVIDER == "openai":
        if not OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY is not set in your .env file")
        payload = {
            "model": MODEL_NAME,
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": 2500,
            "temperature": 0.1
        }
        headers = {
            "Authorization": f"Bearer {OPENAI_API_KEY}",
            "Content-Type": "application/json"
        }
        r = requests.post(OPENAI_URL, json=payload, headers=headers)
        r.raise_for_status()
        return r.json()["choices"][0]["message"]["content"]

    elif MODEL_PROVIDER == "groq":
        if not GROQ_API_KEY:
            raise ValueError("GROQ_API_KEY is not set in your .env file")
        payload = {
            "model": MODEL_NAME,
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": 2500,
            "temperature": 0.1
        }
        headers = {
            "Authorization": f"Bearer {GROQ_API_KEY}",
            "Content-Type": "application/json"
        }
        r = requests.post(GROQ_URL, json=payload, headers=headers)
        r.raise_for_status()
        return r.json()["choices"][0]["message"]["content"]

    else:
        raise ValueError(
            f"Unknown MODEL_PROVIDER: '{MODEL_PROVIDER}'. "
            f"Valid options: perplexity, anthropic, openai, groq"
        )


def _validate_substitutes(substitutes: list, original_title: str) -> list:
    """
    Drops hallucinated or near-duplicate substitutes before they hit Rainforest.
    - Drops titles under 5 characters
    - Drops near-duplicates of the original (>70% word overlap)
    - Drops duplicates within the returned list
    """
    seen = set()
    clean = []
    original_words = set(original_title.lower().split())

    for sub in substitutes:
        title = sub.get("title", "").strip()

        if len(title) < 5:
            print(f"[Validate] Dropped (too short): '{title}'")
            continue

        title_words = set(title.lower().split())
        if len(original_words) > 0:
            overlap = len(title_words & original_words) / len(original_words)
            if overlap > 0.7:
                print(f"[Validate] Dropped (too similar to original): '{title}'")
                continue

        title_key = title.lower().strip()
        if title_key in seen:
            print(f"[Validate] Dropped (duplicate): '{title}'")
            continue

        seen.add(title_key)
        clean.append(sub)

    return clean


def _build_tier_instructions(tier_counts: dict) -> str:
    """
    Builds the tier breakdown section of the prompt.
    Note: tiers here are just to get diverse product suggestions —
    actual tier assignment happens later in enhancer_async based on real prices.
    """
    labels = {
        "budget": (
            "lower-cost option(s) — same product type, prioritizes affordability over features. "
            "Fewer buttons, basic sensor, no frills. Good for casual users."
        ),
        "mid": (
            "direct competitor(s) — similar price and feature set, different brand. "
            "Comparable sensor quality, similar weight, similar programmability. "
            "The most direct like-for-like alternative."
        ),
        "premium": (
            "higher-end option(s) — better in every measurable way than the original. "
            "Superior sensor (higher DPI, better tracking), better build quality, "
            "more programmable buttons, better software ecosystem, longer battery life. "
            "From a well-known reputable brand."
        ),
        "next-gen": (
            "cutting-edge option(s) released in the last 1-2 years — represents the current "
            "state of the art in this product category. Latest sensor technology, newest features, "
            "most advanced specs available right now. Must be currently sold on Amazon."
        ),
    }
    lines = []
    for tier, count in tier_counts.items():
        if count > 0:
            lines.append(f"- {count} {labels.get(tier, tier)}")
    return "\n".join(lines)


def _build_tier_json_template(tier_counts: dict) -> str:
    entries = []
    for tier, count in tier_counts.items():
        for _ in range(count):
            entries.append(f'    {{"title": "Brand Model Name", "tier": "{tier}"}}')
    return "[\n" + ",\n".join(entries) + "\n  ]"


def generate_substitutes(
    query: str,
    asin_hint: str = None,
    tier_counts: dict = None,
    budget_range: tuple = None
) -> dict:
    """
    Calls the configured AI model to identify a product and generate substitutes.

    Args:
        query:        Amazon URL or keyword search term
        asin_hint:    ASIN extracted from URL (passed through to skip Amazon search later)
        tier_counts:  How many of each tier to return.
                      Default: {"budget": 1, "mid": 2, "premium": 1, "next-gen": 1}
        budget_range: Optional (min, max) price filter e.g. (20, 150)

    Note: The AI's tier labels are used only as a guide to get variety.
    Real tier assignment is done by _retier_by_price() in enhancer_async.py
    after actual prices are fetched from Rainforest.
    """
    if tier_counts is None:
        tier_counts = {"budget": 1, "mid": 2, "premium": 1, "next-gen": 1}

    total_substitutes = sum(tier_counts.values())

    if query.startswith("http"):
        product_context = (
            f"The user provided this Amazon product URL: {query}\n"
            f"Extract the exact product name from the URL path and use it.\n"
            f"IMPORTANT: Read the FULL product name carefully and identify the SPECIFIC product type.\n"
            f"Examples of correct interpretation:\n"
            f"- 'YMDK-Keyset-Profile-Mechanical-Keyboard' → product type is KEYCAP SET, not a keyboard\n"
            f"- 'Razer-DeathAdder-Gaming-Mouse-Pad' → product type is MOUSE PAD, not a mouse\n"
            f"- 'Corsair-Vengeance-RAM-DDR5' → product type is RAM/memory, not a full computer\n"
            f"- 'Elgato-Stream-Deck-MK2' → product type is STREAM DECK controller, not a keyboard\n"
            f"Suggest alternatives of that EXACT same specific product type only."
        )
    else:
        product_context = (
            f'The user is searching for: "{query}"\n'
            f"Identify the specific product type and its key features/specs. "
            f"Use those features as the baseline when suggesting alternatives at each tier. "
            f"For example if the original has a high-end sensor, programmable buttons, and lightweight design — "
            f"budget alternatives may sacrifice some of these, while premium alternatives improve on all of them."
        )

    budget_instruction = ""
    if budget_range:
        min_price, max_price = budget_range
        budget_instruction = (
            f"\nBUDGET CONSTRAINT: Every suggested product MUST be priced "
            f"between ${min_price} and ${max_price}. Exclude anything outside this range."
        )

    tier_instructions = _build_tier_instructions(tier_counts)
    tier_template = _build_tier_json_template(tier_counts)

    prompt = f"""You are a product research assistant with expert knowledge of consumer electronics, gaming hardware, and retail products.

{product_context}

Tasks:
1. Identify the exact product name AND specific product type from the URL or query.
2. Classify it into ONE of these categories exactly as written:
   technology, gaming, appliances, furniture, food, grocery, clothing, toys, books, music, sports, health, beauty, automotive, office
3. Suggest exactly {total_substitutes} real alternative products of the SAME specific product type as the original.{budget_instruction}
   Example: if the original is a keycap set → suggest ONLY other keycap sets.
   Example: if the original is a mouse pad → suggest ONLY mouse pads.
   Example: if the original is a webcam → suggest ONLY webcams.

Variety breakdown (suggest a mix across this range):
{tier_instructions}

CRITICAL RULES:
- Every product must be a DIFFERENT product from the original. Do NOT suggest variants or next-model-number versions of the same product line.
  BAD example: original is "Corsair Vengeance a8200" → do NOT suggest "Corsair Vengeance a8300"
- Use the EXACT official product name including specific model number as sold on Amazon.
- Only suggest products actively sold on Amazon in 2025. Do NOT invent products.
- If you are not 100% certain a product exists on Amazon, do not include it.
- Prefer well-known products from reputable brands with strong Amazon listings.
- No generic descriptions, no placeholder names, no made-up model numbers.
- For the cutting-edge slot: only suggest products released in the last 1-2 years (current year or previous year). If none exist, use a well-known premium alternative instead.

Return ONLY valid JSON, no explanation, no markdown, no extra text:

{{
  "resolved_title": "Exact Product Name Here",
  "category": "technology",
  "substitutes": {tier_template}
}}"""

    print(f"[AI] Using {MODEL_PROVIDER} / {MODEL_NAME}")
    reply = _call_model(prompt)
    data = extract_json(reply)

    resolved_title = data.get("resolved_title", query)
    category = data.get("category", "unknown").lower().strip()
    raw_substitutes = data.get("substitutes", [])

    validated = _validate_substitutes(raw_substitutes, resolved_title)
    dropped = len(raw_substitutes) - len(validated)
    if dropped > 0:
        print(f"[Substitutes] {dropped} substitute(s) dropped by validator")

    return {
        "original_product": {
            "title": resolved_title,
            "raw_query": query,
            "asin_hint": asin_hint,
            "category": category,
        },
        "substitutes": validated
    }