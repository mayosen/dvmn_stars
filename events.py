import time
from collections import deque
from curses import window
from typing import Coroutine

from obstacles import Obstacle

COROUTINES = deque()
OBSTACLES = deque()
TIC_TIMEOUT = 0.1


def add_coroutine(*coroutines: Coroutine):
    COROUTINES.extend(coroutines)


def get_obstacles():
    return OBSTACLES


def add_obstacle(obstacle: Obstacle):
    OBSTACLES.append(obstacle)


def remove_obstacle(obstacle: Obstacle):
    OBSTACLES.remove(obstacle)


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
