from src.exceptions import StructError

class Protocol():

    def __init__(self, bs=None):
        if bs:
            self.bs = bytearray(bs)
        else:
            self.bs = bytearray(0)

    def add_int8(self, val:int):
        bytes_value = bytearray(val.to_bytes(1, byteorder='little'))
        self.bs += bytes_value

    def add_str(self, val:str):
        bytes_val = bytearray(val.encode(encoding='utf-8'))
        length = bytearray(len(bytes_val).to_bytes(2, byteorder='little'))
        self.bs += (length + bytes_val)

    def get_int8(self):
        try:
            res = self.bs[:1]
            self.bs = self.bs[1:]
            return int.from_bytes(res, byteorder='little')
        except:
            raise StructError

    def get_str(self):
        try:
            length = int.from_bytes(self.bs[:2], byteorder='little')
            res = self.bs[2:length + 2]

            self.bs = self.bs[2 + length:]
            return res.decode(encoding='utf-8')
        except:
            raise StructError

    def get_packet(self):
        return self.bs

        