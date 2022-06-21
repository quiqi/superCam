import serial

from connect.connect.serial_port import *
from connect.connect.bluetooth import Bluetooth
from connect.connect.web_camera import WebCamera


def factory(key: str, name: str, args):
    if key == 'port':
        return SerialPort(name, args)
    elif key == 'bt':
        return Bluetooth(name, args)
    elif key == 'wc':
        return WebCamera(name, args)
    else:
        return None
