import threading
import inspect
import ctypes


def _async_raise(th, exctype):
    tid = th.ident
    tid = ctypes.c_long(tid)
    """raises the exception, performs cleanup if needed"""
    if not inspect.isclass(exctype):
        exctype = type(exctype)
    res = ctypes.pythonapi.PyThreadState_SetAsyncExc(
        tid, ctypes.py_object(exctype))
    if res == 0:
        raise ValueError("invalid thread id")
    elif res != 1:
        # """if it returns a number greater than one, you're in trouble,
        # and you should call it again with exc=NULL to revert the effect"""
        ctypes.pythonapi.PyThreadState_SetAsyncExc(tid, None)
        raise SystemError("PyThreadState_SetAsyncExc failed")


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

        (self._tlist.remove(th)
         for th in self._tlist if not th.is_alive())  # ^_^

    def function(self, target, name='', *args):
        th = threading.Thread(target=target, args=args, name=name)
        th.start()
        self.append(th)

    def kill_all_thread(self):
        for th in self._tlist:
            try:
                _async_raise(th, SystemExit)
            except ValueError:
                pass

        # self._tlist = []
