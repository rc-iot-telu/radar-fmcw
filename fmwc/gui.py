from PyQt5.QtWidgets import (
    QDesktopWidget, QGridLayout, QGroupBox,
    QLabel, QLineEdit, QMainWindow, 
    QPlainTextEdit, QPushButton, 
    QVBoxLayout, QWidget,
)

from .core import TWRRespirationDetection
from .config import serial_port
from .contrib import list_com_port, set_serial_port

class TWRWindow(QWidget):
    def __init__(self) -> None:
        super().__init__()

        layout = QVBoxLayout()

        self.setLayout(layout)
        self.setFocus()

        self.twr = TWRRespirationDetection(serial_port, 9600)
        self.twr.run()

class RespirationWindow(QWidget):
    def __init__(self) -> None:
        super().__init__()

        layout = QVBoxLayout()
        self.setLayout(layout)

class WindowApp(QMainWindow):

    def __init__(self, parent=None) -> None:
        super().__init__(parent)

        self.setWindowTitle("FMWC Radar Launcher")
        self.resize(640, 480)

        # Move window to the center of the screen
        fg = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        fg.moveCenter(cp)
        self.move(fg.topLeft())

        self.grid = QGridLayout()

        #  self.thread = QThread()

        widget = QWidget()
        widget.setLayout(self.grid)

        self.grid.addWidget(self._serial_port_group(), 0, 0)
        self.grid.addWidget(self._top_button_group(), 0, 1)
        self.grid.addWidget(self._list_serial_ports(), 1, 0, 1, 2)

        self.setCentralWidget(widget)
        self.show()

    def _top_button_group(self) -> QWidget:
        group_box = QGroupBox("Menu Program")

        braspiro = QPushButton("Raspiro Meter")
        btwr = QPushButton("TWR Respiration Detection")
        btwr.clicked.connect(self._twr_launcher)

        h_box = QGridLayout()
        h_box.addWidget(braspiro, 0, 0)
        h_box.addWidget(btwr, 0, 1)
        h_box.addWidget(QLabel("Silahkan memilih program yang ingin dijalankan."), 1, 0, 1, 2)

        group_box.setLayout(h_box)
        return group_box

    def _serial_port_group(self) -> QWidget:
        group_box = QGroupBox("Setting Serial Port")

        set_port = QPushButton("Simpan Serial Port")
        set_port.clicked.connect(self._set_port_number)

        port_number_label = QLabel("Serial Port: ")
        self.port_number = QLineEdit(serial_port)

        grid = QGridLayout()
        grid.addWidget(port_number_label, 0, 0)
        grid.addWidget(self.port_number, 0, 1)
        grid.addWidget(set_port, 0, 2)

        group_box.setLayout(grid)
        return group_box

    def _list_serial_ports(self) -> QWidget:
        group_box = QGroupBox("Daftar Serial Port yang Tersedia")

        #  label = QLabel("Daftar serial port yang terdeteksi: ")
        refresh_port_button = QPushButton("Refresh Daftar Ports")
        refresh_port_button.clicked.connect(self._refresh_ports_list)
        self.port_list = QPlainTextEdit(self)
        self.port_list.insertPlainText(list_com_port())

        grid = QGridLayout()
        #  grid.addWidget(label, 0, 0)
        grid.addWidget(refresh_port_button, 0, 0)
        grid.addWidget(self.port_list, 1, 0, 1, 2)

        group_box.setLayout(grid)
        return group_box

    def _twr_launcher(self, checked) -> None:
        self.twr_window = TWRWindow()
        self.twr_window.show()

    def _refresh_ports_list(self) -> None:
        self.port_list.setPlainText(list_com_port())

    def _set_port_number(self) -> None:
        set_serial_port(self.port_number.text())
