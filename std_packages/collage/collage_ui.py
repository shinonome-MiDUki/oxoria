from PySide6.QtWidgets import(
    QDialog, QLabel, QHBoxLayout,
    QPushButton
)
from PySide6.QtGui import (
    QPixmap, QPainter, QColor,
    QPen
)
from PySide6.QtCore import (
    QPoint, Qt, QRect
)

from oxoria.cmd.canvas_api import CanvasAPI

import grabcut_cv

class CollageImage(QLabel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.start_point = QPoint()
        self.end_point = QPoint()
        self.is_drawing = False
        
        self.setMouseTracking(True)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.start_point = event.position().toPoint()
            self.end_point = self.start_point
            self.is_drawing = True
            self.update()  

    def mouseMoveEvent(self, event):
        if self.is_drawing and (event.buttons() & Qt.MouseButton.LeftButton):
            self.end_point = event.position().toPoint()
            self.update() 

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.end_point = event.position().toPoint()
            self.is_drawing = False
            self.update()

    def paintEvent(self, event):
        super().paintEvent(event)
        
        if not self.start_point.isNull() and not self.end_point.isNull():
            painter = QPainter(self)
            
            pen = QPen(QColor(255, 0, 0), 2, Qt.PenStyle.SolidLine)
            painter.setPen(pen)
            rect = QRect(self.start_point, self.end_point)
            painter.drawRect(rect)
            
            painter.end()

class CollagePluginUi(QDialog):
    def __init__(self):
        super().__init__()
        self.canvas_api = CanvasAPI()
        self.is_cropped = False
        self.draw_ui()

    def draw_ui(self):
        self.setWindowTitle("CollagePlugin")
        self.setModal(True)
        selected_item_ls = self.canvas_api.get_selected()
        if not selected_item_ls:
            return
        self.selected_item = selected_item_ls[0]
        self.selected_pixmap = self.selected_item.base_pixmap
        main_layout = QHBoxLayout()
        self.pixmap_label = CollageImage(self)
        self.pixmap_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.pixmap_label.setPixmap(self.selected_pixmap)
        main_layout.addWidget(self.pixmap_label)

        crop_selected_btn = QPushButton("Crop Selected")
        crop_selected_btn.clicked.connect(self.crop_selected)
        main_layout.addWidget(crop_selected_btn)

        self.accept_btn = QPushButton("Accept")
        self.accept_btn.hide()
        self.accept_btn.clicked.connect(self.accept_process)
        main_layout.addWidget(self.accept_btn)
    
        self.setLayout(main_layout)

    def crop_selected(self):
        if not self.is_cropped:
            if self.pixmap_label.start_point.isNull() or self.pixmap_label.end_point.isNull():
                return
            self.processed_pixmap = grabcut_cv.pixmap_conversion(
                pixmap=self.selected_pixmap,
                crop_start=self.pixmap_label.start_point,
                crop_end=self.pixmap_label.end_point
            )
            self.pixmap_label.setPixmap(self.processed_pixmap)
            self.is_cropped = True
            self.accept_btn.show()
        else:
            self.pixmap_label.setPixmap(self.selected_pixmap)
            self.is_cropped = False
            self.accept_btn.hide()

    def accept_process(self):
        self.canvas_api.set_pixmap(
            pixmap=self.processed_pixmap,
            image_item=self.selected_item
        )
        self.accept()


