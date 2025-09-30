# utils.py

import os
import requests

def get_api_data(train_number):
    api_key = os.getenv("API_KEY")
    api_url = os.getenv("API_URL")
    headers = {"Authorization": f"Bearer {api_key}"}
    
    try:
        response = requests.get(f"{api_url}?train_number={train_number}", headers=headers)
        response.raise_for_status()
        data = response.json()
        return data.get("data", [])
    except Exception as e:
        print(f"API error: {e}")
        return None
