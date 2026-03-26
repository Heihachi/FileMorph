# FileMorph/main.py
import sys

from PyQt6.QtWidgets import QApplication

from ui.main_window import MainWindow
from core.settings_manager import SettingsManager
from utils.theme_utils import apply_theme


def main():
    app = QApplication(sys.argv)

    settings_manager = SettingsManager()
    settings = settings_manager.load()
    apply_theme(app, settings.get("theme", "light"))

    window = MainWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()