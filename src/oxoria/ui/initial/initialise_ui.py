import sys
import os
from pathlib import Path

from PySide6.QtWidgets import (
    QMainWindow, QWidget, 
    QVBoxLayout, QHBoxLayout, QLabel, 
    QLineEdit, QPushButton, QStackedWidget, 
    QFileDialog, QStyle
    )
from PySide6.QtCore import Qt, QSettings
from PySide6.QtGui import QPixmap

class InitUI(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Initial Setup")
        self.setFixedSize(600, 640)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        self.image_label = QLabel("Image Area")
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.setStyleSheet("background-color: #2c3e50; color: white; font-size: 20px;")
        
        current_dir = Path(__file__).resolve().parents[2]
        img_path = current_dir / "_resources/assets/initial_image.jpg"
        print(f"Loading image from: {img_path}")
        img = QPixmap(str(img_path))
        self.image_label.setPixmap(img.scaled(600, 345, Qt.KeepAspectRatioByExpanding))
        
        self.image_label.setFixedHeight(345) 
        main_layout.addWidget(self.image_label)

        self.stack = QStackedWidget()
        main_layout.addWidget(self.stack)
        self.central_repo_dir = self.app_data_dir()  

        self.setup_page_1()
        self.setup_page_2()

    def app_data_dir(self) -> str:
        home = Path.home()
        if sys.platform == "win32":
            app_data = home / "AppData/Local" / "oxoria"
        elif sys.platform == "darwin":
            app_data = home / "Library/Application Support"/ "oxoria"
        else:
            app_data = home / ".local/share" / "oxoria"
        return str(app_data)

    def setup_page_1(self):
        """1番目の画面：入力スペース"""
        page = QWidget()
        layout = QVBoxLayout(page)
        
        layout.addStretch()
        layout.addWidget(QLabel("Central repository directory: "))
        sublauyout = QHBoxLayout()
        self.central_repo = QLineEdit()
        sublauyout.addWidget(self.central_repo)
        self.central_repo.setText(self.central_repo_dir)
        self.browse_btn = QPushButton()
        sublauyout.addWidget(self.browse_btn)
        icon = self.style().standardIcon(QStyle.StandardPixmap.SP_FileDialogStart)
        self.browse_btn.setIcon(icon)
        layout.addLayout(sublauyout)
        self.browse_btn.setFixedWidth(40)
        self.browse_btn.clicked.connect(self.open_file_dialog)
        
        next_btn = QPushButton("Next →")
        next_btn.setFixedHeight(30)
        next_btn.clicked.connect(lambda: self.stack.setCurrentIndex(1))
        layout.addWidget(next_btn)
        layout.addStretch()
        
        self.stack.addWidget(page)

    def setup_page_2(self):
        """2番目の画面：完了・確認など"""
        page = QWidget()
        layout = QVBoxLayout(page)
        
        layout.addStretch()
        launch_btn = QPushButton("Launch")
        launch_btn.clicked.connect(self.launch_main_window)
        layout.addWidget(launch_btn)
        layout.addStretch()
        
        self.stack.addWidget(page)

    def open_file_dialog(self):
        dir_path = QFileDialog.getExistingDirectory(self, "Select Directory", str(Path.home()))
        if dir_path:
            self.central_repo_dir = dir_path
            self.central_repo.setText(dir_path)

    def launch_main_window(self):
        if not os.path.exists(self.central_repo_dir):
            os.makedirs(self.central_repo_dir)
        settings = QSettings("App", "oxoria")
        settings.setValue("central_repo_dir", self.central_repo_dir)
        
        from oxoria.ui.main_ui import MainWindow
        self.main_window = MainWindow()
        self.main_window.show()
        self.close()