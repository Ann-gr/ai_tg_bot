import os

from telegram import Update
from telegram.ext import ContextTypes

from handlers.keyboards import get_modes_keyboard
from state import state_manager

from services.file_service import extract_text_from_file, FileProcessingError
from services.analysis_flow import process_user_input
from services.text_repository import save_text
from services.chunk_repository import save_chunks

from utils.render import render_result
from utils.text_splitter import split_text

MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB
MAX_TEXT_LENGTH = 8000

SUPPORTED_FORMATS = (".txt", ".pdf", ".docx")

# ОБРАБОТКА ТЕКСТА
async def handle_message(update, context):
    user_id = update.effective_user.id
    state = await state_manager.get_state(user_id)
    text = update.message.text
    text_id = state["current_text_id"]

    chunks = split_text(text)
    await save_chunks(text_id, chunks)


    loading_msg = await update.message.reply_text(
        "⏳ Думаю над ответом...\n\nЭто может занять несколько секунд"
    )

    # Если режим QA и мы ожидаем вопрос
    if state.get("mode") == "qa":
        if not state.get("current_text_id"):
            await loading_msg.edit_text("❌ Сначала загрузите текст")
            return
        
        data = await process_user_input(user_id, state, user_question=text)
    else:
        data = await process_user_input(user_id, state, new_text=text)

    # ошибки
    if data.get("error"):
        await loading_msg.edit_text(data["error"])
        return

    # выбрать режим
    if data.get("action") == "ask_mode":
        state = data["state"]
        await state_manager.update_state(user_id, **state)

        # очищаем текущий текст
        state["ui_state"] = "TEXT_LOADED"

        await state_manager.update_state(user_id, **state)

        await update.message.reply_text(
            "✅ Текст загружен\n\nВыберите режим анализа:",
            reply_markup=get_modes_keyboard(),
        )
        return

    # показать результат
    if data.get("action") == "show_result":
        result = data["result"]
        
        state = data["state"]
        state["ui_state"] = "RESULT"
        state["result_view"] = "short"

        await state_manager.update_state(user_id, **state)

        await render_result(
            loading_msg.edit_text,
            state,
            result
        )
        return

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
        text_id = await save_text(user_id, text)
        await state_manager.update_state(
            user_id,
            current_text_id=text_id,
            question=None
        )

        chunks = split_text(text)
        await save_chunks(text_id, chunks)

        await update.message.reply_text(
            "✅ Файл успешно загружен\n\nВыберите режим анализа:",
            reply_markup=get_modes_keyboard(),
        )

    except FileProcessingError as e:
        await update.message.reply_text(f"❌ Ошибка файла:\n{e}")

    except Exception:
        await update.message.reply_text("❌ Не удалось обработать файл")

    finally:
        # Очистка
        if os.path.exists(file_path):
            os.remove(file_path)