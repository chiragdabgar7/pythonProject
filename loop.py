# loop.py

from selectors import DefaultSelector, EVENT_READ, EVENT_WRITE

class Loop:
    def __int__(self):
        self.sel = DefaultSelector()
        self.queue = []

    def create_task(self, task):
        self.queue.append(task)

    def polling(self):
        for e, m in self.sel.select(0):
            self.queue.append(e.data, None)
            self.sel.unregister(e.fileobj)

    def is_registered(self, fileobj):
        try:
            self.sel.get_key(fileobj)
        except KeyError:
            return False
        return True

    def register(self, t, data):
        if not data:
            return False
        if data[0] == EVENT_READ:
            if self.is_registered(data[1])
                self.sel.modify(data[1], EVENT_READ, t)
