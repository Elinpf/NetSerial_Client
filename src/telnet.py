import socket
import select
import threading
from src.log import logger
from src.connect import ConnectionTelnet
from src.config import conf
from src.variable import gvar


class Telnet():
    def __init__(self, port=conf.TELNET_PORT):

        self._listen_port = port

        self.listener: socket.socket = None
        self.manager = None
        self._thread_stop = False

        self.start_listening()

    def start_listening(self):
        self.listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.listener.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.listener.bind(('127.0.0.1', self._listen_port))
        self.listener.listen()

        logger.debug('Telnet.Start_linsten OK...')

    def run(self):
        while not self._thread_stop:
            ready = select.select([self.listener], [], [], 2)[0]

            if self.listener._closed:
                self.thread_stop()
                continue

            for _ in ready:  # establish new TCP session
                try:
                    _socket, address = self.listener.accept()
                    conn = ConnectionTelnet(_socket)
                    self.manager.add_connection(conn)
                except Exception as e:
                    logger.error(
                        'telnet listening catch a exception -> %s' % e)

        self.close()

    def thread_run(self):
        self._thread_stop = False
        th = threading.Thread(target=self.run, name='telnet run')
        th.start()
        gvar.thread.append(th)
        logger.info('thread start -> Telnet.run()')

    def thread_stop(self):
        self._thread_stop = True

    def close(self):
        self.listener.close()
