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
Create a short summary of the text (2-4 sentences, without lists).
Return the result as paragraphed text.
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
Analyze {top_n} word frequency.
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
Тон:
(позитивный / негативный / нейтральный)

Объяснение:
(1–2 предложения)
"""
    },

    "qa": {
    "label": "❓ Вопрос по тексту",
    "needs_param": False,
    "prompt": """
Answer the user's question using ONLY the provided text.
Question: {question}
Return:
Ответ:
(краткий и точный ответ)

Обоснование:
(где в тексте это найдено, 1–2 предложения)

If the answer is not in the text, say:
"Ответ не найден в тексте"
"""
}
}