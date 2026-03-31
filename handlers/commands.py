from telegram import Update
from telegram.ext import ContextTypes
from handlers.keyboards import get_main_keyboard

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Привет! 👋\n\nЯ бот для анализа текста.\nВыберите режим ниже 👇",
        reply_markup=get_main_keyboard()
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Используйте кнопки для выбора режима анализа.\n\n📊 Общий анализ - краткое содержание, основная тема, ключевые идеи и слова (топ 10).\n📝 Краткое содержание - четкая выжимка из текста на 2-4 предложения.\n🔑 Ключевые слова - выводит ключевые слова (количество указывается после выбора режима).\n📈 Частотный анализ - выводит топ слов по частоте упоминания в тексте (количество указывается после выбора режима).",
        reply_markup=get_main_keyboard()
    )