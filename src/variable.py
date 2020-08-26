
class Global_variable():
    def __init__(self):
        # src.manager.Manger
        from src.manager import Manager
        self.manager = None

        # src.serial_port.SerialPort
        from src.serial_port import SerialPort
        self.serial_port = None

        # src.control.Controler
        from src.control import Controler
        self.control = None


gvar = Global_variable()
