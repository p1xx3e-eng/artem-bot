import os
from google import genai
from google.genai import types
from supabase_service import get_guide, get_posts

client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])
MODEL = "gemini-1.5-flash"

def build_system_prompt() -> str:
    guide = get_guide()
    posts = get_posts(limit=30)

    examples_text = "\n\n---\n\n".join(posts) if posts else "Примеров постов пока нет."
    guide_text = guide if guide else "Гайд по постингу пока не загружен."

    return f"""Ты — ИИ-помощник для написания постов в Telegram-канал.

## ГАЙД ПО ПОСТИНГУ:
{guide_text}

## ПРИМЕРЫ ПОСТОВ АВТОРА (изучи стиль, тон, структуру):
{examples_text}

## ТВОЯ ЗАДАЧА:
Писать посты точно в стиле автора — такой же тон, длина, структура, подача.
Не добавляй ничего от себя. Не объясняй что ты сделал. Просто пиши пост.
"""

def generate_post(topic: str) -> str:
    system = build_system_prompt()
    prompt = f"Напиши пост на тему: {topic}"
    response = client.models.generate_content(
        model=MODEL,
        contents=system + "\n\n" + prompt
    )
    return response.text

def suggest_topics(count: int = 5) -> str:
    system = build_system_prompt()
    prompt = f"Предложи {count} идей для постов. Учитывай гайд и стиль автора. Выдай просто список тем, без лишних слов."
    response = client.models.generate_content(
        model=MODEL,
        contents=system + "\n\n" + prompt
    )
    return response.text
