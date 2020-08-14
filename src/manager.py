from src.control import Controler
from src.serial_port import SerialPort


class Manager():

    def __init__(self, control, serial):
        self._control:Controler = control
        self._serial:SerialPort = serial

        self._serial.manager = self

    def recv_serial(self, stream):
        """
        recv from serial, then notic to connections
        """
        pass
