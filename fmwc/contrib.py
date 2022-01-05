from serial.tools.list_ports import comports

from . import config

def list_com_port() -> str:
    ports = comports()

    if not ports:
        return "Tidak ada perangkat yang terhubung!"

    ports = ["{}: {} [{}]\n".format(port, desc, hwid) for port, desc, hwid in sorted(ports)]
    ports = "".join(ports)

    return ports

def set_serial_port(port: str) -> None:
    config.serial_port = port
