from src.control import Controler
from src.serial_port import SerialPort
from src.manager import Manager
from src.variable import gvar


# set up controler
control = Controler()

# set up serial port
serial_port = SerialPort()
# serial_port.thread_connection()

# set up manager
gvar.manager = Manager()
gvar.manager.serial = serial_port
gvar.manager.control = control
gvar.manager.thread_start()

# set up telnet
gvar.manager.listening_telnet()

if gvar.manager.connect_server():
    gvar.manager.regist_room()

gvar.manager.wait_keyboard_interrupt()
