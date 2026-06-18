import sys
from PySide6.QtWidgets import (
    QGraphicsItem, QGraphicsRectItem,
)
from PySide6.QtCore import (
    Qt, QPointF
)
from PySide6.QtGui import (
    QColor, QPen, QBrush
)

from oxoria.cmd.config_api import EditorConfigAPI as Editor

class ResizeHandle(QGraphicsRectItem):

    def __init__(self, corner, parent_item):
        handle_size = Editor.handle_size
        super().__init__(-handle_size / 2, -handle_size / 2, handle_size, handle_size, parent_item)
        self.corner = corner        
        self.parent_item = parent_item
        self.dragging = False
        self.drag_start = QPointF()
        self.is_activated = False

        self.setBrush(QBrush(QColor(Editor.handle_color)))
        self.setPen(QPen(QColor(Editor.handle_outline_color), Editor.handle_outline_thickness))
        self.setZValue(10)
        self.setCursor(self._cursor_for(corner))
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable, False)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIgnoresTransformations, False)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsFocusable, False)
        self.setAcceptHoverEvents(True)

    def _cursor_for(self, corner):
        map = {
            "TL": Qt.CursorShape.SizeFDiagCursor,
            "BR": Qt.CursorShape.SizeFDiagCursor,
            "TR": Qt.CursorShape.SizeBDiagCursor,
            "BL": Qt.CursorShape.SizeBDiagCursor,
        }
        return map.get(corner, Qt.CursorShape.SizeAllCursor)
    
    def hoverEnterEvent(self, event):
        self.is_activated = True
        return super().hoverEnterEvent(event)
    
    def hoverLeaveEvent(self, event):
        self.is_activated = False
        self.parent_item.setFocus()
        return super().hoverLeaveEvent(event)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.dragging   = True
            self.drag_start = event.scenePos()
            event.accept()
        else:
            super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self.dragging:
            self.parent_item.resize_by_handle(self.corner, event.scenePos())
            event.accept()
        else:
            super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.dragging = False
            event.accept()
        else:
            super().mouseReleaseEvent(event)