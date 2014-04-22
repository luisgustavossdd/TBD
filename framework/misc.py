from threading import Lock

__lock = Lock()
def idgen():
    i = 0
    while 1:
        i += 1
        yield i


__id_generator = idgen()

def get_id():
    with __lock:
        return __id_generator.next()