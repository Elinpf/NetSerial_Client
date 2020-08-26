import socket
import threading
import select
from src.log import logger


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
        if text[0] == 255:
            return ""

        if text[0] == 13:
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

        self.send(
            "************************************************\r\n")
        self.send("        NetSerial by Elin\r\n")
        self.send("View: https://github.com/Elinpf/NetSerial\r\n")
        self.send("Press <Ctrl-c> to terminal this session\r\n")
        self.send(
            "************************************************\r\n")

        self.send("\r\n")
        self.send("You are now connected to console.\r\n")

        logger.info('telnet initialize completed')

    def send(self, data):
        self._socket.send(data.encode())
        logger.debug('connect send: %s' % data)

    def recv(self):
        stream = self._socket.recv(1024)
        logger.debug('ConnectionTelnet.recv -> %s' % stream)

        if stream == b'\x03':
            self.close()
            return
        self.control.notice(self.clean_text(stream))

    def run(self):
        while not self._thread_stop:
            ready = [self._socket]
            read = select.select(ready, ready, [], 2)[0]

            if ready:
                data = self.recv()

    def close(self):
        self.thread_stop()
        self._socket.close()
        self.control.remove(self)

    def fileno(self):
        self._socket.fileno()


class ConnectionRoom(Connection):

    def __init__(self, channel):
        self.channel = channel
        super().__init__()

    def close(self):
        self.thread_stop()

    def fileno(self):
        self.channel.fileno()

    def init_tcp(self):
        pass

    def recv(self):
        select.select([self.channel], [], [], 10)

        if self.channel.recv_ready():
            res = self.channel.recv(10)
            return res

        return b''

    def run(self):
        while not self._thread_stop:
            stream = self.recv()
            self.control.notice(stream)

    def send(self, msg):
        logger.debug('SSHConnection send steam -> %s' % msg)
        self.channel.send(msg)
