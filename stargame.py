import asyncio
import curses
from curses import window
from random import randint, choice

import events
import objects
from frames import Frame, GARBAGE_FRAMES, SHIP_FRAMES
from obstacles import show_obstacles, Obstacle


async def fill_orbit_with_garbage(canvas, frames: list[Frame]):
    _, canvas_columns = canvas.getmaxyx()
    count = 5
    garbage = []
    obstacles = []

    def append_random_garbage():
        frame = choice(frames)
        column = randint(0, canvas_columns - frame.columns - 1)
        speed = 0.2

        garbage.append(
            objects.fly_garbage(canvas, frame.frame, column, speed)
        )
        # obstacles.append(Obstacle(0, column, frame.rows, frame.columns, frame.uid))

    for _ in range(count):
        append_random_garbage()

    while True:
        # await show_obstacles(canvas, obstacles)

        for coro in garbage.copy():
            try:
                coro.send(None)
            except StopIteration:
                garbage.remove(coro)
                append_random_garbage()

        await asyncio.sleep(0)


def draw(canvas: window):
    curses.use_default_colors()
    curses.curs_set(False)
    canvas.nodelay(True)

    stars = objects.get_stars(canvas, amount=50)
    ship = objects.get_ship(canvas, SHIP_FRAMES, speed=1)
    garbage = fill_orbit_with_garbage(canvas, GARBAGE_FRAMES)

    events.add_coroutine(*stars, ship, garbage)
    events.loop(canvas)


if __name__ == '__main__':
    curses.update_lines_cols()
    curses.wrapper(draw)
