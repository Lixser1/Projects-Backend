import aiohttp
import os
from dotenv import load_dotenv

load_dotenv()

API_URL = f"http://{os.getenv('API_HOST', '127.0.0.1')}:{os.getenv('API_PORT', '8000')}"
API_KEY = os.getenv("API_KEY", "my_secret_api_key_12345")


async def analyze_text_via_api(text: str, mode: str) -> dict:
    url = f"{API_URL}/analyze"
    headers = {
        "X-API-Key": API_KEY,
        "Content-Type": "application/json"
    }
    payload = {
        "text": text,
        "mode": mode
    }
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=payload, headers=headers) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    error_text = await response.text()
                    raise Exception(f"API вернул ошибку {response.status}: {error_text}")
    except Exception as e:
        raise Exception(f"Ошибка при обращении к API: {str(e)}")