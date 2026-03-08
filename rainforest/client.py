# rainforest/client.py
#
# Shared config for all Rainforest API requests.
# Sync client used only if needed outside the async pipeline.

import os
import requests
from dotenv import load_dotenv

load_dotenv()

BASE_URL = "https://api.rainforestapi.com/request"
API_KEY = os.getenv("RAINFOREST_API_KEY")


def rainforest_request(params: dict) -> dict:
    """Synchronous Rainforest request. Use only outside async context."""
    params["api_key"] = API_KEY
    response = requests.get(BASE_URL, params=params)
    response.raise_for_status()
    return response.json()
