import sys

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QMenu

from oxoria.ui.canvas_area.canvas import MainCanvas
from oxoria.ui.canvas_area.graphics_item import ImageItem
from oxoria.cmd.std_cv_cmd import CvProcessAPI as CvAPI

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
        recovercolor_action = submenu.addAction("Recover Color")
        recovercolor_action.triggered.connect(lambda: self.cv_recovercolor())
        denoise_action = submenu.addAction("Denoise")
        denoise_action.triggered.connect(lambda: self.cv_denoise())


    def delete_images(self):
        for item in self.scene().selectedItems():
            self.scene().removeItem(item)

    def reset_transform(self):
        self.resetTransform()
        self.centerOn(0, 0)

    def cv_toblackwhite(self):
        CvAPI.to_blackwhite()

    def cv_recovercolor(self):
        CvAPI.recover_color()

    def cv_denoise(self):
        CvAPI.denoise_img()
