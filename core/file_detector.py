# FileMorph/core/file_detector.py
from pathlib import Path


IMAGE_FORMATS = {"jpg", "jpeg", "png", "webp", "bmp", "tiff"}
DOCUMENT_FORMATS = {"docx", "txt", "pdf"}
DATA_FORMATS = {"csv", "json", "xlsx"}
AUDIO_FORMATS = {"mp3", "wav", "flac", "ogg", "aac", "m4a"}
VIDEO_FORMATS = {"mp4", "avi", "mkv", "mov", "webm", "gif"}


def normalize_extension(path: Path) -> str:
    return path.suffix.lower().lstrip(".")


def detect_category(path: Path) -> str:
    ext = normalize_extension(path)

    if ext in IMAGE_FORMATS:
        return "image"

    if ext in DOCUMENT_FORMATS:
        return "document"

    if ext in DATA_FORMATS:
        return "data"

    if ext in AUDIO_FORMATS:
        return "audio"

    if ext in VIDEO_FORMATS:
        return "video"

    return "unknown"