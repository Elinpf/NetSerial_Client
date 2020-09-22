from src.register import Register


class Room():
    def __init__(self, conn):
        self.conn = conn
        self.register = Register(self)

    def regist(self):
        if not self.register.is_full():
            self.register.process()

    def is_regist(self):
        return self.register.is_full()

    def room_id(self):
        return self.register.room_id

    def recv(self):
        return self.conn.recv()

    def send(self, msg):
        self.conn.send(msg)

    def close(self):
        if self.conn:
            self.conn.close()
            self.conn = None
