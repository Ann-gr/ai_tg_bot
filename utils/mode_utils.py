MODE_TITLES = {
    "analysis": "📊 Общий анализ",
    "summary": "📝 Краткое содержание",
    "keywords": "🔑 Ключевые слова",
    "frequency": "📈 Частотный анализ",
    "sentiment": "🧠 Тональность",
}

def get_mode_title(mode: str) -> str:
    return MODE_TITLES.get(mode, "📊 Анализ")