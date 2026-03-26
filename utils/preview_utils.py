# FileMorph/utils/preview_utils.py
from pathlib import Path

from docx import Document
from pypdf import PdfReader


def build_text_preview(path: Path, max_lines: int = 12, max_chars: int = 1200) -> str:

    try:
        ext = path.suffix.lower().lstrip(".")

        if ext == "txt":
            return _preview_txt(path, max_lines=max_lines, max_chars=max_chars)

        if ext == "docx":
            return _preview_docx(path, max_lines=max_lines, max_chars=max_chars)

        if ext == "pdf":
            return _preview_pdf(path, max_lines=max_lines, max_chars=max_chars)

        return "Превью для этого типа файла не поддерживается."
    except Exception as e:
        return f"Не удалось сформировать предпросмотр.\n\nОшибка: {e}"


def _preview_txt(path: Path, max_lines: int, max_chars: int) -> str:
    text = path.read_text(encoding="utf-8", errors="replace")
    return _truncate_preview_text(text, max_lines=max_lines, max_chars=max_chars)


def _preview_docx(path: Path, max_lines: int, max_chars: int) -> str:
    document = Document(path)
    lines = []

    for paragraph in document.paragraphs:
        text = paragraph.text.strip()
        if text:
            lines.append(text)

    preview_text = "\n".join(lines)
    return _truncate_preview_text(preview_text, max_lines=max_lines, max_chars=max_chars)


def _preview_pdf(path: Path, max_lines: int, max_chars: int) -> str:
    reader = PdfReader(str(path))
    parts = []

    for page in reader.pages[:3]:
        page_text = page.extract_text() or ""
        if page_text.strip():
            parts.append(page_text.strip())

    preview_text = "\n\n".join(parts)
    if not preview_text.strip():
        return "Не удалось извлечь текст из PDF.\n\nВозможно, это скан или PDF-изображение."

    return _truncate_preview_text(preview_text, max_lines=max_lines, max_chars=max_chars)


def _truncate_preview_text(text: str, max_lines: int, max_chars: int) -> str:

    text = text.replace("\r\n", "\n").replace("\r", "\n").strip()

    if not text:
        return "Файл пуст или не содержит читаемого текста."

    lines = text.split("\n")
    lines = [line for line in lines if line.strip()]

    truncated_lines = lines[:max_lines]
    preview = "\n".join(truncated_lines)

    if len(preview) > max_chars:
        preview = preview[:max_chars].rstrip() + "..."

    if len(lines) > max_lines:
        preview += "\n\n..."

    return preview