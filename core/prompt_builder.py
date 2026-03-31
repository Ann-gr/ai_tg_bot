def create_prompt(text, mode="analysis", top_n=10, freq_n=10):
    base = f"""
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
    if mode == "analysis":
        return base + f"""
        Perform full text analysis.
        Return format:
        📌 Краткое содержание:
        (2–4 преложения)

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

    elif mode == "summary":
        return base + """
        Create a short summary of the text.

        Return format:

        📌 Краткое содержание:
        (2–4 предложения, без списков)
        """

    elif mode == "keywords":
        return base + f"""
        Extract key words from the text.

        Return format:

        📌 Ключевые слова:
        (Top {top_n}) in the format:
        1. word_n)
        """

    elif mode == "frequency":
        return base + f"""
        Analyze word frequency.

        Return format:

        📌 Частотные слова:
        (Top {freq_n} in the format:
        1. word_n: count)

        Rules:
        - ignore stop words and words with lenght less then 2 chars
        - normalize words (lowercase)
        - sort by frequency descending
        """
    if mode not in ["analysis", "summary", "keywords", "frequency"]:
        mode = "analysis"

    else:
        return base + """
        Return a general structured analysis in Russian.
        """