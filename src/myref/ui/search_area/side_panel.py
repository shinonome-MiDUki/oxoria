import sys
from PySide6.QtWidgets import (
    QWidget,QVBoxLayout, QHBoxLayout, QLineEdit, 
    QTreeWidget, QTreeWidgetItem,QLabel, QPushButton
)

from PySide6.QtGui import (
    QColor
)

from myref.ui.ui_var import UI_Var

class SidePanel(QWidget):
    """
    上部：検索バー
    下部：ツリービュー（グループ + アイテム）
    幅は QSplitter によって制御される
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumWidth(UI_Var.SIDEBAR_MIN)
        self.setMaximumWidth(UI_Var.SIDEBAR_MAX)
        self._build_ui()
        self._apply_style()

    def _build_ui(self):
        root_layout = QVBoxLayout(self)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)

        # ── タイトルバー ──────────────────────
        title_bar = QWidget()
        title_bar.setObjectName("titleBar")
        title_bar.setFixedHeight(36)
        tb_layout = QHBoxLayout(title_bar)
        tb_layout.setContentsMargins(12, 0, 8, 0)

        title_label = QLabel("EXTENSIONS")
        title_label.setObjectName("titleLabel")

        icon_btn = QPushButton("···")
        icon_btn.setObjectName("iconBtn")
        icon_btn.setFixedSize(24, 24)
        icon_btn.setToolTip("More actions")

        tb_layout.addWidget(title_label)
        tb_layout.addStretch()
        tb_layout.addWidget(icon_btn)

        # ── 検索バー ──────────────────────────
        search_frame = QWidget()
        search_frame.setObjectName("searchFrame")
        sf_layout = QHBoxLayout(search_frame)
        sf_layout.setContentsMargins(8, 6, 8, 6)

        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText("Search Extensions in Marketplace")
        self.search_box.setObjectName("searchBox")
        self.search_box.setClearButtonEnabled(True)
        self.search_box.textChanged.connect(self._on_search_changed)

        sf_layout.addWidget(self.search_box)

        # ── フィルターボタン行 ─────────────────
        filter_frame = QWidget()
        filter_frame.setObjectName("filterFrame")
        ff_layout = QHBoxLayout(filter_frame)
        ff_layout.setContentsMargins(8, 0, 8, 4)
        ff_layout.setSpacing(4)

        for label in ("Installed", "Popular", "Recommended"):
            btn = QPushButton(label)
            btn.setObjectName("filterBtn")
            btn.setCheckable(True)
            ff_layout.addWidget(btn)
        ff_layout.addStretch()

        # ── ツリービュー ──────────────────────
        self.tree = QTreeWidget()
        self.tree.setObjectName("extTree")
        self.tree.setHeaderHidden(True)
        self.tree.setIndentation(16)
        self.tree.setRootIsDecorated(True)
        self.tree.itemClicked.connect(self._on_item_clicked)
        self._populate_tree()

        # ── 組み立て ──────────────────────────
        root_layout.addWidget(title_bar)
        root_layout.addWidget(search_frame)
        root_layout.addWidget(filter_frame)
        root_layout.addWidget(self.tree, stretch=1)

    def _populate_tree(self):
        """サンプルデータでツリーを埋める"""
        groups = {
            "INSTALLED (4)": [
                ("🎨", "Prettier",         "v3.1.0",  "Prettier formatter"),
                ("🔵", "Pylance",           "v2024.2", "Python language support"),
                ("🟡", "ESLint",            "v2.4.4",  "JS linting"),
                ("🟢", "GitLens",           "v14.9.1", "Git supercharged"),
            ],
            "POPULAR": [
                ("🔴", "Docker",            "v1.29.0", "Container management"),
                ("🟣", "Remote - SSH",      "v0.112",  "Open remote folders"),
                ("⚪", "Live Share",        "v1.0.5",  "Real-time collaboration"),
                ("🔷", "Jupyter",           "v2024.1", "Notebook support"),
                ("🟠", "GitHub Copilot",    "v1.180",  "AI code completion"),
            ],
            "RECOMMENDED": [
                ("🧩", "Path Intellisense", "v2.8.5",  "Filename autocomplete"),
                ("📦", "Import Cost",       "v3.3.0",  "Show package size"),
            ],
        }

        for group_name, items in groups.items():
            group_item = QTreeWidgetItem(self.tree)
            group_item.setText(0, group_name)
            group_item.setExpanded(True)
            font = group_item.font(0)
            font.setBold(True)
            group_item.setFont(0, font)
            group_item.setForeground(0, QColor("#9D9D9D"))

            for icon, name, version, desc in items:
                child = QTreeWidgetItem(group_item)
                child.setText(0, f"  {icon}  {name}  {version}")
                child.setToolTip(0, desc)
                child.setForeground(0, QColor("#CCCCCC"))

    # ── イベント（空実装） ─────────────────────
    def _on_search_changed(self, text):
        pass   # ← バックエンド側で実装

    def _on_item_clicked(self, item, column):
        pass   # ← バックエンド側で実装

    # ── スタイルシート ─────────────────────────
    def _apply_style(self):
        self.setStyleSheet("""
            SidePanel {
                background: #252526;
            }
            QWidget#titleBar {
                background: #252526;
                border-bottom: 1px solid #3C3C3C;
            }
            QLabel#titleLabel {
                color: #BBBBBB;
                font-size: 11px;
                font-weight: bold;
                letter-spacing: 1px;
            }
            QPushButton#iconBtn {
                background: transparent;
                color: #BBBBBB;
                border: none;
                font-size: 16px;
                border-radius: 3px;
            }
            QPushButton#iconBtn:hover {
                background: #3A3A3A;
            }
            QWidget#searchFrame {
                background: #252526;
            }
            QLineEdit#searchBox {
                background: #3C3C3C;
                color: #D4D4D4;
                border: 1px solid #3C3C3C;
                border-radius: 4px;
                padding: 4px 8px;
                font-size: 12px;
            }
            QLineEdit#searchBox:focus {
                border: 1px solid #007ACC;
            }
            QWidget#filterFrame {
                background: #252526;
            }
            QPushButton#filterBtn {
                background: #3C3C3C;
                color: #9D9D9D;
                border: none;
                border-radius: 3px;
                padding: 2px 8px;
                font-size: 11px;
            }
            QPushButton#filterBtn:hover {
                background: #4A4A4A;
                color: #D4D4D4;
            }
            QPushButton#filterBtn:checked {
                background: #007ACC;
                color: #FFFFFF;
            }
            QTreeWidget#extTree {
                background: #252526;
                color: #CCCCCC;
                border: none;
                font-size: 12px;
                outline: none;
            }
            QTreeWidget#extTree::item {
                padding: 3px 0;
            }
            QTreeWidget#extTree::item:hover {
                background: #2A2D2E;
            }
            QTreeWidget#extTree::item:selected {
                background: #094771;
            }
            QScrollBar:vertical {
                background: #252526;
                width: 8px;
            }
            QScrollBar::handle:vertical {
                background: #424242;
                border-radius: 4px;
            }
        """)