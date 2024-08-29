from PyQt6.QtWidgets import QDialog, QFormLayout, QFontComboBox, QSpinBox, QPushButton
from PyQt6.QtCore import pyqtSignal
from PyQt6.QtGui import QFont

class SettingsDialog(QDialog):
    settings_changed = pyqtSignal(dict)

    def __init__(self, parent=None, settings=None):
        super().__init__(parent)
        self.current_settings = settings or {}
        self.initUI()

    def initUI(self):
        self.setWindowTitle("Settings")
        self.setGeometry(300, 300, 300, 250)

        layout = QFormLayout()

        self.font_selector = QFontComboBox(self)
        self.font_selector.setCurrentFont(self.current_settings.get('font', QFont("Arial")))
        layout.addRow("Font:", self.font_selector)

        self.font_size_selector = QSpinBox(self)
        self.font_size_selector.setMinimum(10)
        self.font_size_selector.setMaximum(200)
        self.font_size_selector.setValue(self.current_settings.get('font_size', 48))
        layout.addRow("Font Size:", self.font_size_selector)

        self.speed_selector = QSpinBox(self)
        self.speed_selector.setMinimum(10)
        self.speed_selector.setMaximum(200)
        self.speed_selector.setValue(self.current_settings.get('speed', 50))
        layout.addRow("Scroll Speed:", self.speed_selector)

        apply_button = QPushButton("Apply", self)
        apply_button.clicked.connect(self.apply_settings)
        layout.addWidget(apply_button)

        self.setLayout(layout)

    def apply_settings(self):
        settings = {
            'font': self.font_selector.currentFont(),
            'font_size': self.font_size_selector.value(),
            'speed': self.speed_selector.value()
        }
        self.settings_changed.emit(settings)
        self.close()
