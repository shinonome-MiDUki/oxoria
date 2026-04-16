import sys
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout
)
from PySide6.QtCore import Qt

from myref.ui.canvas_area.canvas import MainCanvas
from myref.ui.search_area.side_panel import SidePanel
from myref.ui.ux_widgets.splitter import Splitter
from myref.ui.ux_widgets.status_bar import HintBar
from myref.ui.ui_var import UI_Var

class MainWindow(QMainWindow):
    def __init__(self):
        print("MainWindow: Initializing UI...")
        super().__init__()
        self.setWindowTitle("Infinite Canvas — PySide6")
        self.resize(1280, 800)
        self.setStyleSheet("background: #1E1E1E;")

        # ── 中央ウィジェット ──────────────────
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QVBoxLayout(central)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # ── スプリッター ──────────────────────
        self.splitter = Splitter(Qt.Orientation.Horizontal)

        self.side_panel = SidePanel()
        self.canvas     = MainCanvas()

        self.splitter.addWidget(self.side_panel)
        self.splitter.addWidget(self.canvas)

        # 初期幅：サイドパネル 240px, キャンバス 残り
        self.splitter.setSizes([UI_Var.SIDEBAR_DEFAULT, 9999])
        self.splitter.setCollapsible(0, True)   # サイドパネルは折り畳み可能
        self.splitter.setCollapsible(1, False)  # キャンバスは折り畳み不可

        # ── 組み立て ──────────────────────────
        main_layout.addWidget(self.splitter, stretch=1)
        main_layout.addWidget(HintBar())