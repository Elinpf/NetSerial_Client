import socket
import select
import threading
from src.log import logger
from src.manager import Manager
from src.connect import ConnectTelnet


class Telnet():
    def __init__(self, port=23):

        self._listen_port = port

        self.listener: socket.socket = None
        self.manager:Manager = None
        self._thread_stop = False

        self.start_listening()

    def start_listening(self):
        self.listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.listener.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.listener.bind(('', self._listen_port))
        self.listener.listen()

        logger.debug('Telnet.Start_new_linsten OK...')

    def run(self):
        while not self._thread_stop:
            ready = []

            if self.listener:
                ready.append(self.listener)

            ready = select.select(ready, ready, [], 2)[0]

            for _ in ready:  # establish new TCP session
                if _ is self.listener:
                    _socket, address = self.listener.accept()
                    conn = ConnectTelnet(_socket)
                    self.manager.add_connection(conn)
                    conn.init_tcp()
                    conn.thread_run()

        self.close()

    def thread_run(self):
        self._thread_stop = False
        th = threading.Thread(target=self.run, name='telnet run')
        th.start()
        logger.info('thread start -> Telnet.run()')

    def thread_stop(self):
        self._thread_stop = True

    def close(self):
        self.listener.close()
