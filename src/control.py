from src.connect import Connection
from src.manager import Manager

class Controler():
    def __init__(self):
        self.clist = []
        self.manager:Manager = None

    def __iter__(self):
        return self.clist

    def __next__(self):
        next(self.clist)

    def append(self, conn:Connection):
        self.clist.append(conn)
        conn.control = self

    def close(self):
        for conn in self.clist:
            conn.close()

    def send(self, stream):
        """
        send stream to every connections
        """
        for conn in self.clist:
            conn.send(stream)

    def notice(self, stream):
        """
        connections notice control class when recv stream
        """
        self.manager.recv_control(stream)

