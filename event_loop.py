import time


coroutines = []
tic_timeout = 0.1


def add_coroutine(*coros):
    coroutines.extend(coros)


def loop(canvas):
    while True:
        for coro in coroutines.copy():
            try:
                coro.send(None)
            except StopIteration:
                coroutines.remove(coro)
        
        canvas.refresh()
        time.sleep(tic_timeout)
