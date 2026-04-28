import httpx
import json
import asyncio
from config import (
    OPENROUTER_API_URL, 
    OPENROUTER_API_KEY, 
    MODEL, 
    YANDEX_API_KEY, 
    YANDEX_FOLDER_ID, 
    YANDEX_API_URL)
from typing import AsyncGenerator, List, Dict

MAX_RETRIES = 2
MAX_TOKENS = 1200
FALLBACK_MODELS = ["openrouter", "yandex"]

async def openrouter_stream(messages, max_tokens) -> AsyncGenerator[str, None]:
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": MODEL,
        "messages": messages,
        "max_tokens": max_tokens,
        "stream": True
    }

    async with httpx.AsyncClient(timeout=30) as client:
        async with client.stream("POST", OPENROUTER_API_URL, headers=headers, json=payload) as response:

            if response.status_code != 200:
                error_text = await response.aread()
                raise Exception(f"❌ Ошибка OpenRouter {response.status_code}: {error_text.decode()}")

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

async def yandex_generate(messages, max_tokens) -> str:
    headers = {
        "Authorization": f"Api-Key {YANDEX_API_KEY}",
        "Content-Type": "application/json",
    }

    prompt = "\n".join([m["content"] for m in messages])

    payload = {
        "modelUri": f"gpt://{YANDEX_FOLDER_ID}/yandexgpt-lite",
        "completionOptions": {
            "stream": False,
            "temperature": 0.6,
            "maxTokens": max_tokens,
        },
        "messages": [
            {"role": "user", "text": prompt}
        ],
    }

    async with httpx.AsyncClient(timeout=30) as client:
        response = await client.post(YANDEX_API_URL, headers=headers, json=payload)

    if response.status_code != 200:
        raise Exception(f"Yandex {response.status_code}")

    data = response.json()

    try:
        return data["result"]["alternatives"][0]["message"]["text"]
    except Exception:
        return ""


async def yandex_stream(messages, max_tokens):
    text = await yandex_generate(messages, max_tokens)

    if not text:
        raise Exception("Яндекс не смог сгенерировать текст")

    # имитация стрима (очень лёгкая)
    for chunk in text.split():
        yield chunk + " "
        await asyncio.sleep(0.01)

async def stream_ai_response(
    messages: List[Dict],
) -> AsyncGenerator[str, None]:

    max_tokens = MAX_TOKENS

    for provider in FALLBACK_MODELS:
        for attempt in range(MAX_RETRIES):

            try:
                if provider == "openrouter":
                    async for chunk in openrouter_stream(messages, max_tokens):
                        yield chunk
                    return

                elif provider == "yandex":
                    async for chunk in yandex_stream(messages, max_tokens):
                        yield chunk
                    return

            except httpx.ReadTimeout:
                continue

            except httpx.ConnectError:
                continue

            except Exception as e:
                err = str(e)
                print(f"❌ Ошибка: {err}")

                # лимиты → уменьшаем
                if "402" in err or "max_tokens" in err:
                    max_tokens = int(max_tokens * 0.7)
                    continue

                # модель не найдена → сразу fallback
                if "404" in err:
                    break

                # остальные ошибки → пробуем ещё раз
                continue
            
            print(f"⚠️ Provider {provider} failed, attempt {attempt}")

    # если всё упало
    yield "⚠️ Не удалось получить ответ от AI. Попробуйте позже."