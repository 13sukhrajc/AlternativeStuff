import os
import json
import re
import requests
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("GROQ_API_KEY")
API_URL = "https://api.groq.com/openai/v1/chat/completions"


def extract_json(text: str):
    # Remove code fences if present
    text = text.replace("```json", "").replace("```", "").strip()

    # Extract the first {...} block
    match = re.search(r"\{.*\}", text, re.DOTALL)
    if not match:
        raise ValueError("No JSON object found in model output")
    return json.loads(match.group(0))


def generate_substitutes(query):
    """
    Uses Groq AI (llama-3.1-8b-instant) to:
    - take a query (keyword or URL)
    - find similar products
    - return ONLY the titles of substitutes
    """

    prompt = f"""
    The user is searching for: "{query}"

    Generate 5 alternative or similar products.
    These alternatives should include
    - if technological current generation devices alongside others
    - If food things that are similar
    - recently released models or one prior generation model nothing further
    - upcoming or next-gen versions if widely known
    - competing brands in the same category

    Return ONLY valid JSON in this exact format:

    {{
      "substitutes": [
        {{"title": "Product 1"}},
        {{"title": "Product 2"}},
        {{"title": "Product 3"}},
        {{"title": "Product 4"}},
        {{"title": "Product 5"}}
      ]
    }}

    RULES:
    - Only output JSON.
    - No explanations.
    - No commentary.
    - No URLs.
    - Titles must be real products.
    """

    payload = {
        "model": "llama-3.1-8b-instant",
        "messages": [
            {"role": "user", "content": prompt}
        ],
        "max_tokens": 500
    }

    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

    response = requests.post(API_URL, json=payload, headers=headers)
    response.raise_for_status()

    reply = response.json()["choices"][0]["message"]["content"]

    data = extract_json(reply)

    return {
        "original_product": {
            "title": query,
            "category": "Unknown",
            "short_description": "Generated product description placeholder."
        },
        "substitutes": data["substitutes"]
    }
