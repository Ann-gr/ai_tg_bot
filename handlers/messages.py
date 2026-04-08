import os

from telegram import Update
from telegram.ext import ContextTypes

from handlers.keyboards import get_mode_keyboard
from state import state_manager

from services.file_service import extract_text_from_file, FileProcessingError

MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB
MAX_TEXT_LENGTH = 20000

SUPPORTED_FORMATS = (".txt", ".pdf", ".docx")

# ОБРАБОТКА ТЕКСТА
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text = update.message.text

    state = await state_manager.get_state(user_id)

    # если режим вопроса → сохраняем вопрос
    if state.get("mode") == "qa" and state.get("last_text"):
        state["question"] = text
        await state_manager.update_state(user_id, **state)

        await update.message.reply_text(
            "✅ Вопрос сохранён, выполняю анализ..."
        )

        # запускаем анализ
        return

    # обычная логика
    await state_manager.update_state(user_id, last_text=text)

    await update.message.reply_text(
        "✅ Текст загружен\n\nВыберите режим анализа:",
        reply_markup=get_mode_keyboard(),
    )

# ОБРАБОТКА ФАЙЛОВ
async def handle_document(update: Update, context: ContextTypes.DEFAULT_TYPE):
    document = update.message.document
    user_id = update.effective_user.id
    file_name = document.file_name.lower()

    # Проверка формата
    if not file_name.endswith(SUPPORTED_FORMATS):
        await update.message.reply_text(
            "❌ Поддерживаются только следующие форматы: PDF, DOCX, TXT"
        )
        return

    # Проверка размера
    if document.file_size > MAX_FILE_SIZE:
        await update.message.reply_text(
            "❌ Файл слишком большой (макс 5MB)"
        )
        return

    await update.message.reply_text("📥 Загружаю файл...")

    file = await context.bot.get_file(document.file_id)
    file_path = f"/tmp/{document.file_name}"

    await file.download_to_drive(file_path)
    
    await update.message.reply_text("🔍 Извлекаю текст из файла...")

    try:
        # Определяем тип
        file_type = file_name.split(".")[-1]

        # Извлекаем текст
        text = extract_text_from_file(file_path, file_type)

        # Ограничение текста
        if len(text) > MAX_TEXT_LENGTH:
            text = text[:MAX_TEXT_LENGTH]

        # Сохраняем в state
        await state_manager.update_state(user_id, last_text=text)

        await update.message.reply_text(
            "✅ Файл успешно загружен\n\nВыберите режим анализа:",
            reply_markup=get_mode_keyboard(),
        )

    except FileProcessingError as e:
        await update.message.reply_text(f"❌ Ошибка файла:\n{e}")

    except Exception:
        await update.message.reply_text("❌ Не удалось обработать файл")

    finally:
        # Очистка
        if os.path.exists(file_path):
            os.remove(file_path)