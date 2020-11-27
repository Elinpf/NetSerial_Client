from src.connect import Connection
from src.manager import Manager


class Controler():
    def __init__(self):
        self.clist = []
        self.manager: Manager = None

    def __iter__(self):
        return self.clist

    def __next__(self):
        next(self.clist)

    def append(self, conn: Connection):
        self.clist.append(conn)
        conn.control = self
        conn.init_tcp()
        conn.thread_run()

    def close(self):
        for conn in self.clist:
            conn.close()

    def remove(self, conn: Connection):
        self.clist.remove(conn)
        del conn

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
