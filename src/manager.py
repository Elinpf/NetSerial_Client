import telnetlib
from paramiko.ssh_exception import SSHException
from src.ssh import SSHClient
from src.connect import ConnectionRoom
from src.room import Room
from src.config import conf
from src.log import logger
from src.variable import gvar
from src.telnet import Telnet
from src.update import Update


class Manager():

    def __init__(self):
        self._control = None
        self._serial = None
        self._room = None
        self._telnet: Telnet = None
        self.ssh_client = None
        self._update = None

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
        # serial port
        self._serial.thread_run()

        # update check
        self._update = Update()
        self._update.thread_run()

    def serial_port_is_connected(self):
        return self._serial.is_connected()

    def read_serial_port(self):
        self._serial.thread_run()

    def try_to_connect_serial_port(self):
        if not self.serial_port_is_connected():
            logger.debug("try to connection serial port")
            gvar.manager.read_serial_port()
        return self.serial_port_is_connected()

    # =====================

    def check_server_port_is_open(self):
        """
        check with server connection and port is open
        but there have some problem, server point will print SSH Error on logbuf
        """
        try:
            tel = telnetlib.Telnet(host=conf.SSH_SERVER_IP_ADDRESS,
                                   port=conf.SSH_SERVER_PORT, timeout=1)
            tel.close()
            return True
        except:
            logger.info(
                "can't connect ssh server, please check the internet setting.")
            return False

    def connect_server(self):
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

            return self.is_connected_server()
        except SSHException:
            logger.error(
                "can't connect netserial server, please contact the administrator.")
            raise SSHException

        except Exception:
            logger.exception("something wrong with the netserial server.")
            raise Exception

    def regist_room(self):
        """
        regist to server, get a room id 
        """
        try:
            if not self.is_connected_server():
                self.connect_server()

            conn = ConnectionRoom(self.get_ssh_channel())

            self._room = Room(conn)
            self._room.regist()
            if self._control:
                self._control.append(conn)
                logger.debug('Manager: Room append in control list')

        except SSHException:
            return

    def get_ssh_channel(self):
        cl = self.ssh_client.channel
        if not cl:
            return False

        return cl

    def get_room_id(self):
        return self._room.room_id()

    def is_connected_server(self):
        return bool(self.ssh_client)  # ! something wrong

    def close_room(self):
        if not self._room:
            logger.info('not in room')
            return

        self.ssh_client.close()
        self._room.close()
        logger.info("close the room")

    # =====================
    def git_pull(self):
        return self._update.pull()

    # =====================

    def listening_telnet(self):
        self._telnet = Telnet()
        self._telnet.manager = self
        self._telnet.thread_run()

    def wait_keyboard_interrupt(self):
        import time

        logger.debug("Into waiting for keyboard interrupt")
        try:
            while gvar.thread.has_alive_thread():
                gvar.thread.clean_stoped_thread()
                time.sleep(50)
        except KeyboardInterrupt:
            logger.info("shutdown the program...")
            self.shutdown()
            gvar.thread.kill_all_thread()

            logger.info("Bye!")

    def shutdown(self):
        """
        Guarantee no threading.
        """
        for mod in [self._control, self._serial, self._telnet, self._room]:
            if mod:
                mod.close()
