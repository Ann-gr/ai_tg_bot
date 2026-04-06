BASE_PROMPT = """
You are a senior text analysis assistant.
Your task is to analyze the given text and return a clear and structured response.

CRITICAL RULES:
- Always respond in Russian
- Do NOT use JSON
- Do NOT add explanations outside the required structure
- Be concise and structured
- Follow the output format EXACTLY
- Do NOT copy large parts of the original text

TEXT:
{text}

IMPORTANT:
You MUST strictly follow the output format.
Do not change section names.
Do not translate them.
Do not add any extra text.

Example output:

Краткое содержание:
...

Тема:
...

Ключевые идеи:
- ...
- ...
- ...
- ...

Ключевые слова:
- ...
- ...
- ...
- ...
- ...
"""

MODE_REGISTRY = {
    "analysis": {
        "label": "📊 Общий анализ",
        "needs_param": False,
        "prompt": """
Perform a full analysis of the text.
Return the result in the following structure:
Краткое содержание:
(2–4 предложения)

Тема:
(1 строка)

Ключевые идеи:
- идея 1
- идея 2
- идея 3
- идея 4

Ключевые слова:
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
Return the result in the following structure:
Краткое содержание:
(2–4 предложения, без списков)
"""
    },

    "keywords": {
        "label": "🔑 Ключевые слова",
        "needs_param": True,
        "param_name": "n",
        "prompt": """
Extract {top_n} key words from the text.

Return the result in the following structure:
1. слово
2. слово
...
"""
    },

    "frequency": {
        "label": "📈 Частотный анализ",
        "needs_param": True,
        "param_name": "n",
        "prompt": """
Analyze word frequency.
Return the result as a numbered list:
1. слово: количество
2. слово: количество

Rules:
- ignore stop words
- ignore words shorter than 2 characters
- normalize words to lowercase
- sort by frequency descending
"""
    },

    "sentiment": {
        "label": "🧠 Тональность",
        "needs_param": False,
        "prompt": """
Analyze the tone of the text.
Return the result in the following structure:

Тональность:
(позитивная / негативная / нейтральная)

Объяснение:
(1–2 предложения)
"""
    }
}