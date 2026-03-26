# FileMorph/ui/progress_widget.py
from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QLabel,
    QProgressBar,
    QPushButton,
    QHBoxLayout
)

from utils.translations import tr


class ProgressWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.current_language = "ru"
        self._setup_ui()
        self.apply_language(self.current_language)

    def _setup_ui(self):
        layout = QVBoxLayout()

        self.title_label = QLabel()
        self.title_label.setStyleSheet("font-size: 16px; font-weight: bold;")

        self.status_label = QLabel()
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)

        buttons_row = QHBoxLayout()
        self.cancel_button = QPushButton()
        self.cancel_button.setEnabled(False)

        buttons_row.addWidget(self.cancel_button)
        buttons_row.addStretch()

        layout.addWidget(self.title_label)
        layout.addWidget(self.status_label)
        layout.addWidget(self.progress_bar)
        layout.addLayout(buttons_row)

        self.setLayout(layout)

    def apply_language(self, language: str):
        self.current_language = language
        self.title_label.setText(tr(language, "progress_title"))
        self.cancel_button.setText(tr(language, "cancel"))
        if self.progress_bar.value() == 0 and not self.cancel_button.isEnabled():
            self.status_label.setText(tr(language, "waiting_conversion"))

    def reset(self):
        self.status_label.setText(tr(self.current_language, "waiting_conversion"))
        self.progress_bar.setValue(0)
        self.cancel_button.setEnabled(False)

    def start(self):
        self.status_label.setText(tr(self.current_language, "preparing_conversion"))
        self.progress_bar.setValue(0)
        self.cancel_button.setEnabled(True)

    def update_status(self, text: str):
        self.status_label.setText(text)

    def update_progress(self, value: int):
        self.progress_bar.setValue(value)

    def finish(self, text: str):
        self.status_label.setText(text)
        self.cancel_button.setEnabled(False)

    def set_cancel_enabled(self, enabled: bool):
        self.cancel_button.setEnabled(enabled)