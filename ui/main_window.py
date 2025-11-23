import os
from pathlib import Path
from PySide6.QtGui import QPixmap, QIcon, QFont, QPalette, QColor

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton,
    QListWidget, QListWidgetItem, QFileDialog, QMessageBox, QLabel, QComboBox, QCheckBox, QSpacerItem
)
from PySide6.QtCore import QThreadPool
from PySide6.QtMultimedia import QSoundEffect

from core.config_manager import load_config, save_config
from core.metadata_fetcher import MetadataFetcher
from ui.link_item_widget import LinkItemWidget
import qdarktheme
from core.downloader import download_missing_binaries


class DownloaderWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.cfg = load_config()
        # self.download_folder = Path(self.cfg.get('last_folder', Path.home()))
        self.download_folder = self.cfg.get('last_folder', str(Path.home()))
        # Apply theme first
        theme = "dark" if self.cfg.get('dark_mode', False) else "light"
        qdarktheme.setup_theme(theme, corner_shape="rounded")

        self.setWindowTitle("YT Downloader")
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
        title = QLabel("YouTube Downloader")
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
            QListWidget::item:selected { background: palette(highlight); }
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
            "Audio Only (Best MP3)",
            "Audio Only (M4A)"
        ])
        preset = self.cfg.get('format_preset', 'Best Quality (Video + Audio)')
        self.format_combo.setCurrentText(preset)
        # self.format_combo.currentTextChanged.connect(self.on_format_changed)

        # Folder selection
        folder_btn = QPushButton("Choose Folder")
        folder_btn.setIcon(QIcon.fromTheme("folder"))
        folder_btn.setMinimumHeight(40)
        folder_btn.clicked.connect(self.choose_folder)

        self.folder_label = QLabel(str(self.download_folder))
        self.folder_label.setStyleSheet("color: palette(mid);")
        # self.folder_label.setElideMode(Qt.TextElideMode.ElideLeft)
        self.folder_label.setMinimumWidth(200)

        open_folder_btn = QPushButton("Open")
        open_folder_btn.setIcon(QIcon.fromTheme("folder-open"))
        open_folder_btn.clicked.connect(self.show_in_explorer)

        # Action buttons
        remove_btn = QPushButton("Remove Selected")
        remove_btn.setIcon(QIcon.fromTheme("list-remove"))
        remove_btn.clicked.connect(self.remove_selected)

        self.download_btn = QPushButton("Download All")
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
