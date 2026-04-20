import httpx
import logging
from config import API_URL, OPENROUTER_API_KEY, MODEL

async def analyze_with_ai(messages):
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": MODEL,
        "messages": messages,
        "max_tokens": 100
    }

    try:
        async with httpx.AsyncClient(timeout=15) as client:
            response = await client.post(API_URL, headers=headers, json=payload)
            logger = logging.getLogger(__name__)
            logger.info(f"AI status: {response.status_code}") # логирование

        if response.status_code == 402:
            return "⚠️ Лимит AI временно исчерпан. Попробуйте позже."

        if response.status_code != 200:
            return f"Ошибка {response.status_code}: {response.text}"

        try:
            data = response.json()
        except Exception:
            return "Ошибка: некорректный ответ от AI"

        if "choices" not in data or not data["choices"]:
            return "Ошибка: пустой ответ от AI"

        try:
            return data["choices"][0]["message"]["content"]
        except (KeyError, IndexError):
            return "Ошибка: неправильный формат ответа AI"

    except httpx.TimeoutException:
        return "⏳ AI долго отвечает, попробуйте позже"

    except httpx.RequestError as e:
        print("Request error:", e)
        return "Ошибка подключения к AI"