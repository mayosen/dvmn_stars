import time
from collections import deque
from curses import window
from typing import Coroutine

from obstacles import Obstacle

TIC_TIMEOUT = 0.1
TICS_PER_SECOND = round(1 / TIC_TIMEOUT)


class Obstacles:
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


class BlownObstacles:
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


class Game:
    _seconds = 0
    _year = 1957
    _finished = False

    PHRASES = {
        1957: "First Sputnik",
        1961: "Gagarin flew!",
        1969: "Armstrong got on the moon!",
        1971: "First orbital space station Salute-1",
        1981: "Flight of the Shuttle Columbia",
        1998: 'ISS start building',
        2011: 'Messenger launch to Mercury',
        2020: "Take the plasma gun! Shoot the garbage!",
    }

    @classmethod
    def get_score(cls):
        return cls._seconds

    @classmethod
    def get_year(cls):
        return cls._year

    @classmethod
    def get_phrase(cls):
        return f": {cls.PHRASES[cls._year]}" if cls._year in cls.PHRASES else ""

    @classmethod
    def finish(cls):
        cls._finished = True

    @classmethod
    def increment(cls):
        if not cls._finished:
            cls._seconds += 1
            if cls._seconds % 2 == 0:
                cls._year += 1


class EventLoop:
    _coroutines = deque()

    @classmethod
    def add_coroutine(cls, *coroutines: Coroutine):
        cls._coroutines.extend(coroutines)

    @classmethod
    def start(cls, canvas: window):
        while True:
            for coroutine in cls._coroutines.copy():
                try:
                    coroutine.send(None)
                except StopIteration:
                    cls._coroutines.remove(coroutine)

            canvas.refresh()
            time.sleep(TIC_TIMEOUT)
