import os
from groq import Groq
from supabase_service import get_guide, get_posts

client = Groq(api_key=os.environ["GROQ_API_KEY"])
MODEL = "llama-3.3-70b-versatile"

def build_system_prompt() -> str:
    guide = get_guide()
    posts = get_posts(limit=5)

    # Режем каждый пост до 400 символов
    trimmed = [p[:400] for p in posts]
    examples_text = "\n\n---\n\n".join(trimmed) if trimmed else ""

    # Режем гайд до 1500 символов
    guide_text = (guide[:1500] + "...") if guide and len(guide) > 1500 else (guide or "")

    system = """Ты пишешь посты для Telegram-канала веб-разработчика фрилансера.

СТИЛЬ АВТОРА:
- Разговорный, живой, без воды
- Пишет от первого лица, делится личным опытом
- Может использовать мат (хуйня, подзаебали и т.д.) — это его стиль
- Темы: фриланс, клиенты, верстка, WordPress, кворк, профи.ру, заработок, обучение
- Длина поста — средняя, не портянка и не 2 строчки
- Никаких иероглифов и китайских символов
- Никаких вступлений типа "Вот пост" — сразу текст
- Не пиши как ChatGPT — пиши как живой человек"""

    if examples_text:
        system += f"\n\nПРИМЕРЫ ЕГО ПОСТОВ:\n{examples_text}"

    if guide_text:
        system += f"\n\nГАЙД ПО ПОСТИНГУ:\n{guide_text}"

    return system

def generate_post(topic: str) -> str:
    system = build_system_prompt()
    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": f"Напиши пост на тему: {topic}"}
        ],
        max_tokens=600
    )
    return response.choices[0].message.content

def suggest_topics(count: int = 5) -> str:
    system = build_system_prompt()
    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": f"Предложи {count} идей для постов под этот канал. Просто список, без лишних слов."}
        ],
        max_tokens=300
    )
    return response.choices[0].message.content
