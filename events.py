import time
from curses import window
from typing import Coroutine

COROUTINES = []
TIC_TIMEOUT = 0.1


def add_coroutine(*coroutines: Coroutine):
    COROUTINES.extend(coroutines)


def loop(canvas: window):
    while True:
        for coro in COROUTINES.copy():
            try:
                coro.send(None)
            except StopIteration:
                COROUTINES.remove(coro)
                continue

        canvas.refresh()
        time.sleep(TIC_TIMEOUT)
