import sys
import os

import qdarktheme

from PyQt5.QtWidgets import QApplication

from fmwc.core import WindowApp


def main(argv):
    os.environ["QT_AUTO_SCREEN_SCALE_FACTOR"] = "1"

    # Entry point for the window app
    app = QApplication(argv)
    app.setStyleSheet(qdarktheme.load_stylesheet('light'))

    ex = WindowApp()
    ex.showMaximized()

    sys.exit(app.exec())


if __name__ == "__main__":
    main(sys.argv)

