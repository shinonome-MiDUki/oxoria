import sys
import math

from PySide6.QtWidgets import (
    QGraphicsView, QGraphicsScene
)
from PySide6.QtCore import (
    Qt, QPoint, QLineF
)
from PySide6.QtGui import (
    QPainter, QColor, QBrush, QPixmap, QPen
)

from oxoria.ui.canvas_area.graphics_item import ImageItem
from oxoria.ui.ui_var import UI_Var

class MainCanvas(QGraphicsView):

    def __init__(self, parent=None):
        super().__init__(parent)


        scene = QGraphicsScene(self)
        scene.setSceneRect(-UI_Var.CANVAS_RANGE, -UI_Var.CANVAS_RANGE, UI_Var.CANVAS_RANGE * 2, UI_Var.CANVAS_RANGE * 2)
        self.setScene(scene)

        self.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)
        self.setDragMode(QGraphicsView.DragMode.RubberBandDrag)
        self.setTransformationAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)
        self.setResizeAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)
        self.setBackgroundBrush(QBrush(QColor("#1E1E1E")))
        self.setAcceptDrops(True)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        UI_Var.CANVAS_HEIGHT = self.size().height()
        self.centerOn(0, 0)
        self.scale(0.2, 0.2)  

        self.panning     = False
        self.pan_start   = QPoint()

    def drawBackground(self, painter, rect):
        super().drawBackground(painter, rect)
        
        transform = self.transform()
        scale = transform.m11()  
        
        base_step = 100
        
        if scale > 2.0:
            step = base_step / 2
        elif scale < 0.5:
            step = base_step * 2
        else:
            step = base_step

        left = rect.left()
        top = rect.top()
        right = rect.right()
        bottom = rect.bottom()

        start_x = math.floor(left / step) * step
        start_y = math.floor(top / step) * step

        thin_pen = QPen(QColor(60, 60, 60), 1.0 / scale)
        thick_pen = QPen(QColor(80, 80, 80), 1.5 / scale)

        x = start_x
        while x < right:
            painter.setPen(thick_pen if int(x) % int(step * 5) == 0 else thin_pen)
            painter.drawLine(QLineF(x, top, x, bottom))
            x += step

        y = start_y
        while y < bottom:
            painter.setPen(thick_pen if int(y) % int(step * 5) == 0 else thin_pen)
            painter.drawLine(QLineF(left, y, right, y))
            y += step

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.MiddleButton:
            self.panning   = True
            self.pan_start = event.position().toPoint()
            self.setCursor(Qt.CursorShape.ClosedHandCursor)
            event.accept()
        else:
            super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self.panning:
            delta = event.position().toPoint() - self.pan_start
            self.pan_start = event.position().toPoint()
            self.horizontalScrollBar().setValue(self.horizontalScrollBar().value() - delta.x())
            self.verticalScrollBar().setValue(self.verticalScrollBar().value() - delta.y())
            event.accept()
        else:
            super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.MiddleButton:
            self.panning = False
            self.setCursor(Qt.CursorShape.ArrowCursor)
            event.accept()
        else:
            super().mouseReleaseEvent(event)

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dragMoveEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event):
        print("Drop event:", event.mimeData().urls())
        for url in event.mimeData().urls():
            path = url.toLocalFile()
            pm = QPixmap(path)
            if not pm.isNull():
                scene_pos = self.mapToScene(event.position().toPoint())
                item = ImageItem(pm, scene_pos)
                self.scene().addItem(item)
        event.acceptProposedAction()

    def keyPressEvent(self, event):
        modifiers = event.modifiers()
        if modifiers & Qt.KeyboardModifier.ControlModifier:
            factor = 1.0
            if event.key() == Qt.Key_Semicolon:
                factor = 1.10
            elif event.key() == Qt.Key_Colon:
                factor = 0.90
            self.scale(factor, factor)
            UI_Var.CANVAS_HEIGHT = self.size().height()
        else:
            if event.key() in (Qt.Key_Delete, Qt.Key_Backspace):
                for item in self.scene().selectedItems():
                    self.scene().removeItem(item)
            elif event.key() == Qt.Key_0 and event.modifiers() & Qt.KeyboardModifier.ControlModifier:
                self.resetTransform()
                self.centerOn(0, 0)
        super().keyPressEvent(event)