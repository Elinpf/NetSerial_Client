import telnetlib
from paramiko.ssh_exception import SSHException
from src.ssh import SSHClient
from src.connect import ConnectionRoom
from src.room import Room
from config import conf
from src.log import logger
from src.variable import gvar
from src.telnet import Telnet


class Manager():

    def __init__(self):
        self._control = None
        self._serial = None
        self._room = None
        self._telnet:Telnet = None
        self.ssh_client = None

    def control(self, ctrl):
        self._control = ctrl
        self._register(self._control)

    def serial(self, serial):
        self._serial = serial
        self._register(self._serial)

    control = property(None, control)
    serial = property(None, serial)

    def recv_serial(self, stream):
        """
        recv from serial, then notice to connections
        """
        self.send_control(stream)

    def send_serial(self, stream):
        """
        send to serial port, if recv from connections
        """
        self._serial.write_stream(stream)

    def recv_control(self, stream):
        """
        recv from connections, then notice to serial port
        """
        self.send_serial(stream)

    def send_control(self, stream):
        """
        send to connections, if recv from serial port
        """
        self._control.send(stream)

    def _register(self, klass):
        """
        need register SerialPort and Control in Manager
        """
        klass.manager = self

    def add_connection(self, conn):
        """
        append a connection in Controlor
        """
        self._control.append(conn)

    def thread_start(self):
        self._serial.thread_run()

    def check_server_connection(self):
        """
        check with server connection
        """
        try:
            telnetlib.Telnet(host=conf.SSH_SERVER_IP_ADDRESS,
                             port=conf.SSH_SERVER_PORT, timeout=1)
            return True
        except:
            logger.info(
                "can't connect ssh server, please check the internet setting.")
            return False

    def connect_server(self):
        if not self.check_server_connection():
            return

        self.ssh_client = SSHClient()
        try:
            self.ssh_client.connect_server(
                conf.SSH_SERVER_IP_ADDRESS, conf.SSH_SERVER_PORT, conf.SSH_SERVER_USERNAME, conf.SSH_SERVER_PASSWORD)
            logger.info('Connect to SSH Server')
            logger.debug('SSH Server IP Address -> %s' %
                         conf.SSH_SERVER_IP_ADDRESS)
            logger.debug('SSH Server Port -> %s' % conf.SSH_SERVER_PORT)
            logger.debug('SSH Connect Username -> %s' %
                         conf.SSH_SERVER_USERNAME)
        except SSHException:
            logger.error(
                "can't connect netserial server, please contact the administrator.")

        except Exception:
            logger.exception("something wrong with the netserial server.")

    def regist_room(self):
        """
        regist to server, get a room id 
        """
        conn = ConnectionRoom(self.get_ssh_channel())
        self._room = Room(conn)
        self._room.regist()
        if self._control:
            self._control.append(conn)
            logger.debug('Manager: Room append in control list')

    def get_ssh_channel(self):
        return self.ssh_client.channel

    def is_connected_server(self):
        return bool(self.ssh_client)

    def close_room(self):
        self._room.close()

    def listening_telnet(self):
        self._telnet = Telnet()
        self._telnet.manager = self
        self._telnet.thread_run()

    def wait_keyboard_interrupt(self):
        import time
        try:
            if gvar.thread.has_alive_thread():
                gvar.thread.clean_stoped_thread()
                time.sleep(100)
        except KeyboardInterrupt:
            logger.info("shutdown the program...")
            while gvar.thread.has_alive_thread():
                self.shutdown()

            logger.info("Bye!")

    def shutdown(self):
        for mod in [self._control, self._serial, self._telnet, self._room]:
            if mod:
                mod.close()