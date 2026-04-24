import httpx
import json
from config import API_URL, OPENROUTER_API_KEY, MODEL

async def stream_ai_response(messages):
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": MODEL,
        "messages": messages,
        "max_tokens": 200,
        "stream": True
    }

    async with httpx.AsyncClient(timeout=None) as client:
        async with client.stream("POST", API_URL, headers=headers, json=payload) as response:

            if response.status_code != 200:
                error_text = await response.aread()
                yield f"❌ Ошибка {response.status_code}: {error_text.decode()}"
                return

            async for line in response.aiter_lines():
                if not line or not line.startswith("data:"):
                    continue

                data_str = line.replace("data: ", "")

                if data_str == "[DONE]":
                    break

                try:
                    data = json.loads(data_str)
                    delta = data["choices"][0]["delta"].get("content")

                    if delta:
                        yield delta

                except Exception:
                    continue