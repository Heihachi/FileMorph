# FileMorph/core/format_registry.py
from converters.audio_converter import AudioConverter
from converters.data_converter import DataConverter
from converters.document_converter import DocumentConverter
from converters.image_converter import ImageConverter
from converters.video_converter import VideoConverter


class FormatRegistry:
    def __init__(self):
        self._registry = {
            "jpg": ImageConverter,
            "jpeg": ImageConverter,
            "png": ImageConverter,
            "webp": ImageConverter,
            "bmp": ImageConverter,
            "tiff": ImageConverter,

            "docx": DocumentConverter,
            "txt": DocumentConverter,
            "pdf": DocumentConverter,

            "csv": DataConverter,
            "json": DataConverter,
            "xlsx": DataConverter,

            "mp3": AudioConverter,
            "wav": AudioConverter,
            "flac": AudioConverter,
            "ogg": AudioConverter,
            "aac": AudioConverter,
            "m4a": AudioConverter,

            "mp4": VideoConverter,
            "avi": VideoConverter,
            "mkv": VideoConverter,
            "mov": VideoConverter,
            "webm": VideoConverter,
            "gif": VideoConverter,
        }

        self._document_output_map = {
            "txt": ["docx", "pdf"],
            "docx": ["txt", "pdf"],
            "pdf": ["txt", "docx"],
        }

        self._data_output_map = {
            "csv": ["json", "xlsx"],
            "json": ["csv", "xlsx"],
            "xlsx": ["csv", "json"],
        }

        self._audio_output_map = {
            "mp3": ["wav", "flac", "ogg", "aac", "m4a"],
            "wav": ["mp3", "flac", "ogg", "aac", "m4a"],
            "flac": ["mp3", "wav", "ogg", "aac", "m4a"],
            "ogg": ["mp3", "wav", "flac", "aac", "m4a"],
            "aac": ["mp3", "wav", "flac", "ogg", "m4a"],
            "m4a": ["mp3", "wav", "flac", "ogg", "aac"],
        }

        self._video_output_map = {
            "mp4": ["avi", "mkv", "mov", "webm", "gif"],
            "avi": ["mp4", "mkv", "mov", "webm", "gif"],
            "mkv": ["mp4", "avi", "mov", "webm", "gif"],
            "mov": ["mp4", "avi", "mkv", "webm", "gif"],
            "webm": ["mp4", "avi", "mkv", "mov", "gif"],
            "gif": ["mp4", "avi", "mkv", "mov", "webm"],
        }

    def get_converter_class(self, extension: str):
        return self._registry.get(extension.lower())

    def get_output_formats(self, extension: str) -> list[str]:
        ext = extension.lower()
        converter_class = self.get_converter_class(ext)

        if converter_class is None:
            return []

        if converter_class is DocumentConverter:
            return self._document_output_map.get(ext, [])

        if converter_class is DataConverter:
            return self._data_output_map.get(ext, [])

        if converter_class is AudioConverter:
            return self._audio_output_map.get(ext, [])

        if converter_class is VideoConverter:
            return self._video_output_map.get(ext, [])

        converter = converter_class()
        return [fmt for fmt in converter.supported_output_formats if fmt != ext]