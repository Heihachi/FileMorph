# FileMorph/ui/main_window.py
from datetime import datetime
import time
from pathlib import Path

from PyQt6.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QFileDialog,
    QLabel,
    QTabWidget,
    QSplitter,
    QMessageBox,
    QStyle,
    QStatusBar
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon

from utils.ffmpeg_checker import find_ffmpeg, get_ffmpeg_version
import webbrowser

from ui.drop_zone import DropZone
from ui.settings_panel import SettingsPanel
from ui.history_panel import HistoryPanel
from ui.progress_widget import ProgressWidget

from core.file_detector import detect_category, normalize_extension
from core.format_registry import FormatRegistry
from core.history_manager import HistoryManager
from core.settings_manager import SettingsManager

from converters.image_converter import ImageConverter
from converters.document_converter import DocumentConverter
from converters.data_converter import DataConverter
from converters.audio_converter import AudioConverter
from converters.video_converter import VideoConverter

from utils.app_paths import get_asset_path
from utils.file_utils import open_path, build_output_path, unique_output_path
from utils.preview_utils import build_text_preview
from utils.ffmpeg_checker import is_ffmpeg_available
from utils.theme_utils import apply_theme
from utils.translations import tr
from workers.conversion_worker import ConversionWorker


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        from PyQt6.QtGui import QIcon
        self.setWindowIcon(QIcon(str(get_asset_path("assets", "logo.png"))))

        self.files: list[Path] = []
        self.current_category: str | None = None
        self.registry = FormatRegistry()
        self.history_manager = HistoryManager()
        self.settings_manager = SettingsManager()
        self.settings = self.settings_manager.load()
        self.current_language = self.settings.get("language", "ru")

        self.worker: ConversionWorker | None = None
        self.last_converted_outputs: dict[str, str] = {}
        self.conversion_started_at: float | None = None
        self.pending_output_paths: dict[str, str] = {}

        self.setMinimumSize(860, 560)
        self.resize(1100, 720)

        self._setup_ui()
        self._connect_signals()

    def _setup_ui(self):
        self._create_menu()

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        root_layout = QVBoxLayout()
        central_widget.setLayout(root_layout)

        top_splitter = QSplitter(Qt.Orientation.Horizontal)

        left_panel = self._build_left_panel()
        right_panel = self._build_right_panel()

        top_splitter.addWidget(left_panel)
        top_splitter.addWidget(right_panel)
        top_splitter.setSizes([620, 360])

        self.bottom_tabs = QTabWidget()
        self.history_panel = HistoryPanel(self.history_manager)
        self.progress_widget = ProgressWidget()

        self.bottom_tabs.addTab(self.history_panel, "")
        self.bottom_tabs.addTab(self.progress_widget, "")

        root_layout.addWidget(top_splitter, stretch=3)
        root_layout.addWidget(self.bottom_tabs, stretch=2)

        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)

        self._apply_saved_settings_to_ui()
        self._apply_language()
        self._update_button_states()
        self._set_status_message(tr(self.current_language, "statusbar_ready"))
        self.update_ffmpeg_status_silent()

    def _create_menu(self):
        menu_bar = self.menuBar()
        menu_bar.clear()

        self.file_menu = menu_bar.addMenu("")
        self.settings_menu = menu_bar.addMenu("")
        self.help_menu = menu_bar.addMenu("")

        self.open_file_action = self.file_menu.addAction("")
        self.open_folder_action = self.file_menu.addAction("")
        self.file_menu.addSeparator()
        self.exit_action = self.file_menu.addAction("")

        self.theme_action = self.settings_menu.addAction("")
        self.language_menu = self.settings_menu.addMenu("")
        self.language_ru_action = self.language_menu.addAction("")
        self.language_en_action = self.language_menu.addAction("")

        self.about_action = self.help_menu.addAction("")

    def _build_left_panel(self) -> QWidget:
        panel = QWidget()
        layout = QVBoxLayout()
        panel.setLayout(layout)

        self.files_title_label = QLabel()
        self.files_title_label.setStyleSheet("font-size: 18px; font-weight: bold;")

        self.drop_zone = DropZone()
        self.file_list = QListWidget()

        buttons_layout = QHBoxLayout()
        self.open_file_button = QPushButton()
        self.remove_selected_button = QPushButton()
        self.clear_all_button = QPushButton()

        buttons_layout.addWidget(self.open_file_button)
        buttons_layout.addWidget(self.remove_selected_button)
        buttons_layout.addWidget(self.clear_all_button)

        layout.addWidget(self.files_title_label)
        layout.addWidget(self.drop_zone)
        layout.addWidget(self.file_list)
        layout.addLayout(buttons_layout)

        return panel

    def _build_right_panel(self) -> QWidget:
        self.settings_panel = SettingsPanel()
        return self.settings_panel
    
    def check_ffmpeg(self):
        path = find_ffmpeg()

        if not path:
            QMessageBox.warning(
                self,
                "FFmpeg",
                "FFmpeg не найден в системе."
            )
            self.settings_panel.ffmpeg_status_label.setText("❌ FFmpeg не найден")
            return

        version = get_ffmpeg_version() or "версия неизвестна"

        self.settings_panel.ffmpeg_status_label.setText(f"✅ {version}")

        QMessageBox.information(
            self,
            "FFmpeg найден",
            f"Путь:\n{path}\n\n{version}"
        )
    
    def update_ffmpeg_status_silent(self):
        path = find_ffmpeg()

        if not path:
            self.settings_panel.ffmpeg_status_label.setText("❌ FFmpeg не найден")
            return

        version = get_ffmpeg_version()
        if version:
            self.settings_panel.ffmpeg_status_label.setText(f"✅ {version}")
        else:
            self.settings_panel.ffmpeg_status_label.setText("✅ FFmpeg найден")

    def download_ffmpeg(self):
        webbrowser.open("https://www.gyan.dev/ffmpeg/builds/")

    def _connect_signals(self):
        self.drop_zone.files_dropped.connect(self.add_files)

        self.open_file_button.clicked.connect(self.open_files_dialog)
        self.remove_selected_button.clicked.connect(self.remove_selected_file)
        self.clear_all_button.clicked.connect(self.clear_files)

        self.open_file_action.triggered.connect(self.open_files_dialog)
        self.open_folder_action.triggered.connect(self.open_files_dialog)
        self.exit_action.triggered.connect(self.close)

        self.about_action.triggered.connect(self.show_about_dialog)
        self.settings_panel.convert_button.clicked.connect(self.convert_files)

        self.file_list.currentItemChanged.connect(self.on_file_selection_changed)
        self.file_list.itemDoubleClicked.connect(self.open_selected_file)
        self.progress_widget.cancel_button.clicked.connect(self.cancel_conversion)

        self.history_panel.open_result_requested.connect(self.open_history_result)
        self.history_panel.open_folder_requested.connect(self.open_history_folder)
        self.history_panel.repeat_requested.connect(self.repeat_history_conversion)
        self.history_panel.history_cleared.connect(lambda: self._set_status_message(
            tr(self.current_language, "statusbar_history_cleared")
        ))

        self.theme_action.triggered.connect(self.toggle_theme)
        self.language_ru_action.triggered.connect(lambda: self.set_language("ru"))
        self.language_en_action.triggered.connect(lambda: self.set_language("en"))
        
        self.file_list.itemSelectionChanged.connect(self._update_button_states)
        
        self.settings_panel.ffmpeg_check_button.clicked.connect(self.check_ffmpeg)
        self.settings_panel.ffmpeg_download_button.clicked.connect(self.download_ffmpeg)

    def _apply_saved_settings_to_ui(self):
        app = QApplication.instance()
        if app is not None:
            apply_theme(app, self.settings.get("theme", "light"))

        self.current_language = self.settings.get("language", "ru")

        output_mode = self.settings.get("output_mode", "source_folder")
        output_folder = self.settings.get("output_folder", "")

        if output_mode == "custom_folder" and output_folder:
            self.settings_panel.output_path_input.setText(output_folder)
        else:
            self.settings_panel.output_path_input.clear()

    def _apply_language(self):
        lang = self.current_language

        self.setWindowTitle(tr(lang, "app_title"))
        self.file_menu.setTitle(tr(lang, "file_menu"))
        self.settings_menu.setTitle(tr(lang, "settings"))
        self.help_menu.setTitle(tr(lang, "help"))

        self.open_file_action.setText(tr(lang, "open_file"))
        self.open_folder_action.setText(tr(lang, "open_files"))
        self.exit_action.setText(tr(lang, "exit"))
        self.theme_action.setText(tr(lang, "theme"))
        self.language_menu.setTitle(tr(lang, "language"))
        self.language_ru_action.setText(tr(lang, "lang_ru"))
        self.language_en_action.setText(tr(lang, "lang_en"))
        self.about_action.setText(tr(lang, "about"))

        self.files_title_label.setText(tr(lang, "files"))
        self.open_file_button.setText(tr(lang, "open_file"))
        self.remove_selected_button.setText(tr(lang, "remove_selected"))
        self.clear_all_button.setText(tr(lang, "clear_list"))

        self.bottom_tabs.setTabText(0, tr(lang, "history"))
        self.bottom_tabs.setTabText(1, tr(lang, "progress"))

        self.drop_zone.set_placeholder_text(tr(lang, "drop_placeholder"))
        self.settings_panel.apply_language(lang)
        self.history_panel.apply_language(lang)
        self.progress_widget.apply_language(lang)

        self._update_format_options()
        self._update_button_states()
        self._set_status_message(tr(lang, "statusbar_ready"))

    def _set_status_message(self, text: str):
        self.statusBar().showMessage(text, 5000)

    def _save_current_settings(self):
        output_folder = self.settings_panel.output_path_input.text().strip()

        if output_folder:
            output_mode = "custom_folder"
        else:
            output_mode = "source_folder"

        self.settings["output_mode"] = output_mode
        self.settings["output_folder"] = output_folder
        self.settings["language"] = self.current_language
        self.settings_manager.save(self.settings)

    def toggle_theme(self):
        current_theme = self.settings.get("theme", "light")
        new_theme = "dark" if current_theme == "light" else "light"

        self.settings["theme"] = new_theme
        self.settings_manager.save(self.settings)

        app = QApplication.instance()
        if app is not None:
            apply_theme(app, new_theme)

        self._set_status_message(
            tr(self.current_language, "statusbar_theme_changed", theme=new_theme)
        )

    def set_language(self, language_code: str):
        self.current_language = language_code
        self.settings["language"] = language_code
        self.settings_manager.save(self.settings)
        self._apply_language()
        self._set_status_message(
            tr(self.current_language, "statusbar_language_changed", lang=language_code.upper())
        )

    def _update_button_states(self):
        busy = self.worker is not None and self.worker.isRunning()
        has_files = bool(self.files)
        has_selection = bool(self.file_list.selectedItems())

        self.open_file_button.setEnabled(not busy)
        self.open_file_action.setEnabled(not busy)
        self.open_folder_action.setEnabled(not busy)

        self.remove_selected_button.setEnabled(not busy and has_selection)
        self.clear_all_button.setEnabled(not busy and has_files)

        self.settings_panel.setEnabled(not busy and has_files)
        self.settings_panel.convert_button.setEnabled(not busy and has_files)

        self.progress_widget.set_cancel_enabled(busy)
        
    def closeEvent(self, event):
        if self.worker is not None and self.worker.isRunning():
            answer = QMessageBox.question(
                self,
                tr(self.current_language, "status_conversion_running"),
                "Конвертация ещё выполняется.\n\nЗакрыть приложение и отменить задачу?"
            )
            if answer != QMessageBox.StandardButton.Yes:
                event.ignore()
                return

            self.worker.cancel()
            self.worker.wait(3000)

        event.accept()

    def open_files_dialog(self):
        files, _ = QFileDialog.getOpenFileNames(
            self,
            tr(self.current_language, "open_files")
        )

        if files:
            path_list = [Path(file_path) for file_path in files]
            self.add_files(path_list)

    def add_files(self, paths: list[Path]):
        if not paths:
            return

        new_categories = set()

        for path in paths:
            category = detect_category(path)
            if category == "unknown":
                QMessageBox.warning(
                    self,
                    tr(self.current_language, "status_unsupported_format"),
                    tr(self.current_language, "warn_unsupported_format", name=path.name)
                )
                return
            new_categories.add(category)

        if len(new_categories) > 1:
            QMessageBox.warning(
                self,
                tr(self.current_language, "status_mixed_types"),
                tr(self.current_language, "warn_mixed_types")
            )
            return

        incoming_category = next(iter(new_categories))

        if self.files and self.current_category and incoming_category != self.current_category:
            QMessageBox.warning(
                self,
                tr(self.current_language, "status_incompatible_files"),
                tr(self.current_language, "warn_incompatible_files")
            )
            return

        added_any = False

        for path in paths:
            if path not in self.files:
                self.files.append(path)
                self._add_file_to_list_widget(path)
                added_any = True

        self.current_category = incoming_category
        self._update_format_options()

        if added_any and self.file_list.count() > 0 and self.file_list.currentRow() == -1:
            self.file_list.setCurrentRow(0)

        self._update_button_states()
        self._set_status_message(
            tr(self.current_language, "statusbar_files_loaded", count=len(self.files))
        )

    def _update_format_options(self):
        if not hasattr(self, "settings_panel"):
            return

        if not self.files:
            self.current_category = None
            self.settings_panel.update_target_formats([])
            self.settings_panel.show_options_for_category(None)
            self.drop_zone.show_placeholder()
            return

        first_file = self.files[0]
        extension = normalize_extension(first_file)

        output_formats = self.registry.get_output_formats(extension)
        self.settings_panel.update_target_formats(output_formats)
        self.settings_panel.show_options_for_category(self.current_category)

    def _add_file_to_list_widget(self, path: Path):
        size_kb = path.stat().st_size / 1024 if path.exists() else 0
        ext = normalize_extension(path)
        item_text = f"{path.name}    |    {ext.upper()}    |    {size_kb:.1f} KB"

        item = QListWidgetItem(item_text)
        item.setData(Qt.ItemDataRole.UserRole, str(path))
        item.setIcon(self._get_icon_for_file(path))

        self.file_list.addItem(item)

    def _get_icon_for_file(self, path: Path) -> QIcon:
        category = detect_category(path)

        if category == "image":
            return self.style().standardIcon(QStyle.StandardPixmap.SP_FileDialogDetailedView)
        if category == "document":
            return self.style().standardIcon(QStyle.StandardPixmap.SP_FileDialogContentsView)
        if category == "data":
            return self.style().standardIcon(QStyle.StandardPixmap.SP_DriveHDIcon)
        if category == "audio":
            return self.style().standardIcon(QStyle.StandardPixmap.SP_MediaVolume)
        if category == "video":
            return self.style().standardIcon(QStyle.StandardPixmap.SP_MediaPlay)

        return self.style().standardIcon(QStyle.StandardPixmap.SP_FileIcon)

    def on_file_selection_changed(self, current: QListWidgetItem | None, previous: QListWidgetItem | None):
        _ = previous

        if current is None:
            if self.files:
                self.drop_zone.show_message(tr(self.current_language, "file_not_selected"))
            else:
                self.drop_zone.show_placeholder()
            self._update_button_states()
            return

        file_path_str = current.data(Qt.ItemDataRole.UserRole)
        selected_path = Path(file_path_str)

        self._update_preview(selected_path)
        self._update_button_states()

    def _update_preview(self, path: Path):
        category = detect_category(path)

        if category == "image":
            self.drop_zone.set_preview(path)
            return

        if category == "document":
            try:
                preview_text = build_text_preview(path)
                self.drop_zone.show_message(preview_text)
            except Exception as e:
                self.drop_zone.show_message(
                    tr(self.current_language, "document_preview_failed", name=path.name, error=e)
                )
            return

        if category in ("audio", "video"):
            self.drop_zone.show_message(
                tr(self.current_language, "preview_audio_video", name=path.name)
            )
            return

        if category == "data":
            self.drop_zone.show_message(
                tr(self.current_language, "preview_data", name=path.name)
            )
            return

        self.drop_zone.show_message(
            tr(self.current_language, "preview_not_available", name=path.name)
        )

    def open_selected_file(self, item: QListWidgetItem):
        file_path_str = item.data(Qt.ItemDataRole.UserRole)
        if not file_path_str:
            return

        path = Path(file_path_str)

        try:
            open_path(path)
        except Exception as e:
            QMessageBox.critical(
                self,
                tr(self.current_language, "status_file_open_failed"),
                f"{path.name}\n\n{e}"
            )

    def remove_selected_file(self):
        if self.worker is not None and self.worker.isRunning():
            QMessageBox.information(
                self,
                tr(self.current_language, "status_conversion_running"),
                tr(self.current_language, "warn_conversion_running")
            )
            return

        selected_items = self.file_list.selectedItems()
        if not selected_items:
            return

        rows_to_remove = []

        for item in selected_items:
            file_path_str = item.data(Qt.ItemDataRole.UserRole)
            file_path = Path(file_path_str)

            if file_path in self.files:
                self.files.remove(file_path)

            rows_to_remove.append(self.file_list.row(item))

        for row in sorted(rows_to_remove, reverse=True):
            self.file_list.takeItem(row)

        if not self.files:
            self.current_category = None
            self.drop_zone.show_placeholder()
        else:
            self.file_list.setCurrentRow(0)

        self._update_format_options()
        self._update_button_states()

    def clear_files(self):
        if self.worker is not None and self.worker.isRunning():
            QMessageBox.information(
                self,
                tr(self.current_language, "status_conversion_running"),
                tr(self.current_language, "warn_conversion_running")
            )
            return

        self.files.clear()
        self.file_list.clear()
        self.current_category = None
        self.pending_output_paths.clear()
        self._update_format_options()
        self.drop_zone.show_placeholder()
        self._update_button_states()

    def _create_converter_for_current_category(self):
        if self.current_category == "image":
            return ImageConverter()

        if self.current_category == "document":
            return DocumentConverter()

        if self.current_category == "data":
            return DataConverter()

        if self.current_category == "audio":
            if not is_ffmpeg_available():
                QMessageBox.warning(
                    self,
                    "FFmpeg",
                    tr(self.current_language, "ffmpeg_missing_audio")
                )
                return None
            return AudioConverter()

        if self.current_category == "video":
            if not is_ffmpeg_available():
                QMessageBox.warning(
                    self,
                    "FFmpeg",
                    tr(self.current_language, "ffmpeg_missing_video")
                )
                return None
            return VideoConverter()

        return None

    def _prepare_output_paths(self, target_format: str, output_dir: Path | None) -> bool:
        self.pending_output_paths.clear()

        candidate_paths = []
        conflicts = []

        for src in self.files:
            dst = build_output_path(src, output_dir, target_format)
            
            if src.resolve() == dst.resolve():
                QMessageBox.warning(
                    self,
                    tr(self.current_language, "status_output_conflict"),
                    f"Исходный и выходной файл совпадают:\n{src}"
                )
                return False
            
            candidate_paths.append((src, dst))
            if dst.exists():
                conflicts.append(dst)

        if conflicts:
            if len(conflicts) == 1:
                answer = QMessageBox.question(
                    self,
                    tr(self.current_language, "status_confirm_overwrite"),
                    tr(self.current_language, "confirm_overwrite_single", path=str(conflicts[0]))
                )
                if answer != QMessageBox.StandardButton.Yes:
                    for src, dst in candidate_paths:
                        if dst.exists():
                            self.pending_output_paths[str(src)] = str(unique_output_path(dst))
                        else:
                            self.pending_output_paths[str(src)] = str(dst)
                    return True
            else:
                answer = QMessageBox.question(
                    self,
                    tr(self.current_language, "status_output_conflict"),
                    tr(self.current_language, "confirm_overwrite_many")
                )
                if answer == QMessageBox.StandardButton.Yes:
                    for src, dst in candidate_paths:
                        self.pending_output_paths[str(src)] = str(dst)
                    return True

                for src, dst in candidate_paths:
                    if dst.exists():
                        self.pending_output_paths[str(src)] = str(unique_output_path(dst))
                    else:
                        self.pending_output_paths[str(src)] = str(dst)
                return True

        for src, dst in candidate_paths:
            self.pending_output_paths[str(src)] = str(dst)

        return True

    def convert_files(self):
        if self.worker is not None and self.worker.isRunning():
            QMessageBox.information(
                self,
                tr(self.current_language, "status_already_running"),
                tr(self.current_language, "warn_already_running")
            )
            return

        if not self.files:
            QMessageBox.warning(
                self,
                tr(self.current_language, "status_no_files"),
                tr(self.current_language, "warn_no_files")
            )
            return

        target_format = self.settings_panel.get_selected_target_format()
        invalid_texts = {
            tr(self.current_language, "no_formats").lower(),
            tr(self.current_language, "add_file_first").lower(),
        }
        if not target_format or target_format in invalid_texts:
            QMessageBox.warning(
                self,
                tr(self.current_language, "status_no_format"),
                tr(self.current_language, "warn_no_format")
            )
            return

        output_dir = self.settings_panel.get_output_directory()
        if output_dir is not None:
            try:
                output_dir.mkdir(parents=True, exist_ok=True)
            except Exception as e:
                QMessageBox.critical(
                    self,
                    tr(self.current_language, "status_error"),
                    f"Не удалось создать папку вывода:\n{output_dir}\n\n{e}"
                )
                return
        options = self.settings_panel.get_options(self.current_category)
        self._save_current_settings()

        if not self._prepare_output_paths(target_format, output_dir):
            return
        
        missing_files = [str(path) for path in self.files if not path.exists()]
        if missing_files:
            QMessageBox.warning(
                self,
                tr(self.current_language, "status_error"),
                "Некоторые исходные файлы больше не существуют:\n\n" + "\n".join(missing_files[:10])
            )
            return

        converter = self._create_converter_for_current_category()
        if converter is None:
            return

        self.worker = ConversionWorker(
            converter=converter,
            files=self.files.copy(),
            output_dir=output_dir,
            target_format=target_format,
            options={**options, "_forced_output_paths": self.pending_output_paths}
        )

        self.worker.progress_updated.connect(self.on_progress_updated)
        self.worker.status_updated.connect(self.on_status_updated)
        self.worker.file_converted.connect(self.on_file_converted)
        self.worker.conversion_done.connect(self.on_conversion_done)
        self.worker.conversion_error.connect(self.on_conversion_error)
        self.worker.conversion_cancelled.connect(self.on_conversion_cancelled)

        self.progress_widget.start()
        self.bottom_tabs.setCurrentWidget(self.progress_widget)
        self.last_converted_outputs.clear()
        self.conversion_started_at = time.perf_counter()

        self._update_button_states()
        self._set_status_message(tr(self.current_language, "statusbar_conversion_started"))
        self.worker.start()

    def cancel_conversion(self):
        if self.worker is not None and self.worker.isRunning():
            self.worker.cancel()
            self.progress_widget.update_status(tr(self.current_language, "conversion_cancel_requested"))

    def on_progress_updated(self, value: int):
        self.progress_widget.update_progress(value)

    def on_status_updated(self, text: str):
        self.progress_widget.update_status(text)

    def on_file_converted(self, src: str, dst: str):
        self.last_converted_outputs[src] = dst

    def _save_history_records(
        self,
        converted_pairs: list[tuple[str, str]],
        error_messages: list[str],
        target_format: str,
        duration_ms: int
    ):
        created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        successful_sources = set()

        for src, dst in converted_pairs:
            src_path = Path(src)
            successful_sources.add(src)

            self.history_manager.add_record(
                source_path=src,
                source_format=normalize_extension(src_path),
                target_format=target_format.lower(),
                target_path=dst,
                status="Success",
                created_at=created_at,
                duration_ms=duration_ms
            )

        for error_text in error_messages:
            parts = error_text.split(":", 1)
            source_name = parts[0].strip() if parts else "unknown"

            matched_source_path = None
            for src_path in self.files:
                if src_path.name == source_name:
                    matched_source_path = src_path
                    break

            if matched_source_path is None:
                continue

            if str(matched_source_path) in successful_sources:
                continue

            self.history_manager.add_record(
                source_path=str(matched_source_path),
                source_format=normalize_extension(matched_source_path),
                target_format=target_format.lower(),
                target_path="",
                status="error",
                created_at=created_at,
                duration_ms=duration_ms
            )

    def on_conversion_done(self, result: dict):
        success_count = result.get("success_count", 0)
        error_messages = result.get("error_messages", [])
        target_format = result.get("target_format", "")
        converted_pairs = result.get("converted_pairs", [])

        duration_ms = 0
        if self.conversion_started_at is not None:
            duration_ms = int((time.perf_counter() - self.conversion_started_at) * 1000)
            self.conversion_started_at = None
        per_file_duration_ms = duration_ms
        if self.files:
            per_file_duration_ms = max(1, duration_ms // max(1, len(self.files)))

        self._save_history_records(
            converted_pairs=converted_pairs,
            error_messages=error_messages,
            target_format=target_format,
            duration_ms=per_file_duration_ms
        )

        self.history_panel.load_history()
        self.progress_widget.finish(
            f"{tr(self.current_language, 'status_ready')}. {success_count}/{len(self.files)}"
        )

        current_item = self.file_list.currentItem()
        if current_item is not None:
            src_path = current_item.data(Qt.ItemDataRole.UserRole)
            if src_path in self.last_converted_outputs:
                preview_path = Path(self.last_converted_outputs[src_path])
                if preview_path.exists() and detect_category(preview_path) == "image":
                    self.drop_zone.set_preview(preview_path)

        self._show_conversion_result(success_count, error_messages, target_format)

        self.worker = None
        self.pending_output_paths.clear()
        self._update_button_states()
        self._set_status_message(tr(self.current_language, "statusbar_conversion_done"))

    def on_conversion_error(self, error_text: str):
        duration_ms = 0
        if self.conversion_started_at is not None:
            duration_ms = int((time.perf_counter() - self.conversion_started_at) * 1000)
            self.conversion_started_at = None

        created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        for src_path in self.files:
            self.history_manager.add_record(
                source_path=str(src_path),
                source_format=normalize_extension(src_path),
                target_format=self.settings_panel.get_selected_target_format(),
                target_path="",
                status="error",
                created_at=created_at,
                duration_ms=duration_ms
            )

        self.history_panel.load_history()
        self.progress_widget.finish(tr(self.current_language, "status_error"))
        QMessageBox.critical(self, tr(self.current_language, "status_error"), error_text)

        self.worker = None
        self.pending_output_paths.clear()
        self._update_button_states()

    def on_conversion_cancelled(self):
        duration_ms = 0
        if self.conversion_started_at is not None:
            duration_ms = int((time.perf_counter() - self.conversion_started_at) * 1000)
            self.conversion_started_at = None

        created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        for src_path in self.files:
            if str(src_path) not in self.last_converted_outputs:
                self.history_manager.add_record(
                    source_path=str(src_path),
                    source_format=normalize_extension(src_path),
                    target_format=self.settings_panel.get_selected_target_format(),
                    target_path="",
                    status="cancelled",
                    created_at=created_at,
                    duration_ms=duration_ms
                )

        self.history_panel.load_history()
        self.progress_widget.finish(tr(self.current_language, "status_cancel"))
        QMessageBox.information(
            self,
            tr(self.current_language, "status_cancel"),
            tr(self.current_language, "msg_cancelled")
        )

        self.worker = None
        self.pending_output_paths.clear()
        self._update_button_states()
        self._set_status_message(tr(self.current_language, "statusbar_conversion_cancelled"))

    def _show_conversion_result(self, success_count: int, errors: list[str], target_format: str):
        if success_count > 0 and not errors:
            QMessageBox.information(
                self,
                tr(self.current_language, "status_ready"),
                tr(self.current_language, "msg_ready", count=success_count, fmt=target_format.upper())
            )
            return

        if success_count > 0 and errors:
            QMessageBox.warning(
                self,
                tr(self.current_language, "status_partial"),
                tr(
                    self.current_language,
                    "msg_partial",
                    success=success_count,
                    errors=len(errors),
                    details="\n".join(errors[:10])
                )
            )
            return

        QMessageBox.critical(
            self,
            tr(self.current_language, "status_error"),
            "\n".join(errors[:10]) if errors else tr(self.current_language, "msg_conversion_failed")
        )

    def open_history_result(self, record_id: int):
        record = self.history_manager.get_record_by_id(record_id)
        if not record:
            QMessageBox.warning(self, tr(self.current_language, "status_error"), tr(self.current_language, "msg_not_found_record"))
            return

        target_path = record.get("target_path", "")
        if not target_path:
            QMessageBox.information(self, tr(self.current_language, "status_error"), tr(self.current_language, "msg_no_result"))
            return

        path = Path(target_path)
        if not path.exists():
            QMessageBox.warning(self, tr(self.current_language, "status_error"), tr(self.current_language, "msg_result_missing", path=target_path))
            return

        try:
            open_path(path)
        except Exception as e:
            QMessageBox.critical(self, tr(self.current_language, "status_result_open_failed"), str(e))

    def open_history_folder(self, record_id: int):
        record = self.history_manager.get_record_by_id(record_id)
        if not record:
            QMessageBox.warning(self, tr(self.current_language, "status_error"), tr(self.current_language, "msg_not_found_record"))
            return

        target_path = record.get("target_path", "")
        source_path = record.get("source_path", "")
        folder_path = None

        if target_path:
            target = Path(target_path)
            if target.exists():
                folder_path = target.parent

        if folder_path is None and source_path:
            source = Path(source_path)
            if source.exists():
                folder_path = source.parent

        if folder_path is None or not folder_path.exists():
            QMessageBox.warning(self, tr(self.current_language, "status_error"), tr(self.current_language, "msg_folder_missing"))
            return

        try:
            open_path(folder_path)
        except Exception as e:
            QMessageBox.critical(self, tr(self.current_language, "status_folder_open_failed"), str(e))

    def repeat_history_conversion(self, record_id: int):
        if self.worker is not None and self.worker.isRunning():
            QMessageBox.information(
                self,
                tr(self.current_language, "status_already_running"),
                tr(self.current_language, "warn_already_running")
            )
            return

        record = self.history_manager.get_record_by_id(record_id)
        if not record:
            QMessageBox.warning(self, tr(self.current_language, "status_error"), tr(self.current_language, "msg_not_found_record"))
            return

        source_path = Path(record["source_path"])
        target_format = record["target_format"]

        if not source_path.exists():
            QMessageBox.warning(
                self,
                tr(self.current_language, "status_error"),
                tr(self.current_language, "msg_source_missing", path=source_path)
            )
            return

        self.clear_files()
        self.add_files([source_path])

        combo = self.settings_panel.target_format_combo
        for i in range(combo.count()):
            if combo.itemText(i).strip().lower() == target_format.lower():
                combo.setCurrentIndex(i)
                break

        self._save_current_settings()
        self.bottom_tabs.setCurrentWidget(self.progress_widget)
        self.convert_files()

    def show_about_dialog(self):
        msg = QMessageBox(self)
        msg.setWindowTitle(tr(self.current_language, "status_about"))
        msg.setIconPixmap(QIcon(str(get_asset_path("assets", "logo.png"))).pixmap(64, 64))

        msg.setText(f"""
<b>FileMorph</b><br><br>

Universal File Converter <br>
using PyQt6<br><br>

👨‍💻 <b>Developer:</b><br>
Jevgenij Anisimov<br><br>

⚙️ <b>Version:</b><br>
1.0 (MVP)
""")

        msg.exec()