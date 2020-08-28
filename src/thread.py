import threading

class Thread():
    def __init__(self):
        self._tlist = []

    def __iter__(self):
        return self._tlist

    def __next__(self):
        next(self._tlist)

    def append(self, th):
        self._tlist.append(th)

    def has_alive_thread(self):
        return (True in [th.is_alive() for th in self._tlist])

    def clean_stoped_thread(self):
        # for th in self._tlist:
        #     if not th.is_alive():
        #         self._tlist.remove(th)

        (self._tlist.remove(th) for th in self._tlist if not th.is_alive())  # ^_^

    def function(self, func, name='', *args):
        th = threading.Thread(target=func, args=args, name=name)
        th.start()
        self.append(th)
