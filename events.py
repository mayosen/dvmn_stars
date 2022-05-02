import time
from collections import deque
from curses import window
from typing import Coroutine

from obstacles import Obstacle

COROUTINES = deque()
TIC_TIMEOUT = 0.1


class obstacles:
    _obstacles = deque()

    @classmethod
    def add(cls, obstacle: Obstacle):
        cls._obstacles.append(obstacle)

    @classmethod
    def get(cls):
        return cls._obstacles

    @classmethod
    def remove(cls, obstacle: Obstacle):
        cls._obstacles.remove(obstacle)


class blown_obstacles:
    _blown_obstacles = deque()

    @classmethod
    def add(cls, obstacle: Obstacle):
        cls._blown_obstacles.append(obstacle)

    @classmethod
    def get(cls):
        return cls._blown_obstacles

    @classmethod
    def remove(cls, obstacle: Obstacle):
        cls._blown_obstacles.remove(obstacle)


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
