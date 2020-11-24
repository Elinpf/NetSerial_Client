import select


def just_see():
    print('just see')
    return 'just see see'


class Menu():
    def __init__(self, client_socket):
        """client socket is local telnet socket"""
        self.socket = client_socket
        root_menu = MenuItem("Root Menu")

        menu_control_user = root_menu.register_submenu("Control User")
        menu_control_user.register_items('远程终端只能查看 (defualt)', just_see)

        self.current_menu = root_menu

        self.show_current_menu()
        self.watting_for_select()

    def show_current_menu(self):
        self.send(self.current_menu.name + "\n")

        _ = "\n".join(self.current_menu.show())
        self.send(_)
        self.send("\n")
        self.send("\n")
        self.send("please input your select: ")

    def recv(self):
        return self.socket.recv(1024)

    def send(self, msg):
        return self.socket.send(msg)

    def watting_for_select(self):
        while True:
            ready = select.select([self._socket], [], [], 10)[0]
            if ready and not self._socket._closed:
                c = self.recv()
                self.send(c + "\n")  # echo
                _select = self.current_menu.select(c)
                if _select is Item:
                    msg = _select.func()
                    self.send(msg + "\n")
                    break

                else:
                    self.current_menu = _select
                    self.show_current_menu()


class MenuItem():

    def __init__(self, item_name: str):
        self.name = item_name
        self.menus_and_items = []

    def register_submenu(self, menu_name):
        """
        item: MenuItem
        """
        menu = MenuItem(menu_name)
        self.menus_and_items.append(menu)
        return menu  # return new menu

    def register_items(self, item_name, func):
        self.menus_and_items.append(Item(item_name, func))
        return self

    def show(self):
        return_list = []

        index = 0
        for e in self.menus_and_items:
            return_list.append("{index}: {message}".format(index, e.name))

        return return_list

    def select(self, idx):
        idx = int(idx)
        if idx < 0 or idx > len(self.menus_and_items):
            return self

        return self.menus_and_items[idx]


class Item():
    def __init__(self, name, func):
        self.name = name
        self.func = func
