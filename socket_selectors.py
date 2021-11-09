import selectors
import socket

sel = selectors.DefaultSelector()


def accept(sock, mask):
    conn, addr = sock.accept()
    print('accepted', conn, 'from  ', addr)
    conn.setblocking(False)
    sel.register(conn, selectors.EVENT_WRITE, read)


def read(conn, mask):
    data = conn.recv(1024)
    if data:
        print('echoing', repr(data), 'to', conn)
        conn.send(data)
    else:
        print('closing ',conn)
        sel.unregister(conn)
        conn.close()


sock = socket.socket()
sock.bind(('127.0.0.1', 1234))
sock.listen(10000)
sock.setblocking(False)
sel.register(sock, selectors.EVENT_READ, accept)

while True:
    events = sel.select()
    for key, mask in events:
        callback = key.data
        callback(key.fileobj, mask)