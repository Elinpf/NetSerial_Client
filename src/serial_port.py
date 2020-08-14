import serial
import serial.tools.list_ports as port_list
import select
from src.log import logger
import config
from src.manager import Manager


class SerialPort():

    def __init__(self):
        self.check_conf()
        self.connection()
        self.port: serial.Serial = None
        self._thread_stop = False
        self.manager:Manger = None

    def check_conf(self):
        if not conf.serial_device:
            logger.info(
                'No Serial Port specified in the configuration, find Serial Ports...')
            plist = port_list.comports()

            if not plist:
                logger.error("can't found any serial port, Exit...")
                exit()

            conf.serial_device = plist[0].device
            logger.info('Specifiy Serial Port > %s' % conf.serial_device)

        if not conf.serial_baudrate:
            logger.error(
                "No Serial Baudrate specified in the configuration, Set to 9600")
            conf.serial_baudrate = 9600

        if not conf.serial_timeout:
            logger.error(
                "No Serial Timeout specified in the configuration, Set to 60s")
            conf.serial_timeout = 60

        return

    def connection(self):
        try:
            self.port = serial.Serial(conf.serial_device, baudrate=conf.serial_baudrate, timeout=conf.serial_timeout,
                                      parity=serial.PARITY_NONE, bytesize=serial.EIGHTBITS, stopbits=serial.STOPBITS_ONE, xonxoff=False)
        except serial.serialutil.SerialException:
            logger.error("can't open serial %s, Exit..." % conf.serial_device)
            exit()

        self.port.flushInput()

    def read(self):
        self._thread_stop = False

        while not self._thread_stop:
            ready = select.select([self.port], [], [], 1)[0]

            if ready:
                bytes_to_read = self.port.inWaiting()
                c = self.port.read(bytes_to_read)
                if c and self._manager:
                    self._manager.notice(c.decode())

    def thread_stop(self):
        self._thread_stop = True            
