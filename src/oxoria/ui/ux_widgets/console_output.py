import sys
import os
from pathlib import Path

from PySide6.QtWidgets import (
    QDialog, QLabel, QVBoxLayout,
    QPushButton, QHBoxLayout
    )
from PySide6.QtCore import Qt

from oxoria.global_var import GBVar

class OxoriaConsole(QDialog):
    def __init__(self):
        super().__init__()
        console_layout = QVBoxLayout()
        self.setWindowTitle("Oxoria Console Output")
        self.setWindowFlags(self.windowFlags() | Qt.WindowStaysOnTopHint)
        self.setFixedSize(600,450)
        self.console_display = QLabel()
        self.load_console()
        console_layout.addWidget(self.console_display)
        console_layout.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        console_layout.addStretch()

        btn_layout = QHBoxLayout()
        reload_console_btn = QPushButton("Reload")
        reload_console_btn.clicked.connect(self.load_console)
        btn_layout.addWidget(reload_console_btn)
        clear_console_btn = QPushButton("Clear")
        clear_console_btn.clicked.connect(self.clear_console)
        btn_layout.addWidget(clear_console_btn)

        console_layout.addLayout(btn_layout)
        self.setLayout(console_layout)

    def load_console(self):
        log_file_path = Path(GBVar.DATA_DIR).resolve().parent / "app_log.txt"
        if log_file_path.exists():
            with open(log_file_path, "r", encoding="utf-8") as f:
                console_log = f.readlines()
                console_log_text = "".join(console_log)
        else:
            console_log_text = "No console message found"
        self.console_display.setText(console_log_text)

    def clear_console(self):
        log_file_path = Path(GBVar.DATA_DIR).resolve().parent / "app_log.txt"
        os.unlink(log_file_path)
        self.console_display.setText("")



    @staticmethod
    def write_console(console_text: str) -> None:
        log_file_path = Path(GBVar.DATA_DIR).resolve().parent / "app_log.txt"
        with open(log_file_path, "a", encoding="utf-8") as f:
            f.write(f"{console_text}\n")