# FileMorph/workers/conversion_worker.py
from pathlib import Path
from typing import Any

from PyQt6.QtCore import QThread, pyqtSignal

from utils.file_utils import build_output_path


class ConversionWorker(QThread):
    progress_updated = pyqtSignal(int)
    status_updated = pyqtSignal(str)
    file_converted = pyqtSignal(str, str)
    conversion_done = pyqtSignal(dict)
    conversion_error = pyqtSignal(str)
    conversion_cancelled = pyqtSignal()

    def __init__(
        self,
        converter: Any,
        files: list[Path],
        output_dir: Path | None,
        target_format: str,
        options: dict
    ):
        super().__init__()
        self.converter = converter
        self.files = files
        self.output_dir = output_dir
        self.target_format = target_format
        self.options = options
        self._cancelled = False

    def cancel(self):
        self._cancelled = True

    def run(self):
        total = len(self.files)
        success_count = 0
        error_messages: list[str] = []
        converted_pairs: list[tuple[str, str]] = []

        if total == 0:
            self.conversion_error.emit("Список файлов пуст.")
            return

        forced_output_paths: dict[str, str] = self.options.get("_forced_output_paths", {})

        for index, src in enumerate(self.files, start=1):
            if self._cancelled:
                self.status_updated.emit("Конвертация отменена пользователем.")
                self.conversion_cancelled.emit()
                return

            try:
                self.status_updated.emit(f"Обработка {index} из {total}: {src.name}")

                forced_dst = forced_output_paths.get(str(src))
                if forced_dst:
                    dst = Path(forced_dst)
                else:
                    dst = build_output_path(src, self.output_dir, self.target_format)

                safe_options = dict(self.options)
                safe_options.pop("_forced_output_paths", None)

                self.converter.convert(src, dst, safe_options)

                success_count += 1
                converted_pairs.append((str(src), str(dst)))
                self.file_converted.emit(str(src), str(dst))

            except Exception as e:
                error_messages.append(f"{src.name}: {e}")

            progress = int(index / total * 100)
            self.progress_updated.emit(progress)

        result = {
            "success_count": success_count,
            "error_messages": error_messages,
            "converted_pairs": converted_pairs,
            "target_format": self.target_format,
            "total": total,
        }
        self.conversion_done.emit(result)