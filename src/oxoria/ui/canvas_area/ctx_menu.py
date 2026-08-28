import sys

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QWidget, QMenu, QLineEdit,
    QVBoxLayout, QWidgetAction
)
from PySide6.QtGui import QCursor

from oxoria.ui.canvas_area.canvas import MainCanvas
from oxoria.ui.canvas_area.graphics_item import ImageItem
from oxoria.ui.canvas_area.memo_item import MemoItem
from oxoria.cmd.std_cv_cmd import CvProcessAPI as CvAPI
from oxoria.cmd.canvas_api import CanvasAPI

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
        move_layer_up_action = menu.addAction('Move one layer above')
        move_layer_up_action.triggered.connect(lambda: self.move_layer(unit=1))
        move_layer_down_action = menu.addAction('Move one layer below')
        move_layer_down_action.triggered.connect(lambda: self.move_layer(unit=-1))
        grouping_action = menu.addAction('Group items')
        grouping_action.triggered.connect(lambda: self.group_items())
        memo_action = menu.addAction('Add memo')
        memo_action.triggered.connect(lambda: self.add_memo_paper())
        menu.addSeparator()
        cv_submenu = menu.addMenu('OpenCV')
        self.cv_submenu_ctx(cv_submenu)

        menu.exec_(self.mapToGlobal(pos))

    def cv_submenu_ctx(self, submenu: QMenu):
        tobw_action = submenu.addAction("To Black-White")
        tobw_action.triggered.connect(lambda: self.cv_toblackwhite())
        recovercolor_action = submenu.addAction("Recover Color")
        recovercolor_action.triggered.connect(lambda: self.cv_recovercolor())
        denoise_action = submenu.addAction("Denoise")
        denoise_action.triggered.connect(lambda: self.cv_denoise())
        custom_cv_menu = submenu.addMenu("Custum OpenCV")
        self.custom_cv_submenu_ctx(custom_cv_menu)

    def custom_cv_submenu_ctx(self, custom_cv_menu: QMenu):
        custom_cv_cmd_widget = QWidget()
        custom_cv_cmd_layout = QVBoxLayout(custom_cv_cmd_widget)
        custom_cv_cmd_input = QLineEdit()
        custom_cv_cmd_input.setPlaceholderText("cv2:")
        custom_cv_cmd_layout.addWidget(custom_cv_cmd_input)
        custom_cv_action = QWidgetAction(custom_cv_menu)
        custom_cv_action.setDefaultWidget(custom_cv_cmd_widget)
        custom_cv_menu.addAction(custom_cv_action)
        exec_custom_cv_action = custom_cv_menu.addAction("Run")
        exec_custom_cv_action.triggered.connect(lambda: CvAPI.custom_operation(cv2_cmd=custom_cv_cmd_input.text()))


    def delete_images(self):
        for item in self.scene().selectedItems():
            self.scene().removeItem(item)

    def reset_transform(self):
        CanvasAPI().set_to_origin()

    def group_items(self):
        CanvasAPI().group_selected()

    def move_layer(self, unit: int):
        selected_item = CanvasAPI().get_selected()
        for item in selected_item:
            current_z = item.zValue()
            item.setZValue(current_z + unit)

    def add_memo_paper(self):
        cursor_pos = QCursor.pos()
        memo = MemoItem(pos=cursor_pos)
        self.scene().addItem(memo)

    def cv_toblackwhite(self):
        CvAPI.to_blackwhite()

    def cv_recovercolor(self):
        CvAPI.recover_color()

    def cv_denoise(self):
        CvAPI.denoise_img()
    
