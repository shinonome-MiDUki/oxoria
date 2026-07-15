import sys
import subprocess
import re
import datetime
from pathlib import Path

from PySide6.QtWidgets import (
    QWidget, QHBoxLayout, QLabel,
    QLineEdit, QPushButton, QCompleter,
    QFileDialog
)
from PySide6.QtCore import QStringListModel, QTimer, Qt

from oxoria.ui.ux_widgets.console_output import OxoriaConsole
from oxoria.cmd.std_menu_cmd import StdMenuCmd
from oxoria.cmd.std_cv_cmd import CvProcessAPI
from oxoria.cmd.canvas_api import CanvasAPI
from oxoria.cmd.resources_api import ResourcesAPI
from oxoria.cmd.search_api import SearchAPI
from oxoria.cmd.app_api import AppAPI
from oxoria.cmd.package_api import PackageAPI
from oxoria.cmd.config_api import UseConfigData as Cfg
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

        open_console_btn = QPushButton("console")
        open_console_btn.setStyleSheet(
            f"color: {Cfg.editor_config().command_line_text_color}; background-color: {Cfg.editor_config().command_line_bg_color};"
            )
        open_console_btn.clicked.connect(self.open_oxoria_console)
        layout.addWidget(open_console_btn)
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
        cmd = self.python_cmd_input.text()
        if cmd not in GBVar.COMMAND_STACK and cmd != "":
            GBVar.COMMAND_STACK.append(cmd)
            if len(GBVar.COMMAND_STACK) > Cfg.app_config().command_stack_length:
                GBVar.COMMAND_STACK.pop(0)
            self.completer_list = [f">{i} - {GBVar.COMMAND_STACK[i * -1]}" for i in range(1, len(GBVar.COMMAND_STACK) + 1)]
            self.completer_model.setStringList(self.completer_list)
        self.error_message_box.setText("")
        self.dismiss_error_box_btn.hide()
        std_menu_cmd = StdMenuCmd()
        std_cv_cmd = CvProcessAPI
        canvas_api = CanvasAPI()
        resources_api = ResourcesAPI()
        search_api = SearchAPI()
        package_api = PackageAPI()
        app_api = AppAPI()
        api_set = {
            "std": std_menu_cmd,
            "cv": std_cv_cmd,
            "canvas": canvas_api,
            "resources": resources_api,
            "search": search_api,
            "app": app_api,
            "package": package_api,
            "cfg": Cfg,
            "print" : OxoriaConsole.write_console
        }
        if cmd.startswith("%"):
            file_path = cmd.lstrip("%")
            self.exec_python_file(file_path=file_path, api_set=api_set)
        else:
            self.exec_python_command(cmd=cmd, api_set=api_set)

    def exec_python_command(self,
                            cmd: str,
                            api_set: dict):
        OxoriaConsole.write_console(console_text=f"Executed : {cmd}")
        try:
            exec(cmd, api_set)
            self.python_cmd_input.clear()
        except Exception as e:
            self.error_message_box.setText(f"{e}")
            self.dismiss_error_box_btn.show()
            OxoriaConsole.write_console(console_text=f"ERROR : {e}")

    def exec_python_file(self, 
                         file_path: str,
                         api_set: dict):
        OxoriaConsole.write_console(console_text=f"Executed Script : {file_path}")
        try:
            if not Path(file_path).exists():
                raise Exception("Designated file path not found")
            with open(file_path, "r", encoding="utf-8") as f:
                code = f.read()
                exec(code, api_set)
        except Exception as e:
            self.error_message_box.setText(f"{e}")
            self.dismiss_error_box_btn.show()
            OxoriaConsole.write_console(console_text=f"ERROR : {e}")
        self.python_cmd_input.clear()

    def dismiss_error_message(self):
        self.error_message_box.setText("")
        self.dismiss_error_box_btn.hide()

    def fill_command(self):
        input_cmd = self.python_cmd_input.text()
        if bool(re.match(r"^>\d+$", input_cmd)):
            stack_idx = int(input_cmd.lstrip(">"))
            if stack_idx > len(GBVar.COMMAND_STACK):
                self.python_cmd_input.setText("")
                return
            self.python_cmd_input.setText(GBVar.COMMAND_STACK[stack_idx * -1])
        elif bool(re.match(r"^:[a-z]$", input_cmd)):
            shortcut_alphabet = str(input_cmd.lstrip(":"))
            mycommand = AppAPI().get_mycommand(shortcut_alphabet)
            self.python_cmd_input.setText(mycommand)
        elif bool(re.match(r"^(ide-)\S*\s$", input_cmd)):
            ide_executable = Cfg.app_config().ide_executable_path
            if not ide_executable: 
                return
            script_dir = Path(GBVar.DATA_DIR).resolve().parent / "script"
            if not script_dir.exists():
                script_dir.mkdir(parents=True, exist_ok=True)
            script_name = input_cmd.split("-")[-1].strip().strip(".py")
            if script_name:
                script_path = script_dir / f"{script_name}.py"
            else:
                script_path = script_dir / f"custom_script_{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}.py"
            if not script_path.exists():
                with open(script_path, "w", encoding="utf-8") as f:
                    f.write("")
            try:
                subprocess.run([ide_executable, script_path])
            except Exception as e:
                self.error_message_box.setText(f"{e}")
                self.dismiss_error_box_btn.show()
                OxoriaConsole.write_console(console_text=f"ERROR : {e}")
                return
            self.python_cmd_input.setText(f"%{script_path}")
        elif input_cmd == "run":
            filename, _ = QFileDialog.getOpenFileName(self, "Open Python script", "", "Python (*.py)")
            if filename:
                self.python_cmd_input.setText(f"%{filename}")
        else:
            return
        
    def open_oxoria_console(self):
        self.oxoria_console = OxoriaConsole()
        self.oxoria_console.setWindowModality(Qt.NonModal)
        self.oxoria_console.show()
        
    def autofill(self, text):
        QTimer.singleShot(
            0, lambda: self.python_cmd_input.setText(text.split("-")[-1].strip())
            )