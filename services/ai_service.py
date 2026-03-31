import requests
from config import API_URL, OPENROUTER_API_KEY, MODEL

def analyze_with_ai(prompt):
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": MODEL,
        "messages": [{"role": "user", "content": prompt}]
    }

    try:
        response = requests.post(API_URL, headers=headers, json=payload, timeout=15)

        if response.status_code == 200:
            return response.json()["choices"][0]["message"]["content"]
        
        return f"Ошибка {response.status_code}: {response.text}"
    
    except requests.exceptions.RequestException:
        return "Ошибка подключения к API"