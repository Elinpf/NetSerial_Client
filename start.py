import ptvsd
from src.telnet import Telnet
from src.control import Controler
from src.serial_port import SerialPort
from src.manager import Manager

# ptvsd.debug_this_thread()

# set up controler
control = Controler()

# set up serial port
serial = SerialPort()

# set up manager
manager = Manager(control, serial)
manager.thread_start()

# set up telnet
telnet = Telnet()
telnet.manager = manager
telnet.thread_run()