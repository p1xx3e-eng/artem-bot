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

    for text_div in soup.select("div.text"):
        text = text_div.get_text(separator="\n").strip()
        if len(text) > 50:
            posts.append(text)

    return posts
