from PyQt6.QtWidgets import QWidget, QPlainTextEdit, QTextEdit
from PyQt6.QtCore import QRect, QSize, Qt
from PyQt6.QtGui import QColor, QPainter, QTextCursor, QTextFormat, QPalette

class LineNumberArea(QWidget):
    def __init__(self, editor):
        super().__init__(editor)
        self.code_editor = editor

    def sizeHint(self):
        return QSize(self.code_editor.line_number_area_width(), 0)

    def paintEvent(self, event):
        self.code_editor.line_number_area_paint_event(event)

class CodeEditor(QPlainTextEdit):
    def __init__(self):
        super().__init__()
        self.line_number_area = LineNumberArea(self)
        self.blockCountChanged.connect(self.update_line_number_area_width)
        self.updateRequest.connect(self.update_line_number_area)
        self.cursorPositionChanged.connect(self.highlight_current_line)
        self.update_line_number_area_width(0)

        # Initialize line_highlight_color
        self.line_highlight_color = QColor(Qt.GlobalColor.yellow)

        # Set colors based on system theme
        self.set_editor_colors()
        self.highlight_current_line()

    def set_editor_colors(self):
        palette = self.palette()
        background_color = palette.color(QPalette.ColorRole.Base)

        # Assuming dark theme if background is dark
        if background_color.lightness() < 128:  # lightness() returns a value from 0 (black) to 255 (white)
            # Dark theme
            self.setStyleSheet("background-color: black; color: white;")
            self.line_highlight_color = QColor(Qt.GlobalColor.darkYellow)
        else:
            # Light theme
            self.setStyleSheet("background-color: white; color: black;")
            self.line_highlight_color = QColor(Qt.GlobalColor.yellow)

    def line_number_area_width(self):
        digits = len(str(self.blockCount())) + 1
        space = 3 + self.fontMetrics().horizontalAdvance('9') * digits
        return space

    def update_line_number_area_width(self, _):
        self.setViewportMargins(self.line_number_area_width(), 0, 0, 0)

    def update_line_number_area(self, rect, dy):
        if dy:
            self.line_number_area.scroll(0, dy)
        else:
            self.line_number_area.update(0, rect.y(), self.line_number_area.width(), rect.height())

        if rect.contains(self.viewport().rect()):
            self.update_line_number_area_width(0)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        cr = self.contentsRect()
        self.line_number_area.setGeometry(QRect(cr.left(), cr.top(), self.line_number_area_width(), cr.height()))

    def line_number_area_paint_event(self, event):
        painter = QPainter(self.line_number_area)
        painter.fillRect(event.rect(), Qt.GlobalColor.lightGray)

        block = self.firstVisibleBlock()
        block_number = block.blockNumber()
        top = int(self.blockBoundingGeometry(block).translated(self.contentOffset()).top())
        bottom = top + int(self.blockBoundingRect(block).height())

        # Gunakan font yang sama dengan editor teks utama
        font = self.font()
        painter.setFont(font)

        while block.isValid() and top <= event.rect().bottom():
            if block.isVisible() and bottom >= event.rect().top():
                number = str(block_number + 1)
                painter.setPen(Qt.GlobalColor.black)
                painter.drawText(0, top, self.line_number_area.width(), self.fontMetrics().height(),
                                Qt.AlignmentFlag.AlignRight, number)

            block = block.next()
            top = bottom
            bottom = top + int(self.blockBoundingRect(block).height())
            block_number += 1

    def highlight_current_line(self):
        extra_selections = []

        if not self.isReadOnly():
            selection = QTextEdit.ExtraSelection()

            # Tentukan warna sorotan berdasarkan tema
            background_color = self.line_highlight_color.lighter(160)

            # Jika background adalah warna kuning dan tema adalah gelap, ubah teks menjadi hitam
            if self.line_highlight_color == QColor(Qt.GlobalColor.darkYellow):
                selection.format.setForeground(Qt.GlobalColor.black)
            else:
                selection.format.setForeground(self.palette().color(QPalette.ColorRole.Text))

            selection.format.setBackground(background_color)
            selection.format.setProperty(QTextFormat.FullWidthSelection, True)
            selection.cursor = self.textCursor()
            selection.cursor.clearSelection()
            extra_selections.append(selection)

        self.setExtraSelections(extra_selections)

