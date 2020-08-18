import serial
import serial.tools.list_ports as port_list
import select
import threading
from src.log import logger
from config import conf
from src.manager import Manager


class SerialPort():

    def __init__(self):
        self.port: serial.Serial = None
        self._thread_stop = False
        self.manager:Manger = None

        self.check_conf()
        self.connection()

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

        logger.info('serial port configraution check finished')
        return

    def connection(self):
        try:
            self.port = serial.Serial(conf.serial_device, baudrate=conf.serial_baudrate, timeout=None,
                                      parity=serial.PARITY_NONE, bytesize=serial.EIGHTBITS, stopbits=serial.STOPBITS_ONE, xonxoff=False)
        except serial.serialutil.SerialException:
            logger.error("can't open serial %s, Exit..." % conf.serial_device)
            exit()

        self.port.flushInput()
        logger.info('serial port connection complete')

    def read(self):
        while not self._thread_stop:
            c = self.port.read()
            _ = self.port.inWaiting()
            c += self.port.read(_)

            stream = c.decode()
            self.manager.recv_serial(stream)
            logger.debug('serial port read stream -> %s' % stream)

    def thread_run(self):
        self._thread_stop = False
        th = threading.Thread(target=self.read, name='serial read')
        th.start()
        logger.info('thread start -> SerialPort.read()')

    def write_stream(self, stream):
        for s in stream:
            self.write(s)

    def write(self, c:int):
        c = chr(c).encode()
        self.port.write(c)
        logger.debug('serial port write -> %s' % c)

    def thread_stop(self):
        self._thread_stop = True            
