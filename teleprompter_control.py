import sys
from PyQt6.QtWidgets import (QApplication, QVBoxLayout, QWidget, QMainWindow, QToolBar, QMessageBox, QPlainTextEdit, QMenuBar, QFileDialog)
from PyQt6.QtCore import Qt, pyqtSignal, QFileInfo
from PyQt6.QtGui import QFont, QKeySequence, QAction, QIcon
import qtawesome as qta
from tkinter import Tk
from tkinter.filedialog import askopenfilename

from code_editor import CodeEditor
from teleprompter_display import TeleprompterDisplay
from settings_dialog import SettingsDialog

class TeleprompterControl(QMainWindow):
    text_changed = pyqtSignal(str)
    settings_changed = pyqtSignal(dict)
    play_pause_triggered = pyqtSignal()
    stop_triggered = pyqtSignal()
    toggle_fullscreen_triggered = pyqtSignal()

    def __init__(self):
        super().__init__()

        # Set ikon aplikasi
        self.setWindowIcon(QIcon("kode_terpisah/icon.ico"))

        self.current_settings = {
            'font': QFont("Arial", 48),
            'font_size': 48,
            'speed': 50,
            'word_wrap': True
        }

        self.initUI()
        self.current_file = None  # Track current file for Save functionality
        self.is_modified = False

        self.teleprompter_window = None

    def initUI(self):
        self.setWindowTitle("Teleprompter Control")
        self.setGeometry(100, 100, 800, 600)

        self.text_edit = CodeEditor()
        self.text_edit.setFont(QFont("Arial", 18))
        self.text_edit.textChanged.connect(self.mark_modified)  # Ini memerlukan metode mark_modified

        central_widget = QWidget()
        layout = QVBoxLayout(central_widget)
        layout.addWidget(self.text_edit)
        self.setCentralWidget(central_widget)

        menubar = self.menuBar()

        file_menu = menubar.addMenu("File")
        options_menu = menubar.addMenu("Options")
        help_menu = menubar.addMenu("Help")

        import_action = QAction('Import .txt', self)
        import_action.setShortcut(QKeySequence('Ctrl+I'))
        import_action.triggered.connect(self.import_text_file)
        file_menu.addAction(import_action)

        save_action = QAction('Save', self)
        save_action.setShortcut(QKeySequence('Ctrl+S'))
        save_action.triggered.connect(self.save_text)
        file_menu.addAction(save_action)

        save_as_action = QAction('Save As...', self)
        save_as_action.setShortcut(QKeySequence('Ctrl+Alt+S'))
        save_as_action.triggered.connect(self.save_text_as)
        file_menu.addAction(save_as_action)

        close_file_action = QAction('Close File', self)
        close_file_action.triggered.connect(self.close_file)
        file_menu.addAction(close_file_action)

        exit_action = QAction('Exit', self)
        exit_action.triggered.connect(self.exit_program)
        file_menu.addAction(exit_action)

        options_action = QAction('Settings', self)
        options_action.triggered.connect(self.open_settings_dialog)
        options_menu.addAction(options_action)

        close_screen_action = QAction('Close Screen', self)
        close_screen_action.triggered.connect(self.close_teleprompter_screen)
        options_menu.addAction(close_screen_action)

        word_wrap_action = QAction('Toggle Word Wrap', self)
        word_wrap_action.setCheckable(True)
        word_wrap_action.setChecked(self.current_settings['word_wrap'])
        word_wrap_action.triggered.connect(self.toggle_word_wrap)
        options_menu.addAction(word_wrap_action)

        about_action = QAction('About', self)
        about_action.triggered.connect(self.show_about_dialog)
        help_menu.addAction(about_action)

        toolbar = QToolBar("Control Toolbar", self)
        self.addToolBar(Qt.ToolBarArea.TopToolBarArea, toolbar)

        self.play_pause_action = QAction(qta.icon('fa.play'), "Play", self)
        self.play_pause_action.triggered.connect(self.play_pause_teleprompter)
        toolbar.addAction(self.play_pause_action)

        stop_action = QAction(qta.icon('fa.stop'), "Stop", self)
        stop_action.triggered.connect(self.stop_teleprompter)
        toolbar.addAction(stop_action)

        update_action = QAction(qta.icon('fa.edit'), "Update Teleprompter", self)
        update_action.triggered.connect(self.update_teleprompter)
        toolbar.addAction(update_action)

        fullscreen_action = QAction(qta.icon('fa.arrows-alt'), "Toggle Full-Screen", self)
        fullscreen_action.triggered.connect(self.toggle_fullscreen_on_teleprompter)
        toolbar.addAction(fullscreen_action)

    def mark_modified(self):
        if not self.is_modified:
            self.is_modified = True
            self.update_window_title()

    def update_window_title(self):
        if self.current_file:
            file_name = QFileInfo(self.current_file).fileName()
            if self.is_modified:
                self.setWindowTitle(f"*{file_name} - Teleprompter Control")
            else:
                self.setWindowTitle(f"{file_name} - Teleprompter Control")
        else:
            self.setWindowTitle("Teleprompter Control")

    def toggle_fullscreen_on_teleprompter(self):
        if self.teleprompter_window:
            self.toggle_fullscreen_triggered.emit()  # Emit signal to toggle full-screen on teleprompter window

    def toggle_word_wrap(self):
        self.current_settings['word_wrap'] = not self.current_settings['word_wrap']
        self.text_edit.setLineWrapMode(
            QPlainTextEdit.LineWrapMode.WidgetWidth if self.current_settings['word_wrap'] else QPlainTextEdit.LineWrapMode.NoWrap
        )

    def closeEvent(self, event):
        if self.is_modified:
            reply = QMessageBox.question(self, 'Unsaved Changes',
                                         "You have unsaved changes. Do you want to save them?",
                                         QMessageBox.StandardButton.Save | QMessageBox.StandardButton.Discard | QMessageBox.StandardButton.Cancel)
            if reply == QMessageBox.StandardButton.Save:
                self.save_text_as()
                event.ignore()  # Batalkan penutupan setelah menyimpan
            elif reply == QMessageBox.StandardButton.Cancel:
                event.ignore()  # Batalkan penutupan
            else:
                event.accept()  # Lanjutkan penutupan

        if event.isAccepted():
            if self.teleprompter_window:
                self.teleprompter_window.close()  # Menutup jendela teleprompter saat program utama ditutup
            event.accept()

    def update_teleprompter(self):
        text = self.text_edit.toPlainText()
        self.text_changed.emit(text)
        # Jangan update window title di sini agar tanda bintang tetap muncul jika belum disimpan

    def open_settings_dialog(self):
        dialog = SettingsDialog(self, self.current_settings)
        dialog.settings_changed.connect(self.update_settings)
        dialog.exec()

    def update_settings(self, settings):
        self.current_settings = settings  # Simpan pengaturan yang baru
        self.settings_changed.emit(settings)

    def import_text_file(self):
        if self.teleprompter_window and not self.teleprompter_window.is_paused:
            QMessageBox.warning(self, "Warning", "Please stop the teleprompter before importing a new file.")
            return

        Tk().withdraw()  # Sembunyikan jendela utama Tkinter
        file_path = askopenfilename(filetypes=[("Text Files", "*.txt")])
        if file_path:
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read()
                self.text_edit.setPlainText(content)
                self.current_file = file_path  # Set current file to imported file
                self.is_modified = False
                self.update_window_title()

    def save_text(self):
        if self.current_file:
            with open(self.current_file, 'w', encoding='utf-8') as file:
                file.write(self.text_edit.toPlainText())
            self.is_modified = False
            self.update_window_title()
        else:
            self.save_text_as()

    def save_text_as(self):
        options = QFileDialog.Options()
        options |= QFileDialog.Option.DontUseNativeDialog
        file_path, _ = QFileDialog.getSaveFileName(self, "Save As", "", 
                                                   "Text Files (*.txt);;All Files (*)", 
                                                   options=options)
        if file_path:
            with open(file_path, 'w', encoding='utf-8') as file:
                file.write(self.text_edit.toPlainText())
                self.current_file = file_path  # Set current file to saved file
                self.is_modified = False
                self.update_window_title()

    def close_file(self):
        if self.teleprompter_window and not self.teleprompter_window.is_paused:
            QMessageBox.warning(self, "Warning", "Please stop the teleprompter before closing the file.")
            return

        if self.is_modified:
            reply = QMessageBox.question(self, 'Unsaved Changes',
                                         "You have unsaved changes. Do you want to save them?",
                                         QMessageBox.StandardButton.Save | QMessageBox.StandardButton.Discard | QMessageBox.StandardButton.Cancel)
            if reply == QMessageBox.StandardButton.Save:
                self.save_text()
            elif reply == QMessageBox.StandardButton.Cancel:
                return

        self.text_edit.clear()
        self.current_file = None
        self.is_modified = False
        self.update_window_title()

    def exit_program(self):
        if self.teleprompter_window and not self.teleprompter_window.is_paused:
            QMessageBox.warning(self, "Warning", "Please stop the teleprompter before exiting the program.")
            return

        if self.is_modified:
            reply = QMessageBox.question(self, 'Unsaved Changes',
                                         "You have unsaved changes. Do you want to save them?",
                                         QMessageBox.StandardButton.Save | QMessageBox.StandardButton.Discard | QMessageBox.StandardButton.Cancel)
            if reply == QMessageBox.StandardButton.Save:
                self.save_text_as()
            elif reply == QMessageBox.StandardButton.Cancel:
                return

        self.close()

    def play_pause_teleprompter(self):
        if self.text_edit.toPlainText().strip() == "":
            QMessageBox.warning(self, "Warning", "Text is empty. Please import a file or type some text before starting the teleprompter.")
            return

        if not self.teleprompter_window:
            self.teleprompter_window = TeleprompterDisplay(self.current_settings)
            self.text_changed.connect(self.teleprompter_window.update_text)
            self.settings_changed.connect(self.teleprompter_window.update_settings)
            # Hubungkan sinyal ke fungsi teleprompter
            self.play_pause_triggered.connect(self.teleprompter_window.play_pause)
            self.stop_triggered.connect(self.teleprompter_window.stop)
            self.toggle_fullscreen_triggered.connect(self.teleprompter_window.toggle_fullscreen)  # Hubungkan full-screen signal ke layar baca
            # Kirimkan teks saat pertama kali play ditekan
            self.update_teleprompter()
            self.teleprompter_window.show()

        self.play_pause_triggered.emit()  # Play atau Pause teleprompter

        # Toggle tombol play/pause
        if self.teleprompter_window.is_paused:
            self.play_pause_action.setIcon(qta.icon('fa.play'))
            self.play_pause_action.setText("Play")
        else:
            self.play_pause_action.setIcon(qta.icon('fa.pause'))
            self.play_pause_action.setText("Pause")

    def stop_teleprompter(self):
        if self.teleprompter_window:
            self.stop_triggered.emit()
            self.play_pause_action.setIcon(qta.icon('fa.play'))
            self.play_pause_action.setText("Play")  # Reset tombol ke "Play" setelah stop

    def close_teleprompter_screen(self):
        if self.teleprompter_window:
            self.stop_teleprompter()  # Pastikan teleprompter berhenti saat layar ditutup
            self.teleprompter_window.close()
            self.teleprompter_window = None  # Reset window reference

    def show_about_dialog(self):
        about_text = """
        <h3>Teleprompter Application</h3>
        <p>Version 1.0</p>
        <p>Developed by: Ilham Ripandi @lunox61official</p>
        <p>This is a simple teleprompter application built with PyQt and Python.</p>
        <p>If you like this project and want to support further development, consider making a donation:</p>
        <p><a href='https://saweria.co/Furryna'>Saweria</a> | <a href='https://paypal.me/IlhamRipandi'>PayPal</a></p>
        """
        QMessageBox.about(self, "About Teleprompter", about_text)


def main():
    app = QApplication(sys.argv)

    control_window = TeleprompterControl()

    control_window.show()

    sys.exit(app.exec())


if __name__ == '__main__':
    main()
