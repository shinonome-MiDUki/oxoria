import sys
from PySide6.QtWidgets import (
    QWidget, QHBoxLayout, QLabel
)

class HintBar(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(22)
        self.setStyleSheet("background: #007ACC;")

        layout = QHBoxLayout(self)
        layout.setContentsMargins(8, 0, 8, 0)
        layout.setSpacing(16)

        hints = [

        ]
        for hint in hints:
            lbl = QLabel(hint)
            lbl.setStyleSheet("color: #FFFFFF; font-size: 11px;")
            layout.addWidget(lbl)

        layout.addStretch()