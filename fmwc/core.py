import logging
import time
import ast

from PyQt5.QtCore import QThread

import serial
import numpy as np

class TWRRespirationDetection:
    def __init__(self, serial_port: str, baudrate: int) -> None:
        #  super(TWRRespirationDetection, self).__init__(parent)

        self.serial = serial.Serial(
            port=serial_port,
            baudrate=baudrate,
            parity=serial.PARITY_ODD,
            stopbits=serial.STOPBITS_TWO,
            bytesize=serial.SEVENBITS
        )
        
    def run(self) -> None:

        if not self.serial.isOpen():
            logging.error("[ERROR] Cannot open the serial port!")
            return

        # Do some clean up, just to make sure
        self.serial.flushInput()
        self.serial.flushOutput()

        self.serial.write(str.encode("oF"))
        time.sleep(0.5)

        #  fphase = open(f'twrphase{None}.csv', "a")
        #  fmag = open(f'twrmag{None}.csv', "a")
        #  fphs = open(f'twrphs{None}.csv', "a")

        SIZE = 100
        y_vec = np.linspace(0, 1, SIZE)

        max_magnitude = {
            "Val": 0,
            "Index": 0
        }

        while True:
            distance = ast.literal_eval(self.serial.readline().decode("utf-8"))

            if isinstance(distance, tuple):
                print("Jarak:", distance[1], end="\r")

