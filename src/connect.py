import threading
import select
from src.log import logger
from src.variable import gvar
from src.config import conf


class Connection():

    def __init__(self):
        self.control = None
        self._thread_stop = False

    def thread_stop(self):
        self._thread_stop = True

    def init_tcp(self):
        raise NotImplementedError

    def recv(self):
        """
        recv data from tcp, then give to manager
        """
        raise NotImplementedError

    def send(self):
        """
        recv from manager, then send to tcp
        """
        raise NotImplementedError

    def thread_run(self):
        self._thread_stop = False
        th = threading.Thread(target=self.run, name='Connection run')
        th.start()
        gvar.thread.append(th)

        logger.info('thread start -> Connection.run()')

    def run(self):
        raise NotImplementedError

    def close(self):
        raise NotImplementedError

    def fileno(self):
        raise NotImplementedError


class ConnectionTelnet(Connection):

    def __init__(self, socket):
        self._socket = socket
        logger.info('establish a new telnet session')

    def clean_text(self, text):
        """
        ignore telnet negotiate code
        """
        if not text:
            return ""

        elif text[0] == 255:
            return ""

        elif text[0] == 13:
            return b'\r'

        return text

    def init_tcp(self):
        """
        set up telnet
        """
        # IAC WILL ECHO
        self._socket.send(bytes.fromhex('fffb01'))

        # IAC DONT ECHO 这个无法使用
        # self._socket.send(bytes.fromhex('fffe01'))

        # don't want linemode
        self._socket.send(bytes.fromhex('fffb22'))

        self.send("*"*60 + "\r\n")
        self.send("                 NetSerial by Elin\r\n")
        self.send("View Project: https://github.com/Elinpf/NetSerial_Client\r\n")
        self.send("\r\n")

        if gvar.manager.is_connected_server():
            self.send("+ Server IP: %s \r\n" % conf.SSH_SERVER_IP_ADDRESS)
            self.send("+ Remote client connetion Port: %s\r\n" %
                      (conf.SSH_SERVER_PORT + 100))
            self.send("+ The Room id is: %s \r\n" % gvar.manager.get_room_id())
            self.send("\r\n")

        self.send("Press <Ctrl-c> to terminal this session\r\n")
        self.send("*"*60 + "\r\n")

        self.send("\r\n")
        self.send("You are now connected to console.\r\n")
        self.send("\r\n")

        logger.info('telnet initialize completed')

    def send(self, data):
        self._socket.send(data.encode())

    def recv(self):
        """
        recv from the telnet client. if host not connected to serial port,
        then try to open serial port frist.
        """
        try:
            stream = self._socket.recv(1024)
        except OSError:
            logger.debug('telnet connect socket was closed.')
            self.close()
            return

        if stream == b'\x03':
            self.close()
            return

        # if serial port is not open, retry connection.
        if b'\r' in stream and not gvar.manager.seial_port_is_connected():
            logger.debug("try to connection serial port")
            gvar.manager.read_serial_port()
            if not gvar.manager.seial_port_is_connected():
                # time.sleep(2)  # time to sleep if retry connection.
                return

        self.control.notice(self.clean_text(stream))
        return stream  # ! don't need

    def run(self):
        while not self._thread_stop:
            ready = select.select([self._socket], [], [], 10)[0]

            if ready and not self._socket._closed:
                self.recv()

    def close(self):
        self.thread_stop()
        self._socket.close()
        self.control.remove(self)

    def fileno(self):
        self._socket.fileno()


class ConnectionRoom(Connection):

    def __init__(self, channel):
        self.channel = channel
        logger.info('establish a new Room session')
        super().__init__()

    def close(self):
        if self.channel:
            self.thread_stop()
            self.channel.close()
            self.control.remove(self)
            self.channel = None

    def fileno(self):
        self.channel.fileno()

    def init_tcp(self):
        pass

    def recv(self):
        select.select([self.channel], [], [], 10)

        if self.channel.recv_ready():
            res = self.channel.recv(50)
            return res

        return b''

    def run(self):
        while not self._thread_stop:
            stream = self.recv()
            self.control.notice(stream)

    def send(self, msg):
        self.channel.send(msg)
