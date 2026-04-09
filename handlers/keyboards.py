from telegram import InlineKeyboardButton, InlineKeyboardMarkup

def get_mode_keyboard():
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

def get_result_keyboard(mode, is_truncated=False):
    keyboard = []

    if is_truncated:
        keyboard.append([
            InlineKeyboardButton("📖 Показать полностью", callback_data="action:full_result")
    ])
        
    if mode == "qa":
        keyboard.append([
            InlineKeyboardButton("💬 Задать ещё вопрос", callback_data="action:ask_more"),
        ])

    keyboard.extend([
        [
            InlineKeyboardButton("🔁 Повторить", callback_data="action:repeat"),
        ],
        [
            InlineKeyboardButton("⚙️ Изменить режим", callback_data="action:change_mode"),
            InlineKeyboardButton("🆕 Новый текст", callback_data="action:new_text"),
        ],
        [
            InlineKeyboardButton("⬅️ В меню", callback_data="go:menu"),
        ]
    ])

    return InlineKeyboardMarkup(keyboard)

def get_main_menu_keyboard(has_text=False):
    keyboard = [
        [InlineKeyboardButton("📂 Загрузить текст", callback_data="go:upload")],
    ]

    if has_text:
        keyboard.append([
            InlineKeyboardButton("🔁 Повторить анализ", callback_data="action:repeat")
        ])
        keyboard.append([
            InlineKeyboardButton("⚙️ Выбрать режим", callback_data="action:change_mode")
        ])

    keyboard.append([
        InlineKeyboardButton("🧠 Помощь", callback_data="go:help")
    ])
    keyboard.append([
        InlineKeyboardButton("🧷 Пример работы", callback_data="go:example")
    ])

    return InlineKeyboardMarkup(keyboard)

def get_back_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("⬅️ Назад", callback_data="go:menu")]
    ])