import sys

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QMenu

from oxoria.ui.canvas_area.canvas import MainCanvas
from oxoria.ui.canvas_area.graphics_item import ImageItem
from oxoria.graphics.cv.cv_proccess import CvProcess as Cv

class CanvasCtxMenu(MainCanvas):

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.menu_ctx)

    def menu_ctx(self, pos):

        menu = QMenu()
        delete_action = menu.addAction("Delete")
        delete_action.triggered.connect(lambda: self.delete_images())
        resettrans_action = menu.addAction('Reset Transform')
        resettrans_action.triggered.connect(lambda: self.reset_transform())
        menu.addSeparator()
        cv_submenu = menu.addMenu('Processing')
        self.cv_submenu_ctx(cv_submenu)

        menu.exec_(self.mapToGlobal(pos))

    def cv_submenu_ctx(self, submenu: QMenu):
        tobw_action = submenu.addAction("To Black-White")
        tobw_action.triggered.connect(lambda: self.cv_toblackwhite())
        denoise_action = submenu.addAction("Denoise")
        denoise_action.triggered.connect(lambda: self.cv_denoise())


    def delete_images(self):
        for item in self.scene().selectedItems():
            self.scene().removeItem(item)

    def reset_transform(self):
        self.resetTransform()
        self.centerOn(0, 0)

    def cv_toblackwhite(self):
        for item in self.scene().selectedItems():
            pixmap = item.base_pixmap
            bw_img = Cv.to_blackwhite(pixmap=pixmap)
            scaled_bw_img = ImageItem.scale_pixmap(bw_img)
            item.setPixmap(scaled_bw_img)

    def cv_denoise(self):
        for item in self.scene().selectedItems():
            pixmap = item.base_pixmap
            bw_img = Cv.denoise_img(pixmap=pixmap)
            scaled_bw_img = ImageItem.scale_pixmap(bw_img)
            item.setPixmap(scaled_bw_img)
