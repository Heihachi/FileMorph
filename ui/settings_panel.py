# FileMorph/ui/settings_panel.py
from pathlib import Path

from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QLabel,
    QComboBox,
    QFormLayout,
    QSpinBox,
    QCheckBox,
    QPushButton,
    QGroupBox,
    QLineEdit,
    QHBoxLayout,
    QFileDialog
)

from utils.translations import tr


class SettingsPanel(QWidget):
    def __init__(self):
        super().__init__()
        self.current_language = "ru"
        self._setup_ui()
        self._connect_signals()
        self.apply_language(self.current_language)

    def _setup_ui(self):
        main_layout = QVBoxLayout()
        main_layout.setSpacing(12)

        self.title_label = QLabel()
        self.title_label.setStyleSheet("font-size: 18px; font-weight: bold;")

        self.format_group = QGroupBox()
        format_layout = QVBoxLayout()

        self.target_format_label = QLabel()
        self.target_format_combo = QComboBox()
        self.target_format_combo.addItem("")

        format_layout.addWidget(self.target_format_label)
        format_layout.addWidget(self.target_format_combo)
        self.format_group.setLayout(format_layout)

        self.image_group = QGroupBox()
        image_form = QFormLayout()

        self.width_spin = QSpinBox()
        self.width_spin.setRange(0, 10000)
        self.width_spin.setValue(0)

        self.height_spin = QSpinBox()
        self.height_spin.setRange(0, 10000)
        self.height_spin.setValue(0)

        self.quality_spin = QSpinBox()
        self.quality_spin.setRange(1, 100)
        self.quality_spin.setValue(90)

        self.rotate_combo = QComboBox()
        self.rotate_combo.addItems(["0", "90", "180", "270"])

        self.grayscale_checkbox = QCheckBox()

        self.width_label = QLabel()
        self.height_label = QLabel()
        self.quality_label = QLabel()
        self.rotate_label = QLabel()

        image_form.addRow(self.width_label, self.width_spin)
        image_form.addRow(self.height_label, self.height_spin)
        image_form.addRow(self.quality_label, self.quality_spin)
        image_form.addRow(self.rotate_label, self.rotate_combo)
        image_form.addRow("", self.grayscale_checkbox)
        self.image_group.setLayout(image_form)

        self.data_group = QGroupBox()
        data_form = QFormLayout()

        self.delimiter_input = QLineEdit(",")
        self.encoding_input = QLineEdit("utf-8")
        self.sheet_name_input = QLineEdit("Sheet1")

        self.delimiter_label = QLabel()
        self.encoding_label = QLabel()
        self.sheet_name_label = QLabel()

        data_form.addRow(self.delimiter_label, self.delimiter_input)
        data_form.addRow(self.encoding_label, self.encoding_input)
        data_form.addRow(self.sheet_name_label, self.sheet_name_input)
        self.data_group.setLayout(data_form)

        self.audio_group = QGroupBox()
        audio_form = QFormLayout()

        self.audio_bitrate_input = QLineEdit("192k")
        self.audio_sample_rate_input = QLineEdit("44100")

        self.audio_bitrate_label = QLabel()
        self.audio_sample_rate_label = QLabel()

        audio_form.addRow(self.audio_bitrate_label, self.audio_bitrate_input)
        audio_form.addRow(self.audio_sample_rate_label, self.audio_sample_rate_input)
        self.audio_group.setLayout(audio_form)

        self.video_group = QGroupBox()
        video_form = QFormLayout()

        self.video_fps_input = QLineEdit("")
        self.video_resolution_input = QLineEdit("")
        self.video_codec_combo = QComboBox()
        self.video_codec_combo.addItems(["", "libx264", "libx265", "libvpx-vp9"])

        self.video_fps_label = QLabel()
        self.video_resolution_label = QLabel()
        self.video_codec_label = QLabel()

        video_form.addRow(self.video_fps_label, self.video_fps_input)
        video_form.addRow(self.video_resolution_label, self.video_resolution_input)
        video_form.addRow(self.video_codec_label, self.video_codec_combo)
        self.video_group.setLayout(video_form)

        self.output_group = QGroupBox()
        output_layout = QVBoxLayout()

        row = QHBoxLayout()
        self.output_path_input = QLineEdit()
        self.browse_output_button = QPushButton()

        row.addWidget(self.output_path_input)
        row.addWidget(self.browse_output_button)

        output_layout.addLayout(row)
        self.output_group.setLayout(output_layout)
        
        self.ffmpeg_status_label = QLabel()
        self.ffmpeg_check_button = QPushButton("Проверить FFmpeg")
        self.ffmpeg_download_button = QPushButton("Скачать FFmpeg")

        main_layout.addWidget(self.ffmpeg_status_label)
        main_layout.addWidget(self.ffmpeg_check_button)
        main_layout.addWidget(self.ffmpeg_download_button)

        self.convert_button = QPushButton()
        self.convert_button.setMinimumHeight(42)
        self.convert_button.setStyleSheet("""
            QPushButton {
                font-size: 16px;
                font-weight: bold;
            }
        """)

        main_layout.addWidget(self.title_label)
        main_layout.addWidget(self.format_group)
        main_layout.addWidget(self.image_group)
        main_layout.addWidget(self.data_group)
        main_layout.addWidget(self.audio_group)
        main_layout.addWidget(self.video_group)
        main_layout.addWidget(self.output_group)
        main_layout.addStretch()
        main_layout.addWidget(self.convert_button)

        self.setLayout(main_layout)
        self.show_options_for_category(None)

    def _connect_signals(self):
        self.browse_output_button.clicked.connect(self.choose_output_folder)

    def apply_language(self, language: str):
        self.current_language = language

        self.title_label.setText(tr(language, "conversion_params"))
        self.format_group.setTitle(tr(language, "format_group"))
        self.target_format_label.setText(tr(language, "target_format"))

        self.image_group.setTitle(tr(language, "image_options"))
        self.width_label.setText(tr(language, "width"))
        self.height_label.setText(tr(language, "height"))
        self.quality_label.setText(tr(language, "quality"))
        self.rotate_label.setText(tr(language, "rotate"))
        self.grayscale_checkbox.setText(tr(language, "grayscale"))

        self.data_group.setTitle(tr(language, "data_options"))
        self.delimiter_label.setText(tr(language, "csv_delimiter"))
        self.encoding_label.setText(tr(language, "encoding"))
        self.sheet_name_label.setText(tr(language, "sheet_name"))

        self.audio_group.setTitle(tr(language, "audio_options"))
        self.audio_bitrate_label.setText(tr(language, "audio_bitrate"))
        self.audio_sample_rate_label.setText(tr(language, "audio_sample_rate"))

        self.video_group.setTitle(tr(language, "video_options"))
        self.video_fps_label.setText(tr(language, "video_fps"))
        self.video_resolution_label.setText(tr(language, "video_resolution"))
        self.video_codec_label.setText(tr(language, "video_codec"))

        self.output_group.setTitle(tr(language, "output_folder_group"))
        self.browse_output_button.setText(tr(language, "choose"))
        self.output_path_input.setPlaceholderText(tr(language, "output_placeholder"))
        self.convert_button.setText(tr(language, "convert"))

        self.width_spin.setSpecialValueText(tr(language, "no_change"))
        self.height_spin.setSpecialValueText(tr(language, "no_change"))

        if self.target_format_combo.count() == 0:
            self.target_format_combo.addItem(tr(language, "add_file_first"))
            
        if self.target_format_combo.count() == 1:
            current = self.target_format_combo.itemText(0).strip().lower()
            if current in {"add a file first", "сначала добавьте файл", "no available formats", "нет доступных форматов"}:
                self.target_format_combo.clear()
                self.target_format_combo.addItem(tr(language, "add_file_first"))

    def choose_output_folder(self):
        folder = QFileDialog.getExistingDirectory(self, tr(self.current_language, "output_folder_group"))
        if folder:
            self.output_path_input.setText(folder)

    def update_target_formats(self, formats: list[str]):
        self.target_format_combo.clear()

        if not formats:
            self.target_format_combo.addItem(tr(self.current_language, "no_formats"))
            return

        self.target_format_combo.addItems([fmt.upper() for fmt in formats])

    def show_options_for_category(self, category: str | None):
        self.image_group.setVisible(category == "image")
        self.data_group.setVisible(category == "data")
        self.audio_group.setVisible(category == "audio")
        self.video_group.setVisible(category == "video")

    def get_selected_target_format(self) -> str:
        return self.target_format_combo.currentText().strip().lower()

    def get_output_directory(self) -> Path | None:
        text = self.output_path_input.text().strip()
        if not text:
            return None
        return Path(text)

    def get_options(self, category: str | None) -> dict:
        if category == "image":
            return {
                "width": self.width_spin.value(),
                "height": self.height_spin.value(),
                "quality": self.quality_spin.value(),
                "rotate": int(self.rotate_combo.currentText()),
                "grayscale": self.grayscale_checkbox.isChecked(),
            }

        if category == "data":
            return {
                "delimiter": self.delimiter_input.text(),
                "encoding": self.encoding_input.text(),
                "sheet_name": self.sheet_name_input.text(),
            }

        if category == "audio":
            return {
                "audio_bitrate": self.audio_bitrate_input.text().strip() or "192k",
                "audio_sample_rate": self.audio_sample_rate_input.text().strip() or "44100",
            }

        if category == "video":
            return {
                "video_fps": self.video_fps_input.text().strip(),
                "video_resolution": self.video_resolution_input.text().strip(),
                "video_codec": self.video_codec_combo.currentText().strip(),
            }

        return {}