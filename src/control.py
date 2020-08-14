from src.connect import Connection

class Controler():
    def __init__(self):
        self.clist = []

    def __iter__(self):
        self.idx = 0
        return self.clist

    def __next__(self):
        if idx < len(self.clist):
            _ = self.clist[self.idx]
            self.idx += 1
            return _
        else:
            raise StopIteration

    def append(self, conn:Connection):
        self.clist.append(conn)

    def close(self):
        for conn in self.clist:
            conn.close()
