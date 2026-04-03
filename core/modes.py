BASE_PROMPT = """
You are a senior text analysis assistant for a Telegram bot.
Your task is to analyze user-provided text and return a clear, structured response.

CRITICAL RULES:
- Always respond in Russian
- Do NOT use JSON
- Do NOT add explanations outside the required structure
- Be concise and structured
- Follow the output format EXACTLY
- Do NOT copy large parts of the original text
- All section titles must be in Russian

TEXT:
{text}
"""

MODE_REGISTRY = {
    "analysis": {
        "label": "📊 Общий анализ",
        "needs_param": False,
        "prompt": """
Perform full text analysis.
Return format:
📌 Краткое содержание:
(2–4 предложения)

📌 Тема:
(1 строка)

📌 Ключевые идеи:
- идея 1
- идея 2
- идея 3
- идея 4

📌 Ключевые слова:
- слово 1
- слово 2
- слово 3
- слово 4
- слово 5
(Top {top_n})
"""
    },

    "summary": {
        "label": "📝 Краткое содержание",
        "needs_param": False,
        "prompt": """
Create a short summary of the text.

Return format:
📌 Краткое содержание:
(2–4 предложения, без списков)
"""
    },

    "keywords": {
        "label": "🔑 Ключевые слова",
        "needs_param": True,
        "param_name": "n",
        "prompt": """
Extract {top_n} key words from the text.

Return format:
📌 Ключевые слова:
(Top {top_n}) in the format:
1. word_n)
"""
    },

    "frequency": {
        "label": "📈 Частотный анализ",
        "needs_param": True,
        "param_name": "n",
        "prompt": """
Analyze word frequency.

Return format:

📌 Частотные слова:
(Top {freq_n} in the format:
1. word_n: count)

Rules:
- ignore stop words and words with length less than 2 chars
- normalize words (lowercase)
- sort by frequency descending
"""
    },

    "sentiment": {
        "label": "🧠 Тональность",
        "needs_param": False,
        "prompt": """
Analyze the tone of the text.

Return format:

📌 Тональность:
(позитивная / негативная / нейтральная)

📌 Объяснение:
(1–2 предложения)
"""
    }
}