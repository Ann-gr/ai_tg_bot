from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from utils.mode_utils import get_mode_title

def get_empty_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📂 Загрузить текст", callback_data="go:upload")],
        [InlineKeyboardButton("🧠 Как это работает", callback_data="go:help")]
    ])

def get_modes_keyboard():
    keyboard = [
        [
            InlineKeyboardButton("📊 Общий анализ", callback_data="mode:analysis"),
            InlineKeyboardButton("📝 Краткое содержание", callback_data="mode:summary"),
        ],
        [
            InlineKeyboardButton("🔑 Ключевые слова", callback_data="mode:keywords"),
            InlineKeyboardButton("📈 Частотный анализ", callback_data="mode:frequency"),
        ],
        [
            InlineKeyboardButton("🧠 Тональность", callback_data="mode:sentiment"),
            InlineKeyboardButton("❓ Вопрос по тексту", callback_data="mode:qa"),
        ],
        [
            InlineKeyboardButton("📜 История", callback_data="go:history")
        ]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_param_keyboard(mode):
    values = [5, 10, 20, 50]

    keyboard = [
        [InlineKeyboardButton(str(v), callback_data=f"param:{mode}:{v}")]
        for v in values
    ]

    keyboard.append([InlineKeyboardButton("⬅️ Назад", callback_data="action:change_mode")])

    return InlineKeyboardMarkup(keyboard)

def get_result_keyboard(is_truncated=False):
    keyboard = []

    if is_truncated:
        keyboard.append([
            InlineKeyboardButton("📖 Показать полностью", callback_data="action:full_result")
        ])
    else:
        keyboard.append([
            InlineKeyboardButton("🔽 Свернуть", callback_data="action:short_result")
        ])

    keyboard.extend([
        [
            InlineKeyboardButton("💬 Задать вопрос по тексту", callback_data="action:ask_more"),
            InlineKeyboardButton("🔁 Повторить", callback_data="action:repeat")
        ],
        [
            InlineKeyboardButton("⚙️ Выбрать другой режим", callback_data="action:change_mode"),
            InlineKeyboardButton("📂 Новый текст", callback_data="action:new_text")
        ]
    ])

    return InlineKeyboardMarkup(keyboard)

def get_qa_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("💬 Ещё вопрос", callback_data="action:ask_more")],
        [InlineKeyboardButton("⬅️ Главное меню", callback_data="go:menu")]
    ])

def get_back_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("⬅️ Назад", callback_data="go:menu")]
    ])

def get_analysis_history_keyboard(history):
    keyboard = []

    for item in history[-10:]:
        preview = item["result"][:40].replace("\n", " ")

        keyboard.append([
            InlineKeyboardButton(
                text=f"{get_mode_title(item['mode'])} | {preview}...",
                callback_data=f"analysis_item:{item['id']}"
            )
        ])

    keyboard.append([
        InlineKeyboardButton("⬅️ Назад", callback_data="go:history")
    ])

    return InlineKeyboardMarkup(keyboard)

def get_history_menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📊 Анализы", callback_data="action:analysis_history")],
        [InlineKeyboardButton("❓ Вопросы", callback_data="action:qa_history")],
        [InlineKeyboardButton("🧹 Очистить", callback_data="action:clear_all")],
        [InlineKeyboardButton("⬅️ Назад", callback_data="go:menu")]
    ])

def get_history_back_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("⬅️ К истории", callback_data="go:history")],
        [InlineKeyboardButton("🏠 В меню", callback_data="go:menu")]
    ])