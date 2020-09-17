import serial
import serial.tools.list_ports as port_list
import select
import threading
from src.log import logger
from config import conf
from src.manager import Manager
from src.variable import gvar


class SerialPort():

    def __init__(self):
        self.port: serial.Serial = None
        self._thread_stop = False
        self.manager: Manger = None

    def check_conf(self):
        if not conf.SERIAL_DEVICE:
            logger.info(
                'No Serial Port specified in the configuration, find Serial Ports...')
            plist = port_list.comports()

            if not plist:
                logger.error(
                    "can't found any serial port, Please check Serial Port")
                return

            conf.SERIAL_DEVICE = plist[0].device
            logger.info('Specifiy Serial Port > %s' % conf.SERIAL_DEVICE)

        if not conf.SERIAL_BAUDRATE:
            logger.error(
                "No Serial Baudrate specified in the configuration, Set to 9600")
            conf.SERIAL_BAUDRATE = 9600

        logger.info('serial port configraution check finished')
        return

    def connection(self):
        try:
            # params: timeout = None means forever
            self.port = serial.Serial(conf.SERIAL_DEVICE, baudrate=conf.SERIAL_BAUDRATE, timeout=None, write_timeout=4,
                                      parity=serial.PARITY_NONE, bytesize=serial.EIGHTBITS, stopbits=serial.STOPBITS_ONE, xonxoff=False)
        except serial.serialutil.SerialException:
            logger.error(
                "can't open serial %s, Please check the COM is open and retry..." % conf.SERIAL_DEVICE)
            raise(serial.SerialException)

        self.port.flushInput()
        logger.info('serial port \'%s\' connection complete' %
                    conf.SERIAL_DEVICE)

    def is_connected(self):
        # just check SerialPort is connected at first time.
        return bool(self.port)

    def read(self):
        if not self.is_connected():
            try:
                self.check_and_connection()
            except serial.SerialException:  # when can't open serial, then return
                return

        while not self._thread_stop:
            try:
                c = self.port.read()
                _ = self.port.inWaiting()
                c += self.port.read(_)
            except serial.SerialException:  # when close the serial port, maybe into this
                logger.debug('serial port was closed')
                return

            stream = c.decode()
            self.manager.recv_serial(stream)

    def thread_run(self):
        self._thread_stop = False
        th = threading.Thread(target=self.read, name='serial read')
        th.start()
        gvar.thread.append(th)
        logger.info('thread start -> SerialPort.read()')

    def check_and_connection(self):
        self.check_conf()
        self.connection()

    def thread_connection(self):
        th = threading.Thread(
            target=self.check_and_connection, name='serial connection')
        th.start()
        gvar.thread.append(th)

    def write_stream(self, stream):
        for s in stream:
            self.write(s)

    def write(self, c: int):
        c = chr(c).encode()
        try:
            self.port.write(c)
        except serial.serialutil.SerialTimeoutException:
            logger.exception("Serial write timeout")
            self.close()

    def thread_stop(self):
        self._thread_stop = True

    def close(self):
        self.thread_stop()
        if self.is_connected():
            self.port.close()
