import os
import requests
from dotenv import load_dotenv

load_dotenv()

BASE_URL = "https://api.rainforestapi.com/request"
API_KEY = os.getenv("RAINFOREST_API_KEY")


def rainforest_request(params):
    params["api_key"] = API_KEY
    response = requests.get(BASE_URL, params=params)
    response.raise_for_status()
    return response.json()
