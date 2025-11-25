import os
from pathlib import Path
from PySide6.QtGui import QPixmap, QIcon, QFont, QDesktopServices, QPainter, QPainterPath
from PySide6.QtCore import Qt, QUrl
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton, QDialog, QFrame, QMenuBar, QMenu,
    QListWidget, QListWidgetItem, QFileDialog, QMessageBox, QLabel, QComboBox, QCheckBox, QSpacerItem
)
from PySide6.QtCore import QThreadPool
from PySide6.QtMultimedia import QSoundEffect

from core.config_manager import load_config, save_config, resource_path
from core.metadata_fetcher import MetadataFetcher
from ui.link_item_widget import LinkItemWidget
import qdarktheme
from core.downloader import download_missing_binaries


class DownloaderWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.cfg = load_config()
        self.download_folder = self.cfg.get('last_folder', str(Path.home()))
        theme = "dark" if self.cfg.get('dark_mode', False) else "light"
        qdarktheme.setup_theme(theme, corner_shape="rounded")

        self.setWindowTitle("yoo_front")
        self.setMinimumSize(800, 600)
        self.resize(1000, 700)
        self.setAcceptDrops(True)

        self.threadpool = QThreadPool.globalInstance()
        download_missing_binaries()

        self.setup_ui()
        self.apply_custom_styling()

    def setup_ui(self):
        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(16)
        main_layout.setContentsMargins(20, 20, 20, 20)

        # === HEADER: Title + Dark Mode Toggle ===
        header = QHBoxLayout()
        title = QLabel("Video Downloader")
        title_font = QFont("Segoe UI", 18, QFont.Weight.Bold)
        title.setFont(title_font)

        self.dark_toggle = QCheckBox("Dark Mode")
        self.dark_toggle.setChecked(self.cfg.get('dark_mode', False))
        self.dark_toggle.stateChanged.connect(self.toggle_dark)

        header.addWidget(title)
        header.addStretch()
        header.addWidget(self.dark_toggle)

        main_layout.addLayout(header)

        # === URL INPUT ROW ===
        input_layout = QHBoxLayout()
        input_layout.setSpacing(12)

        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText(
            "Paste YouTube, TikTok, Instagram or any video link here...")
        self.url_input.setMinimumHeight(48)
        self.url_input.setClearButtonEnabled(True)

        add_btn = QPushButton("Add")
        add_btn.setIcon(QIcon.fromTheme("list-add"))
        add_btn.setMinimumHeight(48)
        add_btn.setDefault(True)
        add_btn.clicked.connect(self.on_add_clicked)

        input_layout.addWidget(self.url_input, 1)
        input_layout.addWidget(add_btn)
        main_layout.addLayout(input_layout)

        # === LINK LIST ===
        self.link_list = QListWidget()
        self.link_list.setMinimumHeight(280)
        self.link_list.setAlternatingRowColors(True)
        self.link_list.setSelectionMode(QListWidget.SelectionMode.ExtendedSelection)
        self.link_list.setStyleSheet("""
            QListWidget::item { padding: 8px; border-bottom: 1px solid rgba(0,0,0,0.05); }
        """)
        main_layout.addWidget(self.link_list)

        # === TOOLBAR (Bottom controls) ===
        toolbar = QHBoxLayout()
        toolbar.setSpacing(12)

        # Format selector
        self.format_combo = QComboBox()
        self.format_combo.setMinimumHeight(40)
        self.format_combo.addItems([
            "Best Quality (Video + Audio)",
            "1080p", "720p", "480p", "360p",
            # "Audio Only (Best MP3)",
            # "Audio Only (M4A)"
        ])
        preset = self.cfg.get('format_preset', 'Best Quality (Video + Audio)')
        self.format_combo.setCurrentText(preset)
        # self.format_combo.currentTextChanged.connect(self.on_format_changed)

        # Folder selection
        folder_btn = QPushButton("Choose")
        folder_btn.setIcon(QIcon.fromTheme("folder"))
        folder_btn.setMinimumHeight(40)
        folder_btn.clicked.connect(self.choose_folder)

        self.folder_label = QLabel(str(self.download_folder))
        self.folder_label.setMinimumWidth(200)

        open_folder_btn = QPushButton("Open")
        open_folder_btn.setIcon(QIcon.fromTheme("folder-open"))
        open_folder_btn.clicked.connect(self.show_in_explorer)

        # Action buttons
        remove_btn = QPushButton("Remove")
        remove_btn.setIcon(QIcon.fromTheme("list-remove"))
        remove_btn.clicked.connect(self.remove_selected)

        self.download_btn = QPushButton("Save All")
        self.download_btn.setIcon(QIcon.fromTheme("document-save"))
        self.download_btn.setMinimumHeight(48)
        self.download_btn.setStyleSheet("""
            QPushButton {
                background-color: #2196F3; 
                color: white; 
                font-weight: bold; 
                border-radius: 8px;
                padding: 0 24px;
            }
            QPushButton:hover { background-color: #1E88E5; }
            QPushButton:pressed { background-color: #1976D2; }
        """)
        self.download_btn.clicked.connect(self.download_all)

        # Add to toolbar
        toolbar.addWidget(QLabel("Format:"))
        toolbar.addWidget(self.format_combo)
        toolbar.addSpacerItem(QSpacerItem(20, 0))
        toolbar.addWidget(QLabel("Save to:"))
        toolbar.addWidget(folder_btn)
        toolbar.addWidget(self.folder_label)
        toolbar.addWidget(open_folder_btn)
        toolbar.addStretch()
        toolbar.addWidget(remove_btn)
        toolbar.addWidget(self.download_btn)

        main_layout.addLayout(toolbar)

        # Sound effect for feedback
        self.sound = QSoundEffect()
        # self.sound.setSource(QUrl.fromLocalFile(":/sounds/add.wav"))  # optional
        self.create_menu()

    def create_menu(self):
        menubar = QMenuBar(self)
        help_menu = QMenu("Help", self)
        about_action = help_menu.addAction("About the Developer")
        about_action.triggered.connect(self.show_about_logarizm)
        menubar.addMenu(help_menu)
        self.layout().setMenuBar(menubar)

    def apply_custom_styling(self):
        # Extra polish
        self.setStyleSheet("""
            QLineEdit {
                padding: 12px;
                border: 2px solid palette(midlight);
                border-radius: 8px;
                font-size: 14px;
            }
            QLineEdit:focus {
                border: 2px solid #2196F3;
            }
            QPushButton {
                padding: 8px 16px;
                border-radius: 6px;
                font-weight: 600;
            }
            QComboBox {
                padding: 8px 12px;
                border: 2px solid palette(midlight);
                border-radius: 6px;
            }
            QLabel {
                font-size: 13px;
            }
        """)

    def on_add_clicked(self):
        url = self.url_input.text().strip()
        if not url:
            QMessageBox.warning(self, 'Empty', 'Please enter a valid link')
            return
        self.add_link_item(url)
        self.url_input.clear()

    def add_link_item(self, url):
        item = QListWidgetItem()
        widget = LinkItemWidget(url)
        item.setSizeHint(widget.sizeHint())
        self.link_list.addItem(item)
        self.link_list.setItemWidget(item, widget)
        MetadataFetcher.fetch_async(
            url, lambda title, content: self.update_widget(widget, title, content))

    def update_widget(self, widget, title, content):
        if title:
            widget.set_title(title)
        if content:
            pix = QPixmap()
            pix.loadFromData(content)
            widget.set_thumbnail(pix)

    def remove_selected(self):
        for itm in self.link_list.selectedItems():
            row = self.link_list.row(itm)
            self.link_list.takeItem(row)

    def download_all(self):
        count = self.link_list.count()
        if count == 0:
            QMessageBox.information(self, 'No Links', 'Add links before downloading.')
            return
        fmt = self.format_combo.currentText()
        # iterate items
        for i in range(self.link_list.count()):
            item = self.link_list.item(i)
            widget = self.link_list.itemWidget(item)
            widget.download()
        print(f'Started downloading {count} items.')

    def choose_folder(self):
        folder = QFileDialog.getExistingDirectory(
            self, 'Choose download folder', self.download_folder)
        if folder:
            self.download_folder = folder
            self.folder_label.setText(folder)
            self.cfg['last_folder'] = folder
            save_config(self.cfg)

    def toggle_dark(self, state):
        enabled = bool(state)
        self.cfg['dark_mode'] = enabled
        if enabled:
            self.apply_dark_style()
        else:
            self.apply_light_style()
        save_config(self.cfg)

    def apply_dark_style(self):
        qdarktheme.setup_theme("dark")

    def apply_light_style(self):
        qdarktheme.setup_theme("light")

    def show_in_explorer(self):
        if self.download_folder and os.path.exists(self.download_folder):
            # Open containing folder and select file
            path = os.path.abspath(self.download_folder)
            if os.name == 'nt':  # Windows
                os.startfile(path)
            elif os.name == 'posix':
                # Linux / macOS
                QDesktopServices.openUrl(QUrl.fromLocalFile(path))

    def show_about_logarizm(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("About Logarizm")
        dialog.setModal(True)
        dialog.resize(460, 620)
        layout = QVBoxLayout(dialog)
        layout.setContentsMargins(32, 32, 32, 32)
        layout.setSpacing(18)

        # ── Logo / Icon ─────────────────────────────────────
        logo_label = QLabel()
        logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        logo_label.setMinimumHeight(100)

        logo_path = resource_path("assets/media/logo.png")  # 256x256 or 512x512 PNG with transparency
        if Path(logo_path).exists():
            pixmap = QPixmap(logo_path).scaled(
                96, 96, Qt.AspectRatioMode.KeepAspectRatioByExpanding,
                Qt.TransformationMode.SmoothTransformation
            )
            # Circular clip
            circular = QPixmap(96, 96)
            circular.fill(Qt.GlobalColor.transparent)
            painter = QPainter(circular)
            painter.setRenderHint(QPainter.RenderHint.Antialiasing)
            path = QPainterPath()
            path.addEllipse(0, 0, 96, 96)
            painter.setClipPath(path)
            painter.drawPixmap(0, 0, pixmap)
            painter.end()
            logo_label.setPixmap(circular)
        else:
            logo_label.setText("Logarizm")
            logo_label.setFont(QFont("Segoe UI", 32, QFont.Weight.Bold))
            logo_label.setStyleSheet("color: #6C5CE7;")  # nice purple/indigo

        layout.addWidget(logo_label)

        # ── Title ───────────────────────────────────────────
        title = QLabel("Logarizm")
        title.setFont(QFont("Segoe UI", 24, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        tagline = QLabel("Simple tools for everyday people")
        tagline.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(tagline)

        # ── Separator ───────────────────────────────────────
        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setFrameShadow(QFrame.Shadow.Sunken)
        line.setStyleSheet("margin: 16px 0;")
        layout.addWidget(line)

        # ── The Heartfelt Message ───────────────────────────
        message = QLabel(
            "Hi! We're <b>Logarizm</b> — a tiny independent developer (or two friends) "
            "making free, clean, and honest software.\n\n"
            "No ads. No trackers. No subscriptions.\n"
            "Just useful tools built with care because we needed them ourselves.\n\n"
            "This YouTube Downloader is 100% open source and will always stay free.\n\n"
            "If it saves you time or makes you smile — that’s more than enough for us"
        )
        message.setWordWrap(True)
        message.setAlignment(Qt.AlignmentFlag.AlignCenter)
        message.setStyleSheet("font-size: 14px; line-height: 1.7;")
        layout.addWidget(message)

        # ── Support (optional & gentle) ─────────────────────
        support = QLabel(
            "<p style='text-align:center; color:#a0a0a0; font-size:13px;'>"
            "Love this app? You can support our work<br>"
            # "<a href='https://buymeacoffee.com/logarizm' style='color:#00A8E8;'>Buy us a coffee</a> • "
            "<a href='https://github.com/Ahmed-Ismail-M' style='color:#00A8E8;'>Star on GitHub</a> • "
            "<a href='https://logarizm.com' style='color:#00A8E8;'>Visit logarizm.com</a>"
            "</p>"
        )
        support.setOpenExternalLinks(True)
        support.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(support)

        layout.addStretch()

        # ── Version & License ───────────────────────────────
        footer = QLabel(
            "yoo_front v1.0<br>"
            "Made with <span style='color:#E91E63;'>♥</span> using Python (yt-dlp) + PyQt6<br>"
            "© 2025 Logarizm • <a href='https://github.com/Ahmed-Ismail-M/yoo_front'>Open Source</a>"
        )
        footer.setOpenExternalLinks(True)
        footer.setAlignment(Qt.AlignmentFlag.AlignCenter)
        footer.setStyleSheet("font-size: 12px;")
        layout.addWidget(footer)

        # ── Close Button ────────────────────────────────────
        close_btn = QPushButton("Close")
        close_btn.setMinimumHeight(48)
        close_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        close_btn.setStyleSheet("""
            QPushButton {
                background: #6C5CE7;
                color: white;
                border-radius: 12px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover { background: #5A4FCF; }
        """)
        close_btn.clicked.connect(dialog.accept)
        layout.addWidget(close_btn)

        dialog.exec()
