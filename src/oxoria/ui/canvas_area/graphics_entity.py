import sys
from typing import TYPE_CHECKING

from PySide6.QtWidgets import (
    QGraphicsPixmapItem, QGraphicsItem, 
)
from PySide6.QtCore import (
    Qt, QPointF
)
from PySide6.QtGui import (
    QColor, QPen
)

from oxoria.ui.canvas_area.resize_handle import ResizeHandle
from oxoria.cmd.config_api import UseConfigData as Cfg
if TYPE_CHECKING:
    BaseClass = QGraphicsItem
else:
    BaseClass = object

class ImageItem(object):

    def __init__(self, pos=QPointF(0, 0)):
        super().__init__()

        self.setPos(pos)
        self.setFlags(
            QGraphicsItem.GraphicsItemFlag.ItemIsMovable |
            QGraphicsItem.GraphicsItemFlag.ItemIsSelectable |
            QGraphicsItem.GraphicsItemFlag.ItemSendsGeometryChanges
        )
        self.setTransformationMode(Qt.TransformationMode.SmoothTransformation)
        self.setCursor(Qt.CursorShape.SizeAllCursor)

        self.handles = {
            "TL": ResizeHandle("TL", self),
            "TR": ResizeHandle("TR", self),
            "BL": ResizeHandle("BL", self),
            "BR": ResizeHandle("BR", self),
        }
        self.original_path = None
        self.pointer = None
        self.setFlag(QGraphicsPixmapItem.GraphicsItemFlag.ItemIsFocusable, True)

        self._place_handles()

    def _place_handles(self):
        w = self.img_w
        h = self.img_h
        self.handles["TL"].setPos(0, 0)
        self.handles["TR"].setPos(w, 0)
        self.handles["BL"].setPos(0, h)
        self.handles["BR"].setPos(w, h)

    def resize_by_handle(self, corner, scene_pos):
        """ドラッグされたコーナーに応じてサイズ・位置を更新する"""
        item_pos  = self.mapFromScene(scene_pos)  
        new_w     = self.img_w
        new_h     = self.img_h
        delta_x   = 0.0
        delta_y   = 0.0

        if corner == "BR":
            new_w = max(Cfg.editor_config().min_item_size, item_pos.x())
            new_h = max(Cfg.editor_config().min_item_size, item_pos.y())

        elif corner == "TR":
            new_w   = max(Cfg.editor_config().min_item_size, item_pos.x())
            new_h   = max(Cfg.editor_config().min_item_size, self.img_h - item_pos.y())
            delta_y = item_pos.y()

        elif corner == "BL":
            new_w   = max(Cfg.editor_config().min_item_size, self.img_w - item_pos.x())
            new_h   = max(Cfg.editor_config().min_item_size, item_pos.y())
            delta_x = item_pos.x()

        elif corner == "TL":
            new_w   = max(Cfg.editor_config().min_item_size, self.img_w - item_pos.x())
            new_h   = max(Cfg.editor_config().min_item_size, self.img_h - item_pos.y())
            delta_x = item_pos.x()
            delta_y = item_pos.y()

        scaled = self.base_pixmap.scaled(
            int(new_w), int(new_h),
            aspectMode = Qt.KeepAspectRatio,
            mode = Qt.TransformationMode.SmoothTransformation
        )
        self.prepareGeometryChange()
        self.setPixmap(scaled)
        self.img_w = self.boundingRect().width()
        self.img_h = self.boundingRect().height()

        if delta_x != 0 or delta_y != 0:
            offset = self.mapToScene(QPointF(delta_x, delta_y)) - self.mapToScene(QPointF(0, 0))
            self.setPos(self.pos() + offset)

        self._place_handles()

    def focusInEvent(self, event):
        for handle_name in self.handles:
            self.handles[handle_name].setVisible(True)
        super().focusInEvent(event)

    def focusOutEvent(self, event):
        for handle_name in self.handles:
            if self.handles[handle_name].is_activated:
                super().focusOutEvent(event)
                return
        for handle_name in self.handles:
            self.handles[handle_name].setVisible(False)
        super().focusOutEvent(event)

    def paint(self, painter, option, widget=None):
        super().paint(painter, option, widget)
        if self.isSelected():
            pen = QPen(QColor("#4A90D9"), 2, Qt.PenStyle.DashLine)
            painter.setPen(pen)
            painter.drawRect(self.boundingRect())