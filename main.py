import sys

from PyQt5.QtWidgets import QApplication

from fmwc.gui import WindowApp


def main(argv):

    # Entry point for the window app
    app = QApplication(argv)
    ex = WindowApp()
    ex.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main(sys.argv)

