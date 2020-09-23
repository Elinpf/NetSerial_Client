from src.protocol import Protocol
from src.log import logger
from src.config import conf


class Register():
    """
    base first code is 0x1
    second code blow:
    |0x0| => request
    |0x1| => room id
    |0x2| => fin room id
    |0xe| => ERROR ROOM ID
    |0xf| => ERROR

    status:
    0x0 : init
    0x1 : get a request
    0x2 : wait room id
    0x4 : full
    """

    INIT_STATUS = 0x0
    WAIT_ROOM_ID_STATUS = 0x2
    FULL_STATUS = 0x4

    def __init__(self, room):
        self.room = room
        self.room_id = None
        self.status = self.INIT_STATUS

    def recv(self):
        res = self.room.recv()
        logger.debug('Register recv message: %s' % res)
        p = Protocol(res)
        first_code = p.get_int8()
        if first_code != 0x1:
            return b''   # ! bad idea

        return p

    def process(self):
        while not self.is_full():
            if self.status == self.INIT_STATUS:  # init
                self.send_request()

            elif self.status == self.WAIT_ROOM_ID_STATUS:  # wait room id
                self.get_room_id()

            else:
                self.send_error()

    def is_full(self):
        return self.status == self.FULL_STATUS

    def send_request(self):
        bs = self.get_proto_head(0x0)

        self.send(bs)
        self.status = self.WAIT_ROOM_ID_STATUS
        logger.debug('Regist: send request, bs:%s ,now status %s' %
                     (bs.get_packet(), self.status))

    def get_room_id(self):
        bs = self.recv()
        if not bs:
            return

        code = bs.get_int8()
        if code != 0x1:
            logger.error('Register: ger error room id code: %s' % code)
            return self.send_error()

        self.room_id = bs.get_str()
        logger.info('Register: Get a room id: %s' % self.room_id)

        conf._SSH_SERVER_TERMINAL_PORT = bs.get_str()
        logger.debug('Register: Get Server Terminal Port: %s' %
                     conf._SSH_SERVER_TERMINAL_PORT)
        self.send_room_id()

    def send_room_id(self):
        bs = self.get_proto_head(0x2)
        bs.add_str(self.room_id)
        self.send(bs)
        self.status = 0x4
        logger.debug('Register: send Fin room id code')

    def send_error(self):
        p = self.get_proto_head(0xf)
        self.send(p)
        self.status = self.INIT_STATUS
        logger.error('Register: send error packet, init status.')

    def send(self, p: Protocol):
        msg = p.get_packet()
        self.room.send(msg)

    def get_proto_head(self, code: int):
        bs = Protocol()
        bs.add_int8(0x1)
        bs.add_int8(code)
        return bs
