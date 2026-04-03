from telegram import Update
from telegram.ext import ContextTypes
# UI (кнопки Telegram)
from handlers.keyboards import get_main_keyboard, get_number_keyboard
# работа с памятью пользователя
from state.user_state import set_user, get_user, get_history, clear_history

from services.analysis_service import run_analysis 

# состояние пользователя по умолчанию
def get_default_state():
    return {
        "mode": "analysis",
        "top_n": 10,
        "freq_n": 10,
        "last_text": None
    }

async def analyze_last_text(update, user_id, state):
    await update.message.reply_text("⏳ Анализирую предыдущий текст...")
    
    try:
        result = await run_analysis(user_id, state["last_text"], state)
    except Exception as e:
        print("AI ERROR:", e)
        result = "❌ Ошибка при обработке"

    await update.message.reply_text(result, reply_markup=get_main_keyboard())
    return True

MODE_CONFIG = {
    "📊 Общий анализ": {
        "mode": "analysis",
        "text": "Режим: общий анализ 📊\n\nОтправьте текст"
    },
    "📝 Краткое содержание": {
        "mode": "summary",
        "text": "Режим: краткое содержание 📝\n\nОтправьте текст"
    },
    "🔑 Ключевые слова": {
        "mode": "keywords",
        "ask_number": True
    },
    "📈 Частотный анализ": {
        "mode": "frequency",
        "ask_number": True
    },
    "🧠 Анализ тональности": {
        "mode": "sentiment",
        "text": "Режим: анализ тональности 🧠\n\nОтправьте текст"
    }
}

CONTROL_BUTTONS = [
    "📊 Общий анализ",
    "📝 Краткое содержание",
    "🔑 Ключевые слова",
    "📈 Частотный анализ",
    "🆕 Добавить новый текст",
    "📜 Показать память",
    "🧹 Очистить память",
    "⬅️ Назад"
]

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE): # вызывается на каждое текстовое сообщение
    user_id = update.effective_user.id
    text = update.message.text

    state = get_user(user_id) or get_default_state()

    # обработка кнопок
    if text in MODE_CONFIG:
        config = MODE_CONFIG[text]

        state["mode"] = config["mode"]

        # если нужен выбор числа
        if config.get("ask_number"):
            state["waiting_for_number"] = True
            set_user(user_id, state)

            if state.get("last_text"):
                await update.message.reply_text(
                    "Текст уже загружен ✅\nВыберите количество слов 👇",
                    reply_markup=get_number_keyboard()
                )
            else:
                await update.message.reply_text(
                    "Сколько слов вывести?",
                    reply_markup=get_number_keyboard()
                )
            return

        set_user(user_id, state)

        # если есть предыдущий текст → анализируем
        if state.get("last_text"):
            await analyze_last_text(update, user_id, state)
        else:
            await update.message.reply_text(
                config["text"],
                reply_markup=get_main_keyboard()
            )
        return
    
    elif text == "⬅️ Назад":
        await update.message.reply_text(
            "Выберите режим 👇",
            reply_markup=get_main_keyboard()
        )
        return
    
    elif text == "🆕 Добавить новый текст":
        state["last_text"] = None
        set_user(user_id, state)

        await update.message.reply_text(
            "Отправьте новый текст ✍️",
            reply_markup=get_main_keyboard()
        )
        return
    
    elif text == "📜 Показать память":
        history = get_history(user_id)

        if not history:
            await update.message.reply_text("Память пустая")
            return

        preview = "\n\n".join(
            f"{m['role']}: {m['content'][:50]}..."
            for m in history[-5:]
        )

        await update.message.reply_text(f"📜 Последние сообщения:\n\n{preview}")
        return
    
    elif text == "🧹 Очистить память":
        clear_history(user_id)
        state["last_text"] = None
        set_user(user_id, state)

        await update.message.reply_text("Память очищена ✅", reply_markup=get_main_keyboard())
        return
    
    # если ждём число
    if state.get("waiting_for_number"):
        if text not in ["5", "10", "15", "20", "25", "30"]:
            await update.message.reply_text("Пожалуйста, выберите число кнопкой 👇")
            return

        number = int(text)

        if state["mode"] == "keywords":
            state["top_n"] = number
        elif state["mode"] == "frequency":
            state["freq_n"] = number

        state["waiting_for_number"] = False
        set_user(user_id, state)

        if state.get("last_text"):
            await analyze_last_text(update, user_id, state)
        else:   
            await update.message.reply_text(
            f"Отлично! Выбрано: {number} ✅\n\nТеперь отправьте текст",
            reply_markup=get_main_keyboard()
        )
        return

    state["last_text"] = text
    set_user(user_id, state)

    await update.message.reply_text("⏳ Анализирую текст...")

    try:
        result = await run_analysis(user_id, text, state)
    except Exception as e:
        print("AI ERROR:", e)
        result = "❌ Ошибка при обработке"

    await update.message.reply_text(result, reply_markup=get_main_keyboard())

    if text in CONTROL_BUTTONS:
        return

async def handle_document(update: Update, context: ContextTypes.DEFAULT_TYPE):
    document = update.message.document
    user_id = update.effective_user.id

    state = get_user(user_id) or get_default_state()

    # проверяем тип файла
    if not document.file_name.endswith(".txt"):
        await update.message.reply_text("Пожалуйста, отправьте .txt файл 📄")
        return

    await update.message.reply_text("📥 Загружаю файл...")

    file = await context.bot.get_file(document.file_id) # получаем файл с серверов Telegram
    file_path = f"/tmp/{document.file_name}" # это временная папка на сервере (в Render работает)

    await file.download_to_drive(file_path)

    # читаем файл
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            text = f.read()
    except Exception:
        await update.message.reply_text("❌ Не удалось прочитать файл")
        return

    # ограничение размера
    if len(text) > 10000:
        text = text[:10000]

    state["last_text"] = text
    set_user(user_id, state)
    mode = state.get("mode", "analysis")

    await update.message.reply_text(f"⏳ Анализирую файл ({mode})...")
    
    try:
        result = await run_analysis(user_id, text, state)
    except Exception as e:
        print("AI ERROR:", e)
        result = "❌ Ошибка при обработке файла"

    await update.message.reply_text(result, reply_markup=get_main_keyboard())