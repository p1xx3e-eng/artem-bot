import io
from aiogram import Router, F
from aiogram.types import Message, Document
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext

import supabase_service as db
import gemini_service as ai
from parser import parse_pdf, parse_telegram_html

router = Router()

# ───────────────────────────── /start ─────────────────────────────

@router.message(CommandStart())
async def cmd_start(message: Message):
    await message.answer(
        "Привет! Я помогу писать посты в твой стиль.\n\n"
        "Что умею:\n"
        "• Напиши тему — сгенерю пост\n"
        "• /topics — предложу идеи для постов\n"
        "• /upload_guide — загрузить PDF гайд по постингу\n"
        "• /upload_posts — загрузить HTML-файлы с примерами постов\n"
        "• /clear_posts — очистить примеры постов\n"
        "• /status — что сейчас загружено"
    )

# ───────────────────────────── /status ─────────────────────────────

@router.message(Command("status"))
async def cmd_status(message: Message):
    guide = db.get_guide()
    posts = db.get_posts(limit=1000)
    guide_status = "✅ Загружен" if guide else "❌ Не загружен"
    await message.answer(
        f"📋 Гайд: {guide_status}\n"
        f"📝 Примеров постов: {len(posts)}"
    )

# ───────────────────────────── /topics ─────────────────────────────

@router.message(Command("topics"))
async def cmd_topics(message: Message):
    await message.answer("Думаю над темами...")
    try:
        topics = ai.suggest_topics(count=5)
        await message.answer(topics)
    except Exception as e:
        await message.answer(f"Ошибка [{type(e).__name__}]: {e}")

# ───────────────────────────── Upload guide ─────────────────────────────

@router.message(Command("upload_guide"))
async def cmd_upload_guide(message: Message):
    await message.answer("Отправь PDF-файл с гайдом по постингу.")

@router.message(F.document, F.document.mime_type == "application/pdf")
async def handle_pdf(message: Message):
    await message.answer("Читаю гайд...")
    try:
        file_bytes = await _download_file(message.bot, message.document)
        text = parse_pdf(file_bytes)
        if not text:
            await message.answer("Не смог извлечь текст из PDF. Попробуй другой файл.")
            return
        db.save_guide(text, message.document.file_name)
        await message.answer(f"✅ Гайд сохранён ({len(text)} символов)")
    except Exception as e:
        await message.answer(f"Ошибка при чтении PDF: {e}")

# ───────────────────────────── Upload posts HTML ─────────────────────────────

@router.message(Command("upload_posts"))
async def cmd_upload_posts(message: Message):
    await message.answer(
        "Отправляй HTML-файлы с экспортом канала.\n"
        "Можно по одному или несколько подряд."
    )

@router.message(F.document)
async def handle_html(message: Message):
    if not (message.document.file_name or "").endswith(".html"):
        return
    await message.answer("Парсю посты...")
    try:
        file_bytes = await _download_file(message.bot, message.document)
        posts = parse_telegram_html(file_bytes)
        if not posts:
            await message.answer("Постов не нашёл в этом файле. Убедись что это экспорт Telegram-канала.")
            return
        db.save_posts(posts, message.document.file_name)
        await message.answer(f"✅ Загружено {len(posts)} постов из {message.document.file_name}")
    except Exception as e:
        await message.answer(f"Ошибка при парсинге HTML: {e}")

# ───────────────────────────── Clear posts ─────────────────────────────

@router.message(Command("clear_posts"))
async def cmd_clear_posts(message: Message):
    db.clear_posts()
    await message.answer("✅ Примеры постов очищены.")

# ───────────────────────────── Generate post ─────────────────────────────

@router.message(F.text)
async def handle_topic(message: Message):
    topic = message.text.strip()
    await message.answer("Пишу пост...")
    try:
        post = ai.generate_post(topic)
        await message.answer(post)
    except Exception as e:
        await message.answer(f"Ошибка генерации [{type(e).__name__}]: {e}")

# ───────────────────────────── Helper ─────────────────────────────

async def _download_file(bot, document: Document) -> bytes:
    file = await bot.get_file(document.file_id)
    buf = io.BytesIO()
    await bot.download_file(file.file_path, destination=buf)
    return buf.getvalue()
