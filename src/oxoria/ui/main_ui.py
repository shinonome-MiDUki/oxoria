import sys
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, 
    QMenu, QToolBar
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QAction

from oxoria.ui.canvas_area.canvas import MainCanvas
from oxoria.ui.search_area.side_panel import SidePanel
from oxoria.ui.ux_widgets.splitter import Splitter
from oxoria.ui.ux_widgets.status_bar import HintBar
from oxoria.ui.outline.menu_bar import MenuBar
from oxoria.ui.ui_var import UI_Var

class MainWindow(QMainWindow):
    def __init__(self):
        print("MainWindow: Initializing UI...")
        super().__init__()
        self.setWindowTitle("Infinite Canvas — PySide6")
        self.resize(1280, 800)
        self.setStyleSheet("background: #1E1E1E;")

        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QVBoxLayout(central)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        self.menu_bar = MenuBar(self)
        self.menu_bar.build_menu()

        self.splitter = Splitter(Qt.Orientation.Horizontal)

        self.side_panel = SidePanel()
        self.canvas     = MainCanvas()

        self.splitter.addWidget(self.side_panel)
        self.splitter.addWidget(self.canvas)

        self.splitter.setSizes([UI_Var.SIDEBAR_DEFAULT, 9999])
        self.splitter.setCollapsible(0, True)  
        self.splitter.setCollapsible(1, False) 

        main_layout.addWidget(self.splitter, stretch=1)
        main_layout.addWidget(HintBar())