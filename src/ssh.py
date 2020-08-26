import paramiko
import select

class SSHClient():

    def __init__(self):
        self.transport:paramiko.Transport = None
        self.channel  :paramiko.Channel   = None

    def connect_server(self, ip, port, username, password):
        self.transport = paramiko.Transport((ip, port))
        self.transport.connect(username=username, password=password)
        self.channel = self.transport.open_channel('session')

    def send(self, msg):
        self.channel.send(msg)

    def recv(self, msg):
        """
        recv data, timeout 2s
        if no data, return empty
        """
        select.select([self.channel], [], [], 2)

        if self.channel.recv_ready():
            return self.channel.recv()

        return ""

