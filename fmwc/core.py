import logging
import ast
import time
import os
import csv

from datetime import datetime
from typing import Union

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QGridLayout, QGroupBox, QLabel, QLineEdit,
    QMainWindow,QPushButton, QWidget,
)

import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas

import serial

import numpy as np

from numba import jit

from . import config
from .contrib import list_com_port, PopUpDialog, SettingWindow

class WindowApp(QMainWindow):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)

        self.setWindowTitle("FMWC Radar Launcher")
        self.resize(640, 480)
        
        self.start_get_data = True

        self.grid = QGridLayout()

        widget = QWidget()
        widget.setStyleSheet(
            """
            QWidget {
                background: #fffdfa;
            }
            """
        )

        self.grid.addWidget(self._top_button_group(), 0, 0)
        #  self.grid.addWidget(self._save_data_group(), 1, 0)

        self.grid.addWidget(self._respiro_graph(), 0, 1)
        self.grid.addWidget(self._twr_graps(), 1, 1)

        self.grid.setColumnStretch(1, 2)

        widget.setLayout(self.grid)
        self.setCentralWidget(widget)

    def closeEvent(self, evnt) -> None:

        try:
            self.serial.close()
        except AttributeError:
            pass

        super(WindowApp, self).closeEvent(evnt)

    def _save_respiro_data(self) -> None:
        now = datetime.now().strftime("%D-%M-%YYYY-%H.%M.%S")

        try:
            if self.respiro_out and self.twr_out:
                pass
        except AttributeError:
            PopUpDialog("Tidak ada data yang di ambil.", "ERROR: Data kosong", self).exec() 
            return

        dest_path_resp = os.path.expanduser(f"~\\Documents\\Data_Respirasi_{now}.csv")
        dest_path_fft = os.path.expanduser(f"~\\Documents\\Data_FFT_{now}.csv")

        if os.path.exists(dest_path_resp) or os.path.exists(dest_path_fft):
            PopUpDialog(
                "File dengan nama yang diinput telah ada, silahkan gunakan nama lain",
                "ERROR: File Exist",
                self
            ).exec()
            return
        try:
            # Save data respirasi
            with open(dest_path_resp, 'w', newline="") as csvfile:
                writer = csv.writer(csvfile)
                for data in self.respiro_out:
                    writer.writerow(data)

            # Save data twr
            with open(dest_path_fft, 'w') as csvfile:
                writer = csv.writer(csvfile)
                for data in self.twr_out:
                    writer.writerow(data)

            # Show "Success" dialog
            PopUpDialog("Berhasil menyimpan Data", "Simpan Data Berhasil", self).exec() 

        except AttributeError as e:
            PopUpDialog(f"Tidak ada data yang ditangkap: {e}", "Data Error", self).exec()

    def _top_button_group(self) -> QWidget:
        group_box = QGroupBox("Menu Program")

        bsetting = QPushButton("Setting")
        bsetting.setStyleSheet(
            """
            QPushButton {
                background: #FFE9CD;
                color: #000;
                border: 0px;
            }
            QPushButton:hover {
                background: #FFDBAE;
            }
            """
        )
        bstart = QPushButton("Mulai Scan")
        bstart.setStyleSheet(
            """
            QPushButton {
                background: #BFE9FF;
                color: #000;
                border: 0px;
            }
            QPushButton:hover {
                background: #AAD0E3;
            }
            """
        )
        bstop = QPushButton("Stop Scan")
        bstop.setStyleSheet(
            """
            QPushButton {
                background: #F8D7D0;
                color: #000;
                border: 0px;
            }
            QPushButton:hover {
                background: #F19CA2;
            }
            """
        )
        bsave = QPushButton("Save Data")
        bsave.setStyleSheet(
            """
            QPushButton {
                background: #B7D7D9;
                color: #000;
                border: 0px;
            }
            QPushButton:hover {
                background: #95D5D9;
            }
            """
        )

        self.distance_label = QLineEdit("Jarak: 0")

        bstart.clicked.connect(self._start_process)
        bstop.clicked.connect(self._stop_get_data)
        bsetting.clicked.connect(self._launch_setting)
        bsave.clicked.connect(self._save_respiro_data)

        layout = QGridLayout()
        layout.setAlignment(Qt.AlignTop)

        layout.addWidget(bstart)
        layout.addWidget(bstop)
        layout.addWidget(bsetting)
        layout.addWidget(bsave)
        layout.addWidget(self.distance_label)

        group_box.setLayout(layout)
        return group_box

    def _save_data_group(self):
        group_box = QGroupBox("Simpan Data Respiro")

        bsave = QPushButton("Simpan Data")
        
        file_name_label = QLabel("Masukan Nama File")
        self.file_name = QLineEdit()

        layout = QGridLayout()
        layout.setAlignment(Qt.AlignTop)

        layout.addWidget(file_name_label, 0, 0)
        layout.addWidget(self.file_name, 0, 1)

        layout.addWidget(bsave, 1, 0, 1, 2)

        bsave.clicked.connect(self._save_respiro_data)

        group_box.setLayout(layout)
        return group_box

    def _start_process(self):
        self._set_serial_port()
        try:

            if not self.start_get_data:
                self.start_get_data = True

            self._get_data_respiro()
        except AttributeError:
            pass

    def _launch_setting(self):
        dialog = SettingWindow(self)
        dialog.exec_()

    def _set_serial_port(self):
        try:
            self.serial = serial.Serial(
                port=config.serial_port,
                baudrate=9600,
                parity=serial.PARITY_ODD,
                stopbits=serial.STOPBITS_TWO,
                bytesize=serial.SEVENBITS
            )
        except serial.SerialException as e:
            PopUpDialog(f"Error Serial Port: {e}", "Serial Port Not Found", self).exec()

    def _max_index_value(self, ls):
        """
        return maximum value and it's index from a list
        """

        maxval = max(ls)
        idx = ls.index(maxval)

        return maxval, idx

    def _twr_graps(self):
        group_box = QGroupBox("Magnitude")

        self.figure_twr = plt.figure()
        self.canvas_twr = FigureCanvas(self.figure_twr)

        grid = QGridLayout()
        grid.addWidget(self.canvas_twr, 1, 0)

        group_box.setLayout(grid)

        return group_box

    def _respiro_graph(self):
        group_box = QGroupBox("Phase")

        self.figure_resp = plt.figure()
        self.canvas_resp = FigureCanvas(self.figure_resp)

        grid = QGridLayout()
        grid.addWidget(self.canvas_resp, 1, 0)

        group_box.setLayout(grid)

        return group_box

    @staticmethod
    @jit(nopython=True)
    def _process_data_respiro(y_vec, yo_vec):
        return yo_vec[-1] * 0.0048 + yo_vec[-2] * 0.0195 + yo_vec[-3] * 0.0289 + yo_vec[-4] * 0.0193 + yo_vec[-5] * 0.0048 - y_vec[-1] - y_vec[-2] * -2.3695 - y_vec[-3] * 2.3140 - y_vec[-4] * -1.0547 - y_vec[-5] * 0.1874

    def _get_data_respiro(self):
        if not self.serial.isOpen():
            logging.info("[INFO] Open the serial port...")
            self.serial.open()

        # instead of ax.hold(False)
        self.figure_resp.clear()
        self.figure_twr.clear()

        # create an axis
        ax_reps = self.figure_resp.add_subplot(111)
        ax_twr = self.figure_twr.add_subplot(111)

        # Do some clean up, just to make sure
        self.serial.flushInput()
        self.serial.flushOutput()

        self.serial.write(str.encode("oF"))
        time.sleep(0.5)
        self.serial.write(str.encode("oP"))

        y_vec = np.linspace(0, 0, 512)[:-1]
        yo_vec = np.linspace(0, 1, 512)[:-1]
        x_vec = np.linspace(0, 1, 512)[:-1]

        self.respiro_out = []
        self.twr_out = []

        peak_index = -1

        while self.start_get_data:

            if not self.serial.isOpen():
                break

            try:
                # Try parsing data coming
                distance = ast.literal_eval(self.serial.readline().decode("utf-8"))
            except (SyntaxError, UnicodeDecodeError):
                # Skip the loop if data can't be parsed
                continue

            if isinstance(distance, tuple):
                # Distance is a tuple
                self.distance_label.setText(f"Jarak: {distance[1]}")

            elif isinstance(distance, dict):
                # FFT and Phase have the same data type: dict
                fft_phase = distance.get("Phase")
                fft_mag = distance.get("FFT")

                if fft_phase and len(self.respiro_out) <= config.number_of_loops:
                    if peak_index < 0:
                        continue

                    yo_vec[-1] = float(fft_phase[peak_index]) * 57.29
                    y_vec[-1] = self._process_data_respiro(y_vec, yo_vec)

                    self.respiro_out.append(fft_phase[:512])

                    #  refresh and plot the data
                    ax_reps.clear()

                    line1, = ax_reps.plot(x_vec[462:], y_vec[462:], '-o', alpha=0.8)
                    line1.set_ydata(y_vec[462:])

                    if np.min(y_vec) <= line1.axes.get_ylim()[0] or np.max(y_vec) >= line1.axes.get_ylim()[1]:
                        plt.ylim([np.min(y_vec) - np.std(y_vec), np.max(y_vec) + np.std(y_vec)])

                    # refresh canvas
                    self.canvas_resp.draw_idle()
                    self.canvas_resp.flush_events()

                    y_vec = np.append(y_vec[1:], 0.0)

                elif fft_mag and len(self.twr_out) <= config.number_of_loops:
                    _, peak_index = self._max_index_value(fft_mag[:512])

                    self.twr_out.append(fft_mag[:512])

                    ax_twr.clear()
                    ax_twr.plot(fft_mag[:100])

                    self.canvas_twr.draw_idle()
                    self.canvas_twr.flush_events()

                elif len(self.respiro_out) >= config.number_of_loops and len(self.twr_out) >= config.number_of_loops and config.number_of_loops > 0:
                    self.start_get_data = False

        self.serial.close()
        PopUpDialog("Selesai mengambil data", "Done Scanning", self).exec()

    def _refresh_ports_list(self) -> None:
        self.port_list.setPlainText(list_com_port())

    def _stop_get_data(self) -> None:
        self.start_get_data = False

