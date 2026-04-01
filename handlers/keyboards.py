from telegram import ReplyKeyboardMarkup
def get_main_keyboard():
    keyboard = [
        ["📊 Общий анализ", "📝 Краткое содержание"],
        ["🔑 Ключевые слова", "📈 Частотный анализ"],
        ["📜 Показать память"],["🧹 Очистить память"]
    ]

    return ReplyKeyboardMarkup(
        keyboard,
        resize_keyboard=True
    )

def get_number_keyboard():
    keyboard = [
        ["5", "10"],
        ["15", "20"],
        ["25", "30"],
        ["⬅️ Назад"]
    ]

    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)