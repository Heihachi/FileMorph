# FileMorph/ui/drop_zone.py
from pathlib import Path

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QPixmap
from PyQt6.QtWidgets import QLabel


class DropZone(QLabel):
    files_dropped = pyqtSignal(list)

    def __init__(self):
        super().__init__()

        self._preview_path: Path | None = None
        self._placeholder_text = "Drop files here"
        self._message_mode = False

        self.setAcceptDrops(True)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setMinimumHeight(220)
        self.setWordWrap(True)
        self.setMargin(14)

        self._default_style = """
            QLabel {
                border: 2px dashed #8a8a8a;
                border-radius: 14px;
                font-size: 15px;
                padding: 20px;
                background-color: rgba(255, 255, 255, 0.55);
                color: #444;
            }
        """

        self._hover_style = """
            QLabel {
                border: 2px dashed #2d89ef;
                border-radius: 14px;
                font-size: 15px;
                padding: 20px;
                background-color: rgba(45, 137, 239, 0.10);
                color: #222;
            }
        """

        self._message_style = """
            QLabel {
                border: 1px solid #909090;
                border-radius: 14px;
                font-size: 14px;
                padding: 16px;
                background-color: rgba(255, 255, 255, 0.65);
                color: #333;
            }
        """

        self.setStyleSheet(self._default_style)
        self.show_placeholder()

    def set_placeholder_text(self, text: str):
        self._placeholder_text = text
        if self._preview_path is None and not self._message_mode:
            self.show_placeholder()

    def show_placeholder(self):
        self._preview_path = None
        self._message_mode = False
        self.clear()
        self.setPixmap(QPixmap())
        self.setText(self._placeholder_text)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setStyleSheet(self._default_style)

    def show_message(self, text: str):
        self._preview_path = None
        self._message_mode = True
        self.clear()
        self.setPixmap(QPixmap())
        self.setText(text)
        self.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
        self.setStyleSheet(self._message_style)

    def set_preview(self, image_path: Path):
        if not image_path.exists():
            self.show_message("File not found.")
            return

        pixmap = QPixmap(str(image_path))
        if pixmap.isNull():
            self.show_message("Failed to load preview.")
            return

        self._preview_path = image_path
        self._message_mode = False
        self.clear()
        self.setText("")
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setStyleSheet(self._default_style)

        scaled = pixmap.scaled(
            max(100, self.width() - 24),
            max(100, self.height() - 24),
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation
        )
        self.setPixmap(scaled)

    def resizeEvent(self, event):
        super().resizeEvent(event)

        if self._preview_path is not None and self._preview_path.exists():
            self.set_preview(self._preview_path)

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
            if not self._message_mode and self._preview_path is None:
                self.setStyleSheet(self._hover_style)
        else:
            event.ignore()

    def dragLeaveEvent(self, event):
        if not self._message_mode and self._preview_path is None:
            self.setStyleSheet(self._default_style)
        event.accept()

    def dropEvent(self, event):
        if not self._message_mode and self._preview_path is None:
            self.setStyleSheet(self._default_style)

        mime_data = event.mimeData()
        if not mime_data.hasUrls():
            event.ignore()
            return

        file_paths = []
        for url in mime_data.urls():
            local_file = url.toLocalFile()
            if local_file:
                path = Path(local_file)
                if path.is_file():
                    file_paths.append(path)

        if file_paths:
            self.files_dropped.emit(file_paths)

        event.acceptProposedAction()