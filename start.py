import ptvsd
from src.telnet import Telnet
from src.control import Controler
from src.serial_port import SerialPort
from src.manager import Manager
from src.variable import gvar

# ptvsd.debug_this_thread()

# set up controler
control = Controler()

# set up serial port
serial_port = SerialPort()
serial_port.check_conf()
serial_port.connection()

# set up manager
gvar.manager = Manager()
gvar.manager.serial = serial_port
gvar.manager.control = control
gvar.manager.thread_start()

# set up telnet
telnet = Telnet()
telnet.manager = gvar.manager
telnet.thread_run()

gvar.manager.connect_server()
gvar.manager.regist_room()