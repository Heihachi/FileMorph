# FileMorph/utils/theme_utils.py
from PyQt6.QtGui import QColor, QPalette
from PyQt6.QtWidgets import QApplication


def apply_light_theme(app: QApplication) -> None:
    app.setStyle("Fusion")
    app.setPalette(app.style().standardPalette())


def apply_dark_theme(app: QApplication) -> None:
    app.setStyle("Fusion")

    palette = QPalette()

    palette.setColor(QPalette.ColorRole.Window, QColor(45, 45, 45))
    palette.setColor(QPalette.ColorRole.WindowText, QColor(220, 220, 220))

    palette.setColor(QPalette.ColorRole.Base, QColor(30, 30, 30))
    palette.setColor(QPalette.ColorRole.AlternateBase, QColor(45, 45, 45))

    palette.setColor(QPalette.ColorRole.ToolTipBase, QColor(255, 255, 255))
    palette.setColor(QPalette.ColorRole.ToolTipText, QColor(255, 255, 255))

    palette.setColor(QPalette.ColorRole.Text, QColor(220, 220, 220))
    palette.setColor(QPalette.ColorRole.Button, QColor(53, 53, 53))
    palette.setColor(QPalette.ColorRole.ButtonText, QColor(220, 220, 220))

    palette.setColor(QPalette.ColorRole.BrightText, QColor(255, 80, 80))
    palette.setColor(QPalette.ColorRole.Highlight, QColor(42, 130, 218))
    palette.setColor(QPalette.ColorRole.HighlightedText, QColor(255, 255, 255))

    app.setPalette(palette)


def apply_theme(app: QApplication, theme_name: str) -> None:
    if theme_name == "dark":
        apply_dark_theme(app)
    else:
        apply_light_theme(app)