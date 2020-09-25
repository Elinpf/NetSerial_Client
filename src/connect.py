import select
import threading

from src.banner import banner
from src.config import conf
from src.log import logger
from src.variable import gvar


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
            return b''

        elif text[0] == 255:
            return b''

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

        if conf._success_check_github:  # if github have new version
            self.send(
                "A new version is detected, do you want to update?(Y/n):")
            while True:
                c = bytes.decode(self.recv())
                if not c:
                    continue
                elif (c.lower() == 'y'):
                    self.send_line(c)  # echo answer
                    self.send_line(gvar.manager.git_pull())
                    break
                elif (c.lower() == 'n'):
                    self.send_line(c)  # echo answer
                    break

        self.send_line("*"*60)
        self.send_line("                 NetSerial by Elin")
        self.send_line(
            "View Project: %s" % banner.REPOSITORY_ADDRESS)
        self.send_line("Version: %s" % banner.VERSION)
        self.send_line()

        # check connect to server point
        if not gvar.manager.is_connected_server():
            self.send_line(" * Try to connect NetSerial Server: %s" %
                           conf.SSH_SERVER_IP_ADDRESS)
            if gvar.manager.connect_server():
                gvar.manager.regist_room()
                self.send_line(" + Successfully connected")
            else:
                self.send_line(" - Connection failed")
                self.send_line()

        if gvar.manager.is_connected_server():
            self.send_line(" + Server IP: %s " % conf.SSH_SERVER_IP_ADDRESS)
            self.send_line(" + Remote client connetion Port: %s" %
                           (conf._SSH_SERVER_TERMINAL_PORT))
            self.send_line(" + The Room id is: %s " %
                           gvar.manager.get_room_id())
            self.send_line()

        self.send_line("Press <Ctrl-c> to terminal this session")
        self.send_line("*"*60 + "")

        self.send_line()

        # # need threading block
        # length = 0
        # if not gvar.manager.serial_port_is_connected():
        #     while not gvar.manager.try_to_connect_serial_port():
        #         length = self.send("Not connected to console")
        #         select.select([self._socket], [], [], 10)
        #         self.recv()
        #         self.clear_line(length)

        self.send_line("You are now connected to console.")
        self.send_line()

        logger.info('telnet initialize completed')

    def send(self, data):
        return self._socket.send(data.encode())

    def send_line(self, msg=""):
        return self.send(msg + "\r\n")

    def clear_line(self, length):
        # self._socket.send(bytes.fromhex('fff8'))
        self._socket.send(b'\x08'*length)
        self._socket.send(b' '*length + b'\x08'*length)

    def recv(self):
        """
        recv from the telnet client.
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

        return self.clean_text(stream)

    def notice(self, stream=b''):
        """
        Notice to Serial port
        if host not connected to serial port, then try to open serial port frist.
        """
        # if serial port is not open, retry connection.
        if b'\r' in stream and not gvar.manager.serial_port_is_connected():
            if not gvar.manager.try_to_connect_serial_port():
                return

        self.control.notice(stream)
        return stream

    def run(self):
        while not self._thread_stop:
            ready = select.select([self._socket], [], [], 10)[0]

            if ready and not self._socket._closed:
                c = self.recv()
                if c:
                    self.notice(c)

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
            logger.info("room connection was closed")

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
        try:
            self.channel.send(msg)
            return len(msg)
        except OSError:
            logger.error("server connection was closed.")
            gvar.manager.close_room()
