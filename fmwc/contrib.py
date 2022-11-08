from PyQt5.QtCore import Qt

from serial.tools.list_ports import comports

from PyQt5.QtWidgets import (
    QDialog, QGridLayout, QGroupBox,
    QHBoxLayout, QLabel, QLineEdit,
    QPlainTextEdit, QPushButton, QSizePolicy, 
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

def setting_loop_number(number: int) -> None:
    config.number_of_loops = number

class PopUpDialog(QDialog):
    def __init__(self, msg: str, title: str, parent=None) -> None:
        super(PopUpDialog, self).__init__(parent)

        self.setWindowTitle(title)
        self.resize(320, 100)

        layout = QHBoxLayout()

        label = QLabel(msg)
        label.setAlignment(Qt.AlignCenter) # type: ignore

        layout.addWidget(label)

        self.setLayout(layout)

class SettingWindow(QDialog):
    def __init__(self, parent=None) -> None:
        super(SettingWindow, self).__init__(parent)

        self.setWindowTitle("Setting Serial Port")
        self.resize(550, 230)

        self.port_number = config.serial_port

        # set the layout
        layout = QGridLayout()

        layout.addWidget(self._serial_port_group(), 0, 0)
        self.setLayout(layout)
        
    def _refresh_ports_list(self) -> None:
        self.port_list.setPlainText(list_com_port())

    def _serial_port_group(self):
        group_box = QGroupBox("Setting Serial Port", self)

        set_port = QPushButton("Simpan Setting", self)
        set_port.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        set_port.clicked.connect(self._save_settings)

        port_number_label = QLabel("Serial Port: ")
        self.port_number_input = QLineEdit(self.port_number, self)

        self.loop_number = QLineEdit(str(config.number_of_loops), self)

        refresh_port_button = QPushButton("Refresh Daftar Ports")
        refresh_port_button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        refresh_port_button.clicked.connect(self._refresh_ports_list)

        self.port_list = QPlainTextEdit(self)
        self.port_list.insertPlainText(list_com_port())

        grid = QGridLayout()
        grid.addWidget(port_number_label, 0, 0)
        grid.addWidget(self.port_number_input, 0, 1)

        grid.addWidget(set_port, 0, 2, 2, 1)
        grid.addWidget(refresh_port_button, 0, 3, 2, 1)

        grid.addWidget(QLabel("Jumlah Perulangan"), 1, 0)
        grid.addWidget(self.loop_number, 1, 1)

        grid.addWidget(QLabel("Isi 'Jumlah Perulangan' 0 jika ingin manual stop."), 2, 0, 1, 4)
        grid.addWidget(self.port_list, 3, 0, 1, 4)

        group_box.setLayout(grid)
        return group_box

    def _save_settings(self):
        try:
            setting_loop_number(int(self.loop_number.text()))
            setting_serial_port(self.port_number_input.text())

            PopUpDialog("Berhasil menyimpan configurasi", "Setting Success", self).exec() 
        except ValueError:
            PopUpDialog("Input tidak Valid", "Value Error", self).exec() 

