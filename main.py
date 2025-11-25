from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QIcon, QFontDatabase, QFont
from ui.main_window import DownloaderWidget
from core.config_manager import resource_path
import sys

if __name__ == "__main__":
    app = QApplication(sys.argv)
    QFontDatabase.addApplicationFont(resource_path("assets/fonts/Inter-VariableFont_opsz,wght.ttf"))
    QFontDatabase.addApplicationFont(resource_path("assets/fonts/Inter-VariableFont_opsz,wght.ttf"))
    # QFontDatabase.addApplicationFont(resource_path("assets/fonts/Inter-Bold.ttf"))
    app.setFont(QFont("Inter", 11))
    app.setWindowIcon(QIcon(resource_path("assets/media/yoo_front_logo.png")))
    window = DownloaderWidget()
    window.show()
    sys.exit(app.exec())
