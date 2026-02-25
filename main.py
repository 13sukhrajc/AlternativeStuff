from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI
from pydantic import BaseModel
from typing import List
import os
import json

from groq import Groq

# -------------------------
# Groq Configuration
# -------------------------
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
if not GROQ_API_KEY:
    raise RuntimeError("Missing GROQ_API_KEY environment variable")

client = Groq(api_key=GROQ_API_KEY)

app = FastAPI()

# -------------------------
# Request Schemas
# -------------------------
class ProductRequest(BaseModel):
    product_url: str

class SubstituteResponse(BaseModel):
    original_product: dict
    substitutes: List[dict]

# -------------------------
# Groq Helper Functions
# -------------------------

async def call_groq_extract(url: str) -> dict:
    prompt = f"""
    Extract structured product data from this product page URL.

    Return ONLY valid JSON with:
    - title (string)
    - price (float)
    - category (string)
    - features (object)
    - short_description (string)

    URL: {url}
    """

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}]
    )

    text = response.choices[0].message.content.strip()

    if text.startswith("```"):
        text = text.strip("`").strip()

    try:
        data = json.loads(text)
        data["price"] = float(data["price"])
        return data
    except Exception:
        raise RuntimeError(f"Groq returned invalid JSON: {text}")


async def call_groq_substitutes(product_data: dict) -> List[dict]:
    prompt = f"""
    Recommend 3 cheaper alternative products for this item:

    {json.dumps(product_data, indent=2)}

    Return ONLY a JSON array of objects with:
    - title
    - price
    - url
    """

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}]
    )

    text = response.choices[0].message.content.strip()

    if text.startswith("```"):
        text = text.strip("`").strip()

    try:
        return json.loads(text)
    except Exception:
        return []

# -------------------------
# Endpoint
# -------------------------

@app.post("/find-substitute", response_model=SubstituteResponse)
async def find_substitute(req: ProductRequest):
    product_data = await call_groq_extract(req.product_url)
    substitutes = await call_groq_substitutes(product_data)

    return {
        "original_product": product_data,
        "substitutes": substitutes
    }
