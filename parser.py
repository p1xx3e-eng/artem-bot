import fitz  # PyMuPDF
from bs4 import BeautifulSoup

def parse_pdf(file_bytes: bytes) -> str:
    doc = fitz.open(stream=file_bytes, filetype="pdf")
    text = ""
    for page in doc:
        text += page.get_text()
    return text.strip()

def parse_telegram_html(file_bytes: bytes) -> list[str]:
    """Парсит HTML-экспорт Telegram-канала, возвращает список текстов постов."""
    soup = BeautifulSoup(file_bytes, "html.parser")
    posts = []

    # Telegram export: посты в div.message
    for msg in soup.select("div.message"):
        text_div = msg.select_one("div.text")
        if text_div:
            text = text_div.get_text(separator="\n").strip()
            if len(text) > 50:  # пропускаем совсем короткие
                posts.append(text)

    return posts
