import logging
import time
import ast

from typing import Union

from PyQt5.QtWidgets import (
    QDialog, QGridLayout, QLineEdit, QPushButton,
    QWidget, QGroupBox, QLabel
)

import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolBar

import serial

import numpy as np

from numba import jit

class TWRRespirationDetection(QDialog):
    def __init__(self, serial_port: str, baudrate: int, parent=None) -> None:
        super(TWRRespirationDetection, self).__init__(parent)

        self.setWindowTitle("TWR Respiration Detection")

        self.serial = serial.Serial(
            port=serial_port,
            baudrate=baudrate,
            parity=serial.PARITY_ODD,
            stopbits=serial.STOPBITS_TWO,
            bytesize=serial.SEVENBITS
        )

        self.figure = plt.figure()
        self.canvas = FigureCanvas(self.figure)
        self.toolbar = NavigationToolBar(self.canvas, self)

        # set the layout
        layout = QGridLayout()

        layout.addWidget(self.toolbar, 0, 0)
        layout.addWidget(self.canvas, 1, 0)
        layout.addWidget(self._setting_group(), 2, 0)
        self.setLayout(layout)

    def closeEvent(self, evnt) -> None:
        self.serial.close()
        time.sleep(4)
        super(TWRRespirationDetection, self).closeEvent(evnt)

    def _setting_group(self) -> QWidget:
        group_box = QGroupBox("Setting Pengambilan Data")

        loop_counter_label = QLabel("Berapa Kali Scan: ")
        self.loop_counter = QLineEdit(self)
        self.loop_counter.setText("10")

        self.run_button = QPushButton("Mulai Scan!")
        self.run_button.clicked.connect(self._get_data)

        h_box = QGridLayout()
        h_box.addWidget(loop_counter_label, 0, 0)
        h_box.addWidget(self.loop_counter, 0, 1)
        h_box.addWidget(self.run_button, 1, 0)
        #  h_box.addWidget(QLabel("Silahkan memilih program yang ingin dijalankan."), 1, 0, 1, 2)

        group_box.setLayout(h_box)
        return group_box

    def _get_data(self) -> Union[None, np.ndarray]:

        if not self.serial.isOpen():
            logging.info("[INFO] Trying to open the port...")
            self.serial.open()

        # instead of ax.hold(False)
        self.figure.clear()

        # create an axis
        ax = self.figure.add_subplot(111)

        # Do some clean up, just to make sure
        self.serial.flushInput()
        self.serial.flushOutput()

        self.serial.write(str.encode("oF"))
        #  self.serial.write(str.encode("oP"))

        self.run_button.setEnabled(False)
        for _ in range(int(self.loop_counter.text())):
            distance = ast.literal_eval(self.serial.readline().decode("utf-8"))

            if isinstance(distance, tuple):
                print("Jarak:", distance[1], end="\r")
            elif isinstance(distance, dict):
                fft_mag = np.asarray(distance.get("FFT"), dtype=np.float64)

                # refresh and plot the data
                ax.clear()
                ax.plot(fft_mag)

                # refresh canvas
                self.canvas.draw()
                self.canvas.draw_idle()
                self.canvas.flush_events()

        self.serial.close()
        time.sleep(4) # sleep for wating the ast really close
        self.run_button.setEnabled(True)


class RespiroAppr(QDialog):
    def __init__(self, serial_port: str, baudrate: int, parent=None) -> None:
        super(RespiroAppr, self).__init__(parent)

        self.setWindowTitle("Respiro Appr")

        self.serial = serial.Serial(
            port=serial_port,
            baudrate=baudrate,
            parity=serial.PARITY_ODD,
            stopbits=serial.STOPBITS_TWO,
            bytesize=serial.SEVENBITS
        )

        self.figure = plt.figure()
        self.canvas = FigureCanvas(self.figure)
        self.toolbar = NavigationToolBar(self.canvas, self)

        # set the layout
        layout = QGridLayout()

        btn = QPushButton("Mulai!")
        btn.clicked.connect(self._get_data)

        layout.addWidget(self.toolbar, 0, 0)
        layout.addWidget(self.canvas, 1, 0)
        layout.addWidget(btn, 2, 0)

        self.setLayout(layout)

    def closeEvent(self, evnt) -> None:
        self.serial.close()
        time.sleep(4)
        super(RespiroAppr, self).closeEvent(evnt)

    def _max_index_value(self, ls) -> Union[dict, None]:
        """
        return maximum value and it's index from a list
        """

        maxval = max(ls)
        idx = ls.index(maxval)

        return {"val": maxval, "index": idx}

    @staticmethod
    @jit(nopython=True)
    def _process_data(y_vec, yo_vec):
        # Get ready for a loooong calculation
        # Not me, blame to other
        return yo_vec[-1] * 0.0048 + yo_vec[-2] * 0.0195 + yo_vec[-3] * 0.0289 + yo_vec[-4] * 0.0193 + yo_vec[-5] * 0.0048 - y_vec[-1] - y_vec[-2] * -2.3695 - y_vec[-3] * 2.3140 - y_vec[-4] * -1.0547 - y_vec[-5] * 0.1874

    def _get_data(self):
        if not self.serial.isOpen():
            logging.info("[INFO] Trying to open the port...")
            self.serial.open()

        # instead of ax.hold(False)
        self.figure.clear()

        # create an axis
        ax = self.figure.add_subplot(111)

        # Do some clean up, just to make sure
        self.serial.flushInput()
        self.serial.flushOutput()

        #  self.serial.write(str.encode("oF"))
        #  time.sleep(0.5)
        self.serial.write(str.encode("oP"))

        # TODO Refactor Me PLSSS
        y_vec = np.linspace(0, 1, 101)[:-1]
        yo_vec = np.linspace(0, 1, 101)[:-1]
        x_vec = np.linspace(0, 1, 101)[:-1]

        while True:

            if not self.serial.isOpen():
                break

            distance = ast.literal_eval(self.serial.readline().decode("utf-8"))

            if isinstance(distance, tuple):
                print("Jarak:", distance[1], end="\r")
                #  pass
            elif isinstance(distance, dict):

                if distance.get("Phase") is None:
                    continue

                fft_phase = distance.get("Phase")

                yo_vec[-1] = float(fft_phase[2]) * 57.29
                #  y_vec[-1] = yo_vec[-1] * 0.0048 + yo_vec[-2] * 0.0195 + yo_vec[-3] * 0.0289 + yo_vec[-4] * 0.0193 + yo_vec[-5] * 0.0048 - y_vec[-1] - y_vec[-2] * -2.3695 - y_vec[-3] * 2.3140 - y_vec[-4] * -1.0547 - y_vec[-5] * 0.1874
                y_vec[-1] = self._process_data(y_vec, yo_vec)

                #  refresh and plot the data
                ax.clear()

                line1, = ax.plot(x_vec, y_vec, '-o', alpha=0.8)
                line1.set_ydata(y_vec)

                if np.min(y_vec) <= line1.axes.get_ylim()[0] or np.max(y_vec) >= line1.axes.get_ylim()[1]:
                    plt.ylim([np.min(y_vec) - np.std(y_vec), np.max(y_vec) + np.std(y_vec)])

                # refresh canvas
                self.canvas.draw()
                self.canvas.draw_idle()
                self.canvas.flush_events()

                y_vec = np.append(y_vec[1:],0.0)

