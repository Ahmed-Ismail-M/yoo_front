from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QIcon
from ui.main_window import DownoaderWidget
import sys

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon("yt_icon.png"))
    window = DownoaderWidget()
    window.show()
    sys.exit(app.exec())
