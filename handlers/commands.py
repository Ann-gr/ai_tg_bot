from telegram import Update
from telegram.ext import ContextTypes
from handlers.keyboards import get_mode_keyboard, get_main_menu_keyboard

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Привет!\n\n"
        "Я бот для анализа текста и документов.\n\n"
        "📂 Отправьте текст/файл\n"
        "или выберите действие ниже 👇",
        reply_markup=get_main_menu_keyboard(False)
    )

async def menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "☰ Главное меню\n\n"
        "Выберите действие:",
        parse_mode="Markdown",
        reply_markup=get_mode_keyboard()
    )

async def help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🧠 *Режимы анализа*\n\n"

        "📊 *Общий анализ*\n"
        "→ краткое содержание, тема, ключевые идеи\n\n"

        "📝 *Краткое содержание*\n"
        "→ выжимка текста в 2–4 предложения\n\n"

        "🔑 *Ключевые слова*\n"
        "→ самые важные слова (вы выбираете количество)\n\n"

        "📈 *Частотный анализ*\n"
        "→ какие слова встречаются чаще всего\n\n"

        "🧠 *Тональность*\n"
        "→ позитивный / нейтральный / негативный\n\n"

        "📌 Как это работает:\n"
        "1. Отправьте файл или текст\n"
        "2. Выберите режим\n"
        "3. Получите анализ\n"
        "4. При необходимости — измените режим без повторной загрузки",
        parse_mode="Markdown",
        reply_markup=get_mode_keyboard()
    )

async def example(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📌 Пример работы:\n\n"
        "Вы отправляете:\n"
        "📄 PDF со статьёй\n\n"
        "Выбираете:\n"
        "📝 Краткое содержание\n\n"
        "Я возвращаю:\n"
        "• Основную мысль\n"
        "• Ключевые выводы\n"
        "• Короткое резюме"
    )