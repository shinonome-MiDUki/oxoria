import sys
from PySide6.QtWidgets import (
    QWidget, QHBoxLayout, QLabel,
    QLineEdit, QPushButton
)

from oxoria.cmd.std_menu_cmd import StdMenuCmd
from oxoria.cmd.std_cv_cmd import CvProcessAPI
from oxoria.cmd.canvas_api import CanvasAPI
from oxoria.cmd.resources_api import ResourcesAPI
from oxoria.cmd.search_api import SearchAPI
from oxoria.cmd.app_api import AppAPI
from oxoria.cmd.config_api import EditorConfigAPI as Editor

class ConsoleLine(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(35)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(30, 0, 0, 0)
        layout.setSpacing(20)

        self.python_cmd_input = QLineEdit()
        self.python_cmd_input.setStyleSheet(
            f"color: {Editor.command_line_text_color}; background-color: {Editor.command_line_bg_color};"
            )
        self.python_cmd_input.setPlaceholderText("Python command ...")
        layout.addWidget(self.python_cmd_input)
        python_exec_btn = QPushButton("exec")
        python_exec_btn.setStyleSheet(
            f"color: {Editor.command_line_text_color}; background-color: {Editor.command_line_bg_color};"
            )
        layout.addWidget(python_exec_btn)
        python_exec_btn.clicked.connect(self.exec_oneline_python)

        layout.addStretch()

    def exec_oneline_python(self):
        std_menu_cmd = StdMenuCmd()
        std_cv_cmd = CvProcessAPI
        canvas_api = CanvasAPI()
        resources_api = ResourcesAPI()
        search_api = SearchAPI()
        app_api = AppAPI()
        api_set = {
            "std": std_menu_cmd,
            "cv": std_cv_cmd,
            "canvas": canvas_api,
            "resources": resources_api,
            "search": search_api,
            "app": app_api
        }
        cmd = self.python_cmd_input.text()
        self.python_cmd_input.clear()
        print(cmd)
        exec(cmd, api_set)