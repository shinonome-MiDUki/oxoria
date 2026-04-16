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

from myref.ui.ui_var import UI_Var

class ResizeHandle(QGraphicsRectItem):
    """親アイテム(ImageItem)の四隅に置かれるドラッグ可能なハンドル"""

    def __init__(self, corner, parent_item):
        super().__init__(-UI_Var.HANDLE_SIZE / 2, -UI_Var.HANDLE_SIZE / 2, UI_Var.HANDLE_SIZE, UI_Var.HANDLE_SIZE, parent_item)
        self.corner      = corner        # "TL" | "TR" | "BL" | "BR"
        self.parent_item = parent_item
        self.dragging    = False
        self.drag_start  = QPointF()

        self.setBrush(QBrush(QColor("#4A90D9")))
        self.setPen(QPen(QColor("#FFFFFF"), 1.5))
        self.setZValue(10)
        self.setCursor(self._cursor_for(corner))
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable, False)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIgnoresTransformations, False)

    def _cursor_for(self, corner):
        map = {
            "TL": Qt.CursorShape.SizeFDiagCursor,
            "BR": Qt.CursorShape.SizeFDiagCursor,
            "TR": Qt.CursorShape.SizeBDiagCursor,
            "BL": Qt.CursorShape.SizeBDiagCursor,
        }
        return map.get(corner, Qt.CursorShape.SizeAllCursor)

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