import sys
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QSplitter,
    QVBoxLayout, QHBoxLayout, QLineEdit, QTreeWidget,
    QTreeWidgetItem, QGraphicsView, QGraphicsScene,
    QGraphicsPixmapItem, QGraphicsItem, QGraphicsRectItem,
    QLabel, QPushButton, QFrame, QSizePolicy, QScrollArea,
)
from PySide6.QtCore import (
    Qt, QRectF, QPointF, QSizeF, QPoint
)
from PySide6.QtGui import (
    QPainter, QColor, QPen, QBrush, QPixmap,
    QCursor, QTransform, QIcon, QFont
)


# ─────────────────────────────────────────────
#  定数
# ─────────────────────────────────────────────
HANDLE_SIZE     = 10      # リサイズハンドルの一辺 (px)
MIN_ITEM_SIZE   = 40      # 画像アイテムの最小サイズ (px)
CANVAS_RANGE    = 50000   # シーンの論理サイズ (±px)
SIDEBAR_DEFAULT = 240     # サイドパネルの初期幅 (px)
SIDEBAR_MIN     = 100       # サイドパネルの最小幅 (px)  ← 0で「消せる」
SIDEBAR_STANDBY = 50
SIDEBAR_MAX     = 600     # サイドパネルの最大幅 (px)


# ─────────────────────────────────────────────
#  無限キャンバス（QGraphicsView）
# ─────────────────────────────────────────────
class InfiniteCanvas(QGraphicsView):
    """
    ・中ボタン or Space+左ボタン でパン
    ・Ctrl+ホイール でズーム
    ・画像をシーンへドロップ可能（ファイル）
    """

    def __init__(self, parent=None):
        super().__init__(parent)

        # シーン設定
        scene = QGraphicsScene(self)
        scene.setSceneRect(-CANVAS_RANGE, -CANVAS_RANGE, CANVAS_RANGE * 2, CANVAS_RANGE * 2)
        self.setScene(scene)

        # ビュー設定
        self.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)
        self.setDragMode(QGraphicsView.DragMode.RubberBandDrag)
        self.setTransformationAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)
        self.setResizeAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)
        self.setBackgroundBrush(QBrush(QColor("#1E1E1E")))
        self.setAcceptDrops(True)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        # パン用の内部状態
        self.panning     = False
        self.pan_start   = QPoint()

    # ── パン（中ボタン or Space+左ボタン）──────
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.MiddleButton:
            self.panning   = True
            self.pan_start = event.position().toPoint()
            self.setCursor(Qt.CursorShape.ClosedHandCursor)
            event.accept()
        else:
            super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self.panning:
            delta = event.position().toPoint() - self.pan_start
            self.pan_start = event.position().toPoint()
            self.horizontalScrollBar().setValue(self.horizontalScrollBar().value() - delta.x())
            self.verticalScrollBar().setValue(self.verticalScrollBar().value() - delta.y())
            event.accept()
        else:
            super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.MiddleButton:
            self.panning = False
            self.setCursor(Qt.CursorShape.ArrowCursor)
            event.accept()
        else:
            super().mouseReleaseEvent(event)

    # ── ファイルドロップ ──────────────────────
    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dragMoveEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event):
        print("Drop event:", event.mimeData().urls())
        for url in event.mimeData().urls():
            path = url.toLocalFile()
            pm = QPixmap(path)
            if not pm.isNull():
                scene_pos = self.mapToScene(event.position().toPoint())
                item = ImageItem(pm, scene_pos)
                self.scene().addItem(item)
        event.acceptProposedAction()

    # ── キーボードショートカット ──────────────
    def keyPressEvent(self, event):
        modifiers = event.modifiers()
        if modifiers & Qt.KeyboardModifier.ControlModifier:
            factor = 1.0
            if event.key() == Qt.Key_Semicolon:
                factor = 1.10
            elif event.key() == Qt.Key_Colon:
                factor = 0.90
            self.scale(factor, factor)
        else:
            # Delete / Backspace で選択アイテム削除
            if event.key() in (Qt.Key_Delete, Qt.Key_Backspace):
                for item in self.scene().selectedItems():
                    self.scene().removeItem(item)
            # 0 キーでビューをリセット
            elif event.key() == Qt.Key_0 and event.modifiers() & Qt.KeyboardModifier.ControlModifier:
                self.resetTransform()
                self.centerOn(0, 0)
        super().keyPressEvent(event)

# ─────────────────────────────────────────────
#  リサイズハンドル（画像の四隅に表示される小さな矩形）
# ─────────────────────────────────────────────
class ResizeHandle(QGraphicsRectItem):
    """親アイテム(ImageItem)の四隅に置かれるドラッグ可能なハンドル"""

    def __init__(self, corner, parent_item):
        super().__init__(-HANDLE_SIZE / 2, -HANDLE_SIZE / 2, HANDLE_SIZE, HANDLE_SIZE, parent_item)
        self.corner      = corner        # "TL" | "TR" | "BL" | "BR"
        self.parent_item = parent_item
        self.dragging    = False
        self.drag_start  = QPointF()

        self.setBrush(QBrush(QColor("#4A90D9")))
        self.setPen(QPen(QColor("#FFFFFF"), 1.5))
        self.setZValue(10)
        self.setCursor(self._cursor_for(corner))
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable, False)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIgnoresTransformations, False)

    def _cursor_for(self, corner):
        map = {
            "TL": Qt.CursorShape.SizeFDiagCursor,
            "BR": Qt.CursorShape.SizeFDiagCursor,
            "TR": Qt.CursorShape.SizeBDiagCursor,
            "BL": Qt.CursorShape.SizeBDiagCursor,
        }
        return map.get(corner, Qt.CursorShape.SizeAllCursor)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.dragging   = True
            self.drag_start = event.scenePos()
            event.accept()
        else:
            super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self.dragging:
            self.parent_item.resize_by_handle(self.corner, event.scenePos())
            event.accept()
        else:
            super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.dragging = False
            event.accept()
        else:
            super().mouseReleaseEvent(event)


# ─────────────────────────────────────────────
#  画像アイテム（ドラッグ移動 + 四隅リサイズ）
# ─────────────────────────────────────────────
class ImageItem(QGraphicsPixmapItem):
    """キャンバス上に置かれる画像。移動・リサイズに対応。"""

    def __init__(self, pixmap, pos=QPointF(0, 0)):
        super().__init__(pixmap)
        canvas = InfiniteCanvas()
        canvas_height = canvas.size().height()
        minimise_ratio = 0.4

        self.base_pixmap = pixmap

        scale_factor = (canvas_height * minimise_ratio) / float(pixmap.width())
        scaled = self.base_pixmap.scaled(
            int(float(pixmap.height()) * scale_factor), int(float(pixmap.width()) * scale_factor),
            aspectMode = Qt.KeepAspectRatio,
            mode = Qt.TransformationMode.SmoothTransformation
        )
        self.setPixmap(scaled)
        self.setScale(1.0)
        self.img_w = self.boundingRect().width()
        self.img_h = self.boundingRect().height()

        self.setPos(pos)
        self.setFlags(
            QGraphicsItem.GraphicsItemFlag.ItemIsMovable |
            QGraphicsItem.GraphicsItemFlag.ItemIsSelectable |
            QGraphicsItem.GraphicsItemFlag.ItemSendsGeometryChanges
        )
        self.setTransformationMode(Qt.TransformationMode.SmoothTransformation)
        self.setCursor(Qt.CursorShape.SizeAllCursor)

        # 四隅のハンドルを生成・配置
        self.handles = {
            "TL": ResizeHandle("TL", self),
            "TR": ResizeHandle("TR", self),
            "BL": ResizeHandle("BL", self),
            "BR": ResizeHandle("BR", self),
        }

        self._place_handles()

    # ── ハンドル座標計算 ──────────────────────
    def _place_handles(self):
        w = self.img_w
        h = self.img_h
        self.handles["TL"].setPos(0, 0)
        self.handles["TR"].setPos(w, 0)
        self.handles["BL"].setPos(0, h)
        self.handles["BR"].setPos(w, h)

    # ── リサイズ処理 ──────────────────────────
    def resize_by_handle(self, corner, scene_pos):
        """ドラッグされたコーナーに応じてサイズ・位置を更新する"""
        item_pos  = self.mapFromScene(scene_pos)  # ローカル座標に変換
        new_w     = self.img_w
        new_h     = self.img_h
        delta_x   = 0.0
        delta_y   = 0.0

        if corner == "BR":
            new_w = max(MIN_ITEM_SIZE, item_pos.x())
            new_h = max(MIN_ITEM_SIZE, item_pos.y())

        elif corner == "TR":
            new_w   = max(MIN_ITEM_SIZE, item_pos.x())
            new_h   = max(MIN_ITEM_SIZE, self.img_h - item_pos.y())

        elif corner == "BL":
            new_w   = max(MIN_ITEM_SIZE, self.img_w - item_pos.x())
            new_h   = max(MIN_ITEM_SIZE, item_pos.y())

        elif corner == "TL":
            new_w   = max(MIN_ITEM_SIZE, self.img_w - item_pos.x())
            new_h   = max(MIN_ITEM_SIZE, self.img_h - item_pos.y())

        # ピクセルマップをスケーリングして適用
        scaled = self.base_pixmap.scaled(
            int(new_w), int(new_h),
            aspectMode = Qt.KeepAspectRatio,
            mode = Qt.TransformationMode.SmoothTransformation
        )
        self.prepareGeometryChange()
        self.setPixmap(scaled)
        self.img_w = self.boundingRect().width()
        self.img_h = self.boundingRect().height()

        # アイテム自体の位置を補正（TL/TR/BL ドラッグ時に画像が「ずれない」ように）
        if delta_x != 0 or delta_y != 0:
            offset = self.mapToScene(QPointF(delta_x, delta_y)) - self.mapToScene(QPointF(0, 0))
            self.setPos(self.pos() + offset)

        self._place_handles()

    # ── 選択状態の視覚フィードバック ─────────
    def paint(self, painter, option, widget=None):
        super().paint(painter, option, widget)
        if self.isSelected():
            pen = QPen(QColor("#4A90D9"), 2, Qt.PenStyle.DashLine)
            painter.setPen(pen)
            painter.drawRect(self.boundingRect())


# ─────────────────────────────────────────────
#  サイドパネル（VSCode の Extensions Explorer 風）
# ─────────────────────────────────────────────
class SidePanel(QWidget):
    """
    上部：検索バー
    下部：ツリービュー（グループ + アイテム）
    幅は QSplitter によって制御される
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumWidth(SIDEBAR_MIN)
        self.setMaximumWidth(SIDEBAR_MAX)
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


# ─────────────────────────────────────────────
#  スプリッターハンドル（視認性向上）
# ─────────────────────────────────────────────
class StyledSplitter(QSplitter):
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


# ─────────────────────────────────────────────
#  ステータスバー
# ─────────────────────────────────────────────
class StatusBar(QWidget):
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


# ─────────────────────────────────────────────
#  メインウィンドウ
# ─────────────────────────────────────────────
class MainWindow(QMainWindow):
    def __init__(self):
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
        self.splitter = StyledSplitter(Qt.Orientation.Horizontal)

        self.side_panel = SidePanel()
        self.canvas     = InfiniteCanvas()

        self.splitter.addWidget(self.side_panel)
        self.splitter.addWidget(self.canvas)

        # 初期幅：サイドパネル 240px, キャンバス 残り
        self.splitter.setSizes([SIDEBAR_DEFAULT, 9999])
        self.splitter.setCollapsible(0, True)   # サイドパネルは折り畳み可能
        self.splitter.setCollapsible(1, False)  # キャンバスは折り畳み不可

        # ── 組み立て ──────────────────────────
        main_layout.addWidget(self.splitter, stretch=1)
        main_layout.addWidget(StatusBar())


# ─────────────────────────────────────────────
#  エントリポイント
# ─────────────────────────────────────────────
def main():
    app = QApplication(sys.argv)
    app.setStyle("Fusion")

    win = MainWindow()
    win.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()