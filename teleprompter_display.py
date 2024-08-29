from PyQt6.QtWidgets import QWidget, QTextEdit, QVBoxLayout, QLabel
from PyQt6.QtCore import QTimer, QPoint, QTime, Qt
from PyQt6.QtGui import QFont, QTextCursor, QMouseEvent

class TeleprompterDisplay(QWidget):
    def __init__(self, settings):
        super().__init__()
        self.speed = settings.get('speed', 50)
        self.is_paused = True  # Awalnya teleprompter dalam keadaan berhenti
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.scroll_text)
        self.timer.setInterval(1000 // self.speed)  # Mengatur interval berdasarkan kecepatan
        self.dragging = False  # Flag untuk mendeteksi drag
        self.last_mouse_pos = QPoint()  # Posisi terakhir mouse

        # Timer untuk stopwatch
        self.stopwatch_timer = QTimer(self)
        self.stopwatch_timer.timeout.connect(self.update_stopwatch)
        self.stopwatch_time = QTime(0, 0)  # Mulai stopwatch dari 00:00
        self.initUI(settings)

    def initUI(self, settings):
        self.setWindowTitle("Teleprompter Display")
        self.setGeometry(950, 100, 800, 600)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)

        self.text_display = QTextEdit(self)
        font = settings.get('font', QFont("Arial", 48))
        font_size = settings.get('font_size', 48)
        font.setPointSize(font_size)
        self.text_display.setFont(font)
        self.text_display.setReadOnly(True)
        self.text_display.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        # Inisialisasi label stopwatch
        self.stopwatch_label = QLabel(self)
        self.stopwatch_label.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.stopwatch_label.setText(self.stopwatch_time.toString("mm:ss"))

        layout = QVBoxLayout()
        layout.addWidget(self.text_display)
        layout.addWidget(self.stopwatch_label)  # Tambahkan label stopwatch ke layout
        self.setLayout(layout)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_F11:
            self.toggle_fullscreen()

    def toggle_fullscreen(self):
        if self.isFullScreen():
            self.showNormal()
        else:
            self.showFullScreen()

    def update_text(self, text):
        self.text_display.setText(text)
        self.text_display.moveCursor(QTextCursor.MoveOperation.Start)

    def update_settings(self, settings):
        font = settings.get('font', QFont("Arial", 48))
        font_size = settings.get('font_size', 48)
        font.setPointSize(font_size)
        self.text_display.setFont(font)

        if 'speed' in settings:
            self.speed = settings['speed']
            self.timer.setInterval(1000 // self.speed)  # Perbarui interval timer

    def scroll_text(self):
        if not self.is_paused:
            current_scroll_value = self.text_display.verticalScrollBar().value()
            max_scroll_value = self.text_display.verticalScrollBar().maximum()

            if current_scroll_value < max_scroll_value:
                self.text_display.verticalScrollBar().setValue(current_scroll_value + 1)
            else:
                self.finish_scrolling()

    def finish_scrolling(self):
        self.timer.stop()
        self.stopwatch_timer.stop()
        self.is_paused = True

    def play_pause(self):
        if self.is_paused:
            self.is_paused = False
            self.timer.start()  # Memulai timer untuk scroll
            self.stopwatch_timer.start(1000)  # Memulai stopwatch dengan interval 1 detik
        else:
            self.is_paused = True
            self.timer.stop()  # Menghentikan timer untuk menghentikan scroll
            self.stopwatch_timer.stop()  # Jeda stopwatch

    def stop(self):
        self.is_paused = True
        self.timer.stop()  # Menghentikan timer
        self.text_display.moveCursor(QTextCursor.MoveOperation.Start)
        self.text_display.verticalScrollBar().setValue(0)

        self.stopwatch_timer.stop()  # Menghentikan stopwatch
        self.stopwatch_time = QTime(0, 0)  # Reset stopwatch
        self.stopwatch_label.setText(self.stopwatch_time.toString("mm:ss"))

    def update_stopwatch(self):
        self.stopwatch_time = self.stopwatch_time.addSecs(1)
        self.stopwatch_label.setText(self.stopwatch_time.toString("mm:ss"))

    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.MouseButton.LeftButton:
            self.dragging = True
            self.last_mouse_pos = event.pos()

    def mouseMoveEvent(self, event: QMouseEvent):
        if self.dragging:
            delta = event.pos() - self.last_mouse_pos
            scrollbar = self.text_display.verticalScrollBar()
            scrollbar.setValue(scrollbar.value() - delta.y())
            self.last_mouse_pos = event.pos()

    def mouseReleaseEvent(self, event: QMouseEvent):
        if event.button() == Qt.MouseButton.LeftButton:
            self.dragging = False
