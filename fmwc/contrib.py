from serial.tools.list_ports import comports

from PyQt5.QtWidgets import (
    QDialog, QGridLayout, QGroupBox,
    QHBoxLayout, QLabel, QLineEdit,
    QPlainTextEdit, QPushButton, 
)

from . import config

def list_com_port() -> str:
    ports = comports()

    if not ports:
        return "Tidak ada perangkat yang terhubung!"

    ports = ["{}: {} [{}]\n".format(port, desc, hwid) for port, desc, hwid in sorted(ports)]
    ports = "".join(ports)

    return ports

def setting_serial_port(port: str) -> None:
    config.serial_port = port

class ErrorDialog(QDialog):
    def __init__(self, error_msg:str, error_title: str, parent=None) -> None:
        super(ErrorDialog, self).__init__(parent)

        self.setWindowTitle(error_title)
        self.resize(220, 100)

        layout = QHBoxLayout()
        layout.addWidget(QLabel(error_msg))

        self.setLayout(layout)

class SettingWindow(QDialog):
    def __init__(self, parent=None) -> None:
        super(SettingWindow, self).__init__(parent)

        self.setWindowTitle("Setting Serial Port")

        self.port_number = config.serial_port


        # set the layout
        layout = QGridLayout()

        layout.addWidget(self._serial_port_group(), 0, 0)
        self.setLayout(layout)
        
    def _refresh_ports_list(self) -> None:
        self.port_list.setPlainText(list_com_port())

    def _serial_port_group(self):
        group_box = QGroupBox("Setting Serial Port")

        set_port = QPushButton("Simpan Serial Port")
        set_port.clicked.connect(self._set_serial_port)

        port_number_label = QLabel("Serial Port: ")
        self.port_number_input = QLineEdit(self.port_number)

        refresh_port_button = QPushButton("Refresh Daftar Ports")
        refresh_port_button.clicked.connect(self._refresh_ports_list)
        self.port_list = QPlainTextEdit(self)
        self.port_list.insertPlainText(list_com_port())

        grid = QGridLayout()
        grid.addWidget(port_number_label, 0, 0)
        grid.addWidget(self.port_number_input, 0, 1)

        grid.addWidget(set_port, 0, 2)
        grid.addWidget(refresh_port_button, 0, 3)

        grid.addWidget(self.port_list, 1, 0, 1, 4)

        group_box.setLayout(grid)
        return group_box

    def _set_serial_port(self):
        setting_serial_port(self.port_number_input.text())


