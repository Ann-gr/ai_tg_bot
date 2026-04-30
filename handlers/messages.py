import os

from telegram import Update
from telegram.ext import ContextTypes

from handlers.keyboards import get_modes_keyboard
from state import state_manager

from services.analysis_flow import run_analysis_pipeline
from services.file_service import extract_text_from_file, FileProcessingError
from services.history_repository import save_analysis, save_qa
from services.text_repository import save_text, save_chunks

from utils.text_splitter import split_text

MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB
MAX_TEXT_LENGTH = 4000

SUPPORTED_FORMATS = (".txt", ".pdf", ".docx")

UPDATE_INTERVAL = 0.4  # сек
MIN_CHARS = 40

# ОБРАБОТКА ТЕКСТА
async def handle_message(update, context):
    user_id = update.effective_user.id
    state = await state_manager.get_state(user_id)
    text = update.message.text

    if update.message.photo:
        await update.message.reply_text("📷 Пожалуйста, отправьте файл (PDF, DOCX, TXT), а не фото")

    loading_msg = await update.message.reply_text(
        "⏳ Думаю над ответом...\n\nЭто может занять несколько секунд"
    )

    # Если QA режим → это вопрос
    user_question = text if state.get("mode") == "qa" else None

    full_text = await run_analysis_pipeline(
        edit_func=loading_msg.edit_text,
        user_id=user_id,
        state=state,
        new_text=text if not user_question else None,
        user_question=user_question
    )

    try:
        if not full_text:
            print("❌ Пустой результат, пропускаем сохранение в БД")
            return
        
        if state.get("mode") == "qa":
            await save_qa(
                user_id,
                state.get("current_text_id"),
                text,
                full_text
            )
        else:
            analysis_id = await save_analysis(
                user_id,
                state.get("current_text_id"),
                state.get("mode"),
                full_text
            )

            state["last_result_id"] = analysis_id
            await state_manager.update_state(user_id, **state)

    except Exception as e:
        print("❌ Ошибка сохранения в БД:", e)  

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
        # Определяем тип и извлекаем текст
        text = extract_text_from_file(file_path, file_name.split(".")[-1])

        # Ограничение текста
        if len(text) > MAX_TEXT_LENGTH:
            text = text[:MAX_TEXT_LENGTH]

        # Сохраняем в state
        text_id = await save_text(user_id, text)
        await state_manager.update_state(
            user_id,
            current_text_id=text_id
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

async def handle_unsupported(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "❌ Поддерживаются только файлы: PDF, DOCX, TXT"
    )