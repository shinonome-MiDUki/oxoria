import json
from dataclasses import fields

from PySide6.QtWidgets import (
    QPushButton, QDialog, QVBoxLayout,
    QLabel, QWidget, QLineEdit, 
    QTabWidget, QCheckBox, QGridLayout
)
from PySide6.QtGui import QIntValidator, QDoubleValidator

from oxoria.cmd.config_api import AppConfigAPI, EditorConfigAPI

class SettingsDialog(QDialog):
    def __init__(self):
        super().__init__()

    def draw_dialog(self):
        self.setWindowTitle("App Settings")
        self.setModal(True)
        layout = QVBoxLayout()
        self.tabs = QTabWidget()
        self.tabs.addTab(self.draw_settings_tab(ConfigType=AppConfigAPI), "App Settings")
        self.tabs.addTab(self.draw_settings_tab(ConfigType=EditorConfigAPI), "Editor Settings")
        layout.addWidget(self.tabs)
        self.setLayout(layout)


    def draw_settings_tab(self,
                          ConfigType: AppConfigAPI | EditorConfigAPI
                          ) -> QWidget:
        page = QWidget(self)
        sub_lo = QGridLayout()
        row_count = 0
        for field in fields(ConfigType):
            attr_name = field.name
            attr_value = getattr(ConfigType, field.name)
            value_type = type(attr_value).__name__
            attr_label = QLabel(attr_name)
            match value_type:
                case "int":
                    setting_widget = QLineEdit()
                    validator = QIntValidator(bottom=1)
                    setting_widget.setValidator(validator)
                    setting_widget.setText(str(attr_value))
                    confirm_widget = QPushButton("Set")
                    confirm_widget.clicked.connect(self.test)
                case "float":
                    setting_widget = QLineEdit()
                    validator = QDoubleValidator(bottom=0.1)
                    setting_widget.setValidator(validator)
                    setting_widget.setText(str(attr_value))
                    confirm_widget = QPushButton("Set")
                    confirm_widget.clicked.connect(self.test)
                case "str":
                    setting_widget = QLineEdit()
                    setting_widget.setText(attr_value)
                    confirm_widget = QPushButton("Set")
                    confirm_widget.clicked.connect(self.test)
                case "bool":
                    setting_widget = QCheckBox()
                    setting_widget.setChecked(attr_value)
                    confirm_widget = QPushButton("Set")
                    confirm_widget.clicked.connect(self.test)
                case _:
                    setting_widget = QLineEdit()
                    setting_widget.setText(str(attr_value))
                    confirm_widget = QPushButton("Set")
                    confirm_widget.clicked.connect(self.test)
            sub_lo.addWidget(attr_label, row_count, 0)
            sub_lo.addWidget(setting_widget, row_count, 1)
            sub_lo.addWidget(confirm_widget, row_count, 2)
            row_count += 1
        close_window_btn = QPushButton("Close")
        close_window_btn.clicked.connect(self.close)
        sub_lo.addWidget(close_window_btn)
        page.setLayout(sub_lo)
        return page


    def test(self):
        print("TEST")

    def close_window(self):
        self.accept()