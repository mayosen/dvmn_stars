import time
from typing import Coroutine

COROUTINES = []
TIC_TIMEOUT = 0.1


def add_coroutine(*coros: Coroutine):
    COROUTINES.extend(coros)


def start_loop(canvas):
    while True:
        for coro in COROUTINES.copy():
            try:
                coro.send(None)
            except StopIteration:
                COROUTINES.remove(coro)
        
        canvas.refresh()
        time.sleep(TIC_TIMEOUT)
