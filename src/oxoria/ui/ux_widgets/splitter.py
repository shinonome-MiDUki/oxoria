import sys
from PySide6.QtWidgets import QSplitter

from oxoria.cmd.config_api import EditorConfigAPI as Editor

class Splitter(QSplitter):

    def __init__(self, orientation, parent=None):
        super().__init__(orientation, parent)
        self.setHandleWidth(Editor.splitter_handle_width)
        self.setStyleSheet("""
            QSplitter::handle {
                background: #3C3C3C;
            }
            QSplitter::handle:hover {
                background: #007ACC;oco
            }
            QSplitter::handle:pressed {
                background: #005F9E;
            }ox
        """)