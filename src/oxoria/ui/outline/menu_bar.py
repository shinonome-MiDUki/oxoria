import sys
import json
from pathlib import Path

from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, 
    QMenu, QToolBar
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QAction

from oxoria.global_var import GBVar

class MenuBar():
    def __init__(self, main_window: QMainWindow):
        self.menu_bar = main_window.menuBar()
        with open(Path(GBVar.DATA_DIR) / "config/editor_config.json", "r", encoding="utf-8") as f:
            self.config = json.load(f)
        
    def build_menu(self):
        if "menu_bar" not in self.config:
            return
        for menu_item in self.config["menu_bar"]:
            menu_item_obj = self.menu_bar.addMenu(str(menu_item))
            if not isinstance(self.config["menu_bar"][menu_item], dict):
                continue
            for action_item in self.config["menu_bar"][menu_item]:
                menu_item_obj.addAction(action_item)