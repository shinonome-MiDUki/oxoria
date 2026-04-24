import json
from pathlib import Path

from PySide6.QtWidgets import (
    QApplication, QMainWindow, QPushButton, QDialog, QVBoxLayout,
    QLabel, QFileDialog, QWidget, QLineEdit, QHBoxLayout
)
from PySide6.QtGui import QPixmap
from PySide6.QtCore import Qt, QSettings

from oxoria.ui.resources_lib.side_panel import SidePanel
from oxoria.cmd.resources_api import ResourcesAPI

class RegisterResourcesDialog(QDialog):
    def __init__(self, img_path: str, img_hash: str):
        super().__init__()
        self.setWindowTitle("Register Resources")
        self.setModal(True)
        self.img_path = img_path
        self.img_hash = img_hash
        layout = QVBoxLayout()
        self.image_preview_label = QLabel("Image Preview")
        self.image_preview_label.setAlignment(Qt.AlignCenter)
        self.image_preview_label.setStyleSheet("background-color: #ecf0f1; color: #2c3e50; font-size: 20px;")
        img = QPixmap(self.img_path)
        self.image_preview_label.setPixmap(img.scaled(600, 345, Qt.KeepAspectRatioByExpanding))
        self.image_preview_label.setFixedHeight(345)
        layout.addWidget(self.image_preview_label)
        
        input_fields_layout = QVBoxLayout()
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Resource Name")
        input_fields_layout.addWidget(self.name_input)
        self.name_input.textEdited.connect(self.check_duplicate_name)
        self.name_check_label = QLabel()
        self.name_check_label.setText("Please input the image name")
        self.memo_input = QLineEdit()
        self.memo_input.setPlaceholderText("Memo")
        input_fields_layout.addWidget(self.memo_input)
        input_fields_layout.addStretch()
        layout.addLayout(input_fields_layout)

        button_layout = QHBoxLayout()
        self.register_button = QPushButton("Register resource")
        self.register_button.clicked.connect(self.register_resource)
        button_layout.addWidget(self.register_button)
        self.opt_out_register_button = QPushButton("Import without register")
        self.opt_out_register_button.clicked.connect(self.opt_out_register)
        button_layout.addWidget(self.opt_out_register_button)
        layout.addLayout(button_layout)
        layout.addLayout(input_fields_layout)

        self.setLayout(layout)

        resources_dir = Path(QSettings("App", "oxoria").value("central_repo_dir", "")) / "resources_lib"
        with open(resources_dir / "resources.json", mode="r", encoding="utf-8") as f:
            resources_dict = json.load(f)
        self.resources_dict = resources_dict.get("resources", {})
        self.existing_path_set = set()
        self.existing_name_set = set()
        for k, v in self.resources_dict.items():
            if "path" in v:
                self.existing_path_set.add(v["path"])
            if "name" in v:
                self.existing_name_set.add(v["name"])
        
        self.resources_api = ResourcesAPI()

    def register_resource(self):
        input_name = str(self.name_input.text)
        if input_name in self.existing_name_set:
            return
        resource_profile = self.resources_api.make_resource_profile(img_path=str(self.img_path),
                                                                    name=str(self.name_input.text),
                                                                    memo=str(self.memo_input.text),
                                                                    tags=["a", "b", "c"])
        self.resources_api.import_resource(img_path=str(self.img_path),
                                                           profile=resource_profile)
        self.side_panel = SidePanel()

    def opt_out_register(self):
        pass

    def check_duplicate_name(self):
        input_name = str(self.name_input.text)
        if input_name in self.existing_name_set:
            self.name_check_label.setText(f"{input_name} already exist")
        else:
            self.name_check_label.setText("This name is available")
