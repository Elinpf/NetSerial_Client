from src.log import logger
from src.exceptions import SocketClosed
import select


class Socket():
    def __init__(self, socket):
        self._socket = socket

    def recv(self):
        try:
            stream = self._socket.recv(1024)
        except OSError:
            logger.debug('telnet connect socket was closed.')
            raise SocketClosed
        return stream

    def waitting_recv(self, recv_func=None):
        while True:
            ready = select.select([self._socket], [], [], 10)[0]
            if self.closed():
                raise SocketClosed  # ! not use yet

            if ready:
                break

        if recv_func:
            return recv_func()

        return self.recv()

    def send(self, data):
        return self.send_raw(data.encode())

    def send_raw(self, data):
        return self._socket.send(data)

    def send_line(self, data=""):
        if data is None:
            data = ''
        return self.send(data + "\r\n")

    def send_middle(self, data, length):
        padding = int((length - len(data)) / 2)
        return self.send_line(' ' * padding + data)

    def clear_line(self, length):
        self.send_raw(b'\x08'*length)
        self.send_raw(b' '*length + b'\x08'*length)

    def fileno(self):
        return self._socket.fileno()

    def closed(self):
        return self._socket._closed
