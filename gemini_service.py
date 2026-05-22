import os
from groq import Groq
from supabase_service import get_guide, get_posts

client = Groq(api_key=os.environ["GROQ_API_KEY"])
MODEL = "llama-3.3-70b-versatile"

def build_system_prompt() -> str:
    guide = get_guide()
    posts = get_posts(limit=10)

    examples_text = "\n\n---\n\n".join(posts) if posts else "Примеров постов пока нет."
    guide_text = (guide[:3000] + "...") if guide and len(guide) > 3000 else (guide or "Гайд по постингу пока не загружен.")

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
    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": prompt}
        ]
    )
    return response.choices[0].message.content

def suggest_topics(count: int = 5) -> str:
    system = build_system_prompt()
    prompt = f"Предложи {count} идей для постов. Учитывай гайд и стиль автора. Выдай просто список тем, без лишних слов."
    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": prompt}
        ]
    )
    return response.choices[0].message.content
