from typing import Counter
from src.exceptions import SocketClosed
from src.config import conf
from src.variable import gvar


def remote_user_just_read():
    conf.REMOTE_USER_MODIFY = False
    return "remote user can't modify"


def remote_user_read_and_modify():
    conf.REMOTE_USER_MODIFY = True
    return "remote user can modify"


def get_room_id():
    room_id = gvar.manager.get_room_id()
    return ("the room id is: %s" % room_id)


def close_menu():
    pass


class Menu():
    def __init__(self, client_socket):
        """client socket is local telnet socket"""
        self.socket = client_socket
        root_menu = MenuItem("Root Menu")

        # User Control
        menu_user_control = root_menu.register_submenu("User Control")

        if conf.REMOTE_USER_MODIFY:
            pand1 = ''
            pand2 = '*'
        else:
            pand1 = '*'
            pand2 = ''

        menu_user_control.register_items(
            '远程终端只能查看  %s' % pand1, remote_user_just_read)
        menu_user_control.register_items(
            '远程终端可看可修改  %s' % pand2, remote_user_read_and_modify)

        #  Room Control
        menu_room_control = root_menu.register_submenu("Room Control")
        menu_room_control.register_items('查看 room id', get_room_id)

        self.current_menu = root_menu

    def open(self):
        self.show_current_menu()
        self.waitting_for_select()

    def show_current_menu(self):
        self.send_line()
        self.send_line('-' * 40)
        self.send_middle(self.current_menu.name, 40)
        self.send_line('-' * 40)

        self.send(self.current_menu.show())
        self.send_line()
        self.send_line()
        self.send("please input your select: ")

    def recv(self):
        return self.socket.recv()

    def send(self, msg):
        if msg is None:
            msg = ''

        return self.socket.send(msg)

    def send_line(self, msg=''):
        return self.socket.send_line(msg)

    def send_middle(self, msg, length):
        return self.socket.send_middle(msg, length)

    def waitting_for_select(self):
        while True:
            try:
                c = self.socket.waitting_recv()
                self.send_line(c.decode())  # echo
                _select = self.current_menu.select(c)
                if isinstance(_select, Item):
                    msg = _select.func()
                    self.send_line(msg)
                    break

                else:
                    self.current_menu = _select
                    self.show_current_menu()
            except SocketClosed:
                return  # ! WRONG


class MenuItem():

    def __init__(self, item_name: str, father_menu=None):
        self.name = item_name
        self.menus_and_items = {}
        self.father_menu = father_menu
        self.register_zero()
        self.idx = 1

    def register_zero(self):
        if not self.father_menu:
            desc = 'close menu'
            item = Item('close menu', close_menu)
            self.menus_and_items[0] = {'desc': desc, 'klass': item}

        else:
            desc = 'back to %s' % self.father_menu.name
            self.menus_and_items[0] = {'desc': desc, 'klass': self.father_menu}

    def register_submenu(self, menu_name, desc=''):
        """
        item: MenuItem
        """
        if not desc:
            desc = menu_name

        menu = MenuItem(menu_name, father_menu=self)
        self.menus_and_items[self.idx] = {'desc': desc, 'klass': menu}
        self.idx += 1

        return menu  # return new menu

    def register_items(self, item_name, func, desc=''):
        if not desc:
            desc = item_name

        self.menus_and_items[self.idx] = {
            'desc': desc, 'klass': Item(item_name, func)}
        self.idx += 1
        return self

    def show(self):
        return_list = []

        for i, v in self.menus_and_items.items():
            if i == 0:
                continue

            return_list.append("%s: %s" % (str(i), v['desc']))

        return_list.append("")
        return_list.append("0: %s" % self.menus_and_items[0]['desc'])

        return "\r\n".join(return_list)

    def select(self, idx):
        try:
            idx = int(idx)
        except:
            return self

        if idx < 0 or idx >= len(self.menus_and_items):
            return self

        return self.menus_and_items[idx]['klass']


class Item():
    def __init__(self, name, func):
        self.name = name
        self.func = func
