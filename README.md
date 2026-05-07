# 🤖 AI Text Analyzer Telegram Bot

Telegram bot for text and document analysis using LLM APIs (OpenRouter + YandexGPT fallback).

Built with:
- Python
- python-telegram-bot
- PostgreSQL
- Async architecture
- Streaming AI responses

---

# 🚀 Features

## 📄 Text & File Processing
- TXT
- PDF
- DOCX

## 🧠 Analysis Modes
- Full analysis
- Summary
- Keywords extraction
- Word frequency analysis
- Sentiment analysis
- Context-aware Q&A

## ⚡ Streaming Responses
- Real-time AI response streaming
- Incremental message updates
- Telegram-friendly rendering

## 💬 Smart Toggle UX
- Expand/collapse analysis
- No re-generation
- No extra AI requests
- Minimal Telegram message updates

## 🗂 History System
- Analysis history
- Q&A history
- Persistent PostgreSQL storage

## 🔄 AI Fallback System
If OpenRouter fails:
- automatic retry
- token reduction
- fallback to YandexGPT

---

# 🏗 Architecture

## Layers

### handlers/
Telegram UI layer:
- commands
- callbacks
- messages
- keyboards

### services/
Business logic:
- AI communication
- streaming
- repositories
- orchestration

### state/
User state management.

### core/
Prompt system and mode registry.

### utils/
Pure utility/helper functions.

---

# 🧠 Streaming Architecture

The bot uses:
- async generators
- incremental rendering
- edit_message_text for pseudo-streaming UX

This creates a ChatGPT-like experience within Telegram API limitations.

---

# ⚠️ Telegram API Limitations

Telegram does not support:
- partial message updates
- DOM-like rendering

Because of this:
- toggle is implemented via `edit_message_text`
- streaming is simulated through message editing

---

# 🗄 Database

PostgreSQL tables:
- texts
- text_chunks
- analysis_results
- qa_messages
- user_state

---

# 🚀 Deployment

Designed for:
- Render
- Railway
- VPS

Uses:
- Flask webhook
- async Telegram bot
- PostgreSQL connection pool

---