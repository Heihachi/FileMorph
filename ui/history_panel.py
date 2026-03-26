# FileMorph/ui/history_panel.py
from pathlib import Path

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QLabel,
    QTableWidget,
    QTableWidgetItem,
    QPushButton,
    QHBoxLayout,
    QMessageBox,
    QHeaderView
)

from utils.translations import tr


class HistoryPanel(QWidget):
    open_result_requested = pyqtSignal(int)
    open_folder_requested = pyqtSignal(int)
    repeat_requested = pyqtSignal(int)
    history_cleared = pyqtSignal()

    def __init__(self, history_manager):
        super().__init__()

        self.history_manager = history_manager
        self.current_language = "ru"

        self._setup_ui()
        self.apply_language(self.current_language)
        self.load_history()
    
    def _translate_status(self, status: str) -> str:
        normalized = status.strip().lower()

        aliases = {
            "success": "success",
            "успешно": "success",
            "error": "error",
            "ошибка": "error",
            "cancelled": "cancelled",
            "отменено": "cancelled",
        }

        normalized = aliases.get(normalized, normalized)

        status_map = {
            "success": {"ru": "Успешно", "en": "Success"},
            "error": {"ru": "Ошибка", "en": "Error"},
            "cancelled": {"ru": "Отменено", "en": "Cancelled"},
        }

        return status_map.get(normalized, {}).get(self.current_language, status)

    def _setup_ui(self):
        layout = QVBoxLayout()

        self.title_label = QLabel()
        self.title_label.setStyleSheet("font-size: 16px; font-weight: bold;")

        self.table = QTableWidget()
        self.table.setColumnCount(8)

        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(5, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(6, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(7, QHeaderView.ResizeMode.ResizeToContents)

        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self.table.verticalHeader().setVisible(False)

        buttons_layout = QHBoxLayout()
        self.refresh_button = QPushButton()
        self.clear_button = QPushButton()
        self.open_result_button = QPushButton()
        self.open_folder_button = QPushButton()
        self.repeat_button = QPushButton()

        buttons_layout.addWidget(self.refresh_button)
        buttons_layout.addWidget(self.clear_button)
        buttons_layout.addSpacing(20)
        buttons_layout.addWidget(self.open_result_button)
        buttons_layout.addWidget(self.open_folder_button)
        buttons_layout.addWidget(self.repeat_button)
        buttons_layout.addStretch()

        layout.addWidget(self.title_label)
        layout.addWidget(self.table)
        layout.addLayout(buttons_layout)
        self.setLayout(layout)

        self.refresh_button.clicked.connect(self.load_history)
        self.clear_button.clicked.connect(self.clear_history)
        self.open_result_button.clicked.connect(self._emit_open_result)
        self.open_folder_button.clicked.connect(self._emit_open_folder)
        self.repeat_button.clicked.connect(self._emit_repeat)

    def apply_language(self, language: str):
        self.current_language = language

        self.title_label.setText(tr(language, "history_title"))
        self.refresh_button.setText(tr(language, "refresh"))
        self.clear_button.setText(tr(language, "clear_history"))
        self.open_result_button.setText(tr(language, "open_result"))
        self.open_folder_button.setText(tr(language, "open_folder"))
        self.repeat_button.setText(tr(language, "repeat"))

        self.table.setHorizontalHeaderLabels([
            tr(language, "history_col_id"),
            tr(language, "history_col_source"),
            tr(language, "history_col_from"),
            tr(language, "history_col_to"),
            tr(language, "history_col_status"),
            tr(language, "history_col_result"),
            tr(language, "history_col_date"),
            tr(language, "history_col_duration"),
        ])

    def load_history(self):
        records = self.history_manager.get_all()
        self.table.setRowCount(len(records))

        for row_index, record in enumerate(records):
            source_name = Path(record["source_path"]).name if record["source_path"] else "-"
            target_name = Path(record["target_path"]).name if record["target_path"] else "-"

            values = [
                str(record["id"]),
                source_name,
                record["source_format"],
                record["target_format"],
                self._translate_status(record["status"]),
                target_name,
                record["created_at"],
                str(record["duration_ms"]),
            ]

            for col_index, value in enumerate(values):
                item = QTableWidgetItem(value)
                item.setTextAlignment(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft)

                if col_index == 1:
                    item.setToolTip(record["source_path"])
                elif col_index == 5:
                    item.setToolTip(record["target_path"])

                self.table.setItem(row_index, col_index, item)

    def clear_history(self):
        answer = QMessageBox.question(
            self,
            tr(self.current_language, "status_clear_history"),
            tr(self.current_language, "confirm_clear_history")
        )

        if answer != QMessageBox.StandardButton.Yes:
            return

        self.history_manager.clear()
        self.load_history()
        self.table.clearSelection()
        self.history_cleared.emit()

    def _get_selected_record_id(self) -> int | None:
        current_row = self.table.currentRow()
        if current_row < 0:
            return None

        id_item = self.table.item(current_row, 0)
        if id_item is None:
            return None

        try:
            return int(id_item.text())
        except ValueError:
            return None

    def _emit_open_result(self):
        record_id = self._get_selected_record_id()
        if record_id is not None:
            self.open_result_requested.emit(record_id)

    def _emit_open_folder(self):
        record_id = self._get_selected_record_id()
        if record_id is not None:
            self.open_folder_requested.emit(record_id)

    def _emit_repeat(self):
        record_id = self._get_selected_record_id()
        if record_id is not None:
            self.repeat_requested.emit(record_id)