import sys
from PySide6.QtWidgets import QSplitter

class Splitter(QSplitter):
    """デフォルトより太くて見やすいドラッグハンドル"""

    def __init__(self, orientation, parent=None):
        super().__init__(orientation, parent)
        self.setHandleWidth(10)
        self.setStyleSheet("""
            QSplitter::handle {
                background: #3C3C3C;
            }
            QSplitter::handle:hover {
                background: #007ACC;
            }
            QSplitter::handle:pressed {
                background: #005F9E;
            }
        """)