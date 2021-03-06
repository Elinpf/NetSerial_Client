import select
from src.exceptions import SocketClosed
import threading

from src.banner import banner
from src.config import conf
from src.log import logger
from src.variable import gvar
from src.menu import Menu
from src.socket import Socket


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
        self._socket = Socket(socket)
        self._block = Block()
        self._block.set()
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
        self._socket.send_raw(bytes.fromhex('fffb01'))

        # IAC DONT ECHO 这个无法使用
        # self._socket.send(bytes.fromhex('fffe01'))

        # don't want linemode
        self._socket.send_raw(bytes.fromhex('fffb22'))

        if conf._success_check_github:  # if github have new version
            self.send(
                "A new version is detected, do you want to update?(Y/n):", force=True)
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

        self.send_line("Press <Ctrl-n> to open Menu")
        self.send_line("*"*60 + "")

        self.send_line()

        # need threading block
        length = 0
        if not gvar.manager.serial_port_is_connected():
            while not gvar.manager.try_to_connect_serial_port():
                length = self.send(" [-] Not connected to console", True)
                select.select([self._socket], [], [], None)
                self.recv()
                self.clear_line(length)

        length = self.send_line("You are now connected to console.")

        self._block.unset()
        logger.info('telnet initialize completed')

    def send(self, data, force=False):
        """
        when init status , block the send channel
        force to send to terminal if want
        """
        if self._block.is_set():
            if not force:
                self._block.save_data(data)
                return 0

        return self._socket.send(data)

    def send_line(self, msg=""):
        return self.send(msg + "\r\n", True)

    def clear_line(self, length):
        self._socket.clear_line(length)

    def recv(self):
        """
        recv from the telnet client.
        """
        try:
            stream = self._socket.recv()

            # ctrl-n open menu
            if stream == b'\x0e':
                self._block.set()
                self.oepn_menu()
                self.send(self._block.freed_data())
                return

        except SocketClosed:
            logger.debug('telnet connect socket was closed.')
            self.close()
            return

        # logger.info("stream: %s" % stream)

        return self.clean_text(stream)

    def oepn_menu(self):
        Menu(self._socket).open()

    def notice(self, stream=b''):
        """
        Notice to Serial port
        if host not connected to serial port, then try to open serial port frist.
        """
        if stream is None:
            return

        # if serial port is not open, retry connection.
        if b'\r' in stream and not gvar.manager.serial_port_is_connected():
            if not gvar.manager.try_to_connect_serial_port():
                return

        if self._block.is_set():
            return

        self.control.notice(stream)
        return stream

    def run(self):
        while not self._thread_stop:
            _ = self._socket.waitting_recv(self.recv)
            self.notice(_)

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
            if conf.REMOTE_USER_MODIFY:
                self.control.notice(stream)

    def send(self, msg):
        try:
            self.channel.send(msg)
            return len(msg)
        except OSError:
            logger.error("server connection was closed.")
            gvar.manager.close_room()


class Block():
    def __init__(self):
        self._block = False
        self._data = []

    def set(self):
        self._block = True

    def unset(self):
        self._block = False

    def is_set(self):
        return self._block

    def save_data(self, data):
        if self.is_set():
            self._data.append(data)

    def freed_data(self):
        self.unset()
        d = ''.join(self._data)
        self._data.clear()
        return d
