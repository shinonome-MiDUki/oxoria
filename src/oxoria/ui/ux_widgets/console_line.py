import sys
import re

from PySide6.QtWidgets import (
    QWidget, QHBoxLayout, QLabel,
    QLineEdit, QPushButton, QCompleter
)
from PySide6.QtCore import QStringListModel, QTimer

from oxoria.cmd.std_menu_cmd import StdMenuCmd
from oxoria.cmd.std_cv_cmd import CvProcessAPI
from oxoria.cmd.canvas_api import CanvasAPI
from oxoria.cmd.resources_api import ResourcesAPI
from oxoria.cmd.search_api import SearchAPI
from oxoria.cmd.app_api import AppAPI
from oxoria.cmd.config_api import UseConfigData as Cfg
from oxoria.cmd.config_api import AppConfigAPI, EditorConfigAPI
from oxoria.global_var import GBVar

class ConsoleLine(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(35)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(30, 0, 0, 0)
        layout.setSpacing(20)

        self.python_cmd_input = QLineEdit()
        self.python_cmd_input.setStyleSheet(
            f"color: {Cfg.editor_config().command_line_text_color}; background-color: {Cfg.editor_config().command_line_bg_color};"
            )
        self.python_cmd_input.setPlaceholderText("Python command ...")
        self.completer_list = []
        self.completer_model = QStringListModel(self.completer_list)
        python_command_completer = QCompleter()
        python_command_completer.setModel(self.completer_model)
        python_command_completer.activated.connect(self.autofill)
        self.python_cmd_input.setCompleter(python_command_completer)
        self.python_cmd_input.textChanged.connect(self.fill_command)
        layout.addWidget(self.python_cmd_input)

        python_exec_btn = QPushButton("exec")
        python_exec_btn.setStyleSheet(
            f"color: {Cfg.editor_config().command_line_text_color}; background-color: {Cfg.editor_config().command_line_bg_color};"
            )
        layout.addWidget(python_exec_btn)
        python_exec_btn.clicked.connect(self.exec_oneline_python)
        layout.addStretch()

        self.error_message_box = QLabel("")
        self.error_message_box.setStyleSheet("color: red;")
        layout.addWidget(self.error_message_box)
        self.dismiss_error_box_btn = QPushButton("OK")
        self.dismiss_error_box_btn.setStyleSheet(
            "color: white; background-color: red;"
        )
        self.dismiss_error_box_btn.clicked.connect(self.dismiss_error_message)
        self.dismiss_error_box_btn.hide()
        layout.addWidget(self.dismiss_error_box_btn)


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
            "app": app_api,
            "cfg": Cfg
        }
        cmd = self.python_cmd_input.text()
        self.error_message_box.setText("")
        self.dismiss_error_box_btn.hide()
        if cmd not in GBVar.COMMAND_STACK:
            GBVar.COMMAND_STACK.append(cmd)
            if len(GBVar.COMMAND_STACK) > Cfg.app_config().command_stack_length:
                GBVar.COMMAND_STACK.pop(0)
            self.completer_list = [f">{i} - {GBVar.COMMAND_STACK[i * -1]}" for i in range(1, len(GBVar.COMMAND_STACK) + 1)]
            self.completer_model.setStringList(self.completer_list)
        try:
            exec(cmd, api_set)
            self.python_cmd_input.clear()
        except Exception as e:
            self.error_message_box.setText(f"{e}")
            self.dismiss_error_box_btn.show()

    def dismiss_error_message(self):
        self.error_message_box.setText("")
        self.dismiss_error_box_btn.hide()

    def fill_command(self):
        input_cmd = self.python_cmd_input.text()
        if bool(re.match("^>\d+$", input_cmd)):
            stack_idx = int(input_cmd.lstrip(">"))
            if stack_idx > len(GBVar.COMMAND_STACK):
                self.python_cmd_input.setText("")
                return
            self.python_cmd_input.setText(GBVar.COMMAND_STACK[stack_idx * -1])
        elif bool(re.match(r"^:[a-z]$", input_cmd)):
            shortcut_alphabet = str(input_cmd.lstrip(":"))
            mycommand = AppAPI().get_mycommand(shortcut_alphabet)
            self.python_cmd_input.setText(mycommand)
        else:
            return
        
    def autofill(self, text):
        QTimer.singleShot(
            0, 
            lambda: self.python_cmd_input.setText(text.split("-")[-1].strip())
            )