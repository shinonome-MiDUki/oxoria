import sys
from PySide6.QtWidgets import QGraphicsTextItem, QGraphicsScene, QGraphicsView, QApplication
from PySide6.QtCore import Qt, QPointF, QRectF
from PySide6.QtGui import QColor, QFont, QPen

from oxoria.cmd.config_api import EditorConfigAPI as Editor

class MemoItem(QGraphicsTextItem):
    def __init__(self, pos: QPointF = QPointF(0, 0), size: int = 1200):
        super().__init__()
        self.setPos(pos)
        self.size = size

        self.setTextInteractionFlags(Qt.TextInteractionFlag.NoTextInteraction)

        font = QFont(Editor.memo_text_font, Editor.memo_text_font_size)
        self.setFont(font)
        self.setDefaultTextColor(QColor(Editor.memo_text_color)) 
        self.setPlainText("Memo ...")

        self.margin = Editor.memo_text_margin
        self.setTextWidth(self.size - (self.margin * 2))

        self.setFlags(
            self.GraphicsItemFlag.ItemIsMovable |
            self.GraphicsItemFlag.ItemIsSelectable |
            self.GraphicsItemFlag.ItemSendsGeometryChanges |
            self.GraphicsItemFlag.ItemIsFocusable
        )
        self.setCursor(Qt.CursorShape.SizeAllCursor)

    def boundingRect(self):
        return QRectF(0, 0, self.size, self.size)

    def paint(self, painter, option, widget):
        painter.setBrush(QColor(Editor.memo_paper_color))
        
        rect = self.boundingRect()
        painter.drawRect(rect)

        super().paint(painter, option, widget)


    def mouseDoubleClickEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.setTextInteractionFlags(Qt.TextInteractionFlag.TextEditorInteraction)
            self.setFocus() 
            super().mouseDoubleClickEvent(event)

    def focusOutEvent(self, event):
        self.setTextInteractionFlags(Qt.TextInteractionFlag.NoTextInteraction)
        cursor = self.textCursor()
        cursor.clearSelection()
        self.setTextCursor(cursor)
        super().focusOutEvent(event)