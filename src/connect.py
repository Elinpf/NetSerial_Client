import socket
import threading

class Connection():

    def __init__(self):
        pass

    def init_tcp(self):
        raise NotImplementedError

    def recv_tcp(self):
        """
        recv data from tcp, then give to manager
        """
        raise NotImplementedError

    def send_tcp(self):
        """
        recv from manager, then send to tcp
        """
        raise NotImplementedError

    def thread_run(self):
        th = threading.Thread(target=self.run)
        th.start()

    def run(self):
        raise NotImplementedError

    def close(self):
        raise NotImplementedError

    def fileno(self):
        raise NotImplementedError

class ConnectTelnet(Connection):

    def __init__(self, socket):
        self._socket = socket

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

        self.send_tcp(
            "************************************************\r\n")
        self.send_tcp("NetSerial by Elin\r\n")
        self.send_tcp(
            "************************************************\r\n")

        self.send_tcp("\r\n")
        self.send_tcp("You are now connected to console.\r\n")

    def send_tcp(self, data):
        self._socket.send(data.encode())

    def recv_tcp(self):
        return self._socket.recv(1024)

    def close(self):
        self._socket.close()

    def fileno(self):
        self._socket.fileno()