import os
from google import genai
from supabase_service import get_guide, get_posts

client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])
MODEL = "gemini-2.0-flash"

def build_system_prompt() -> str:
    guide = get_guide()
    posts = get_posts(limit=15)

    examples_text = "\n\n---\n\n".join(posts) if posts else "Примеров постов пока нет."
    guide_text = (guide[:3000] + "...") if guide and len(guide) > 3000 else (guide or "Гайд не загружен.")

    return f"""Ты помогаешь писать посты для Telegram-канала. Твоя задача — писать ТОЧНО в стиле автора.

ПРИМЕРЫ ПОСТОВ АВТОРА (копируй стиль, тон, длину, подачу):
{examples_text}

ГАЙД ПО ПОСТИНГУ:
{guide_text}

ПРАВИЛА:
- Пиши точно как автор — тот же разговорный стиль, те же обороты, та же длина
- Никаких иероглифов и иностранных слов кроме английских терминов из IT
- Не объясняй что ты сделал — просто пиши пост
- Никаких вступлений типа "Вот пост:" — сразу текст
"""

def generate_post(topic: str) -> str:
    system = build_system_prompt()
    response = client.models.generate_content(
        model=MODEL,
        contents=f"{system}\n\nНапиши пост на тему: {topic}"
    )
    return response.text

def suggest_topics(count: int = 5) -> str:
    system = build_system_prompt()
    response = client.models.generate_content(
        model=MODEL,
        contents=f"{system}\n\nПредложи {count} идей для постов. Учитывай стиль и тематику канала. Просто список тем без лишних слов."
    )
    return response.text
