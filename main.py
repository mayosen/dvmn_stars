import curses
import asyncio
from random import randint, choice
from typing import List

import events
import animate
from frames import GARBAGE_FRAMES, SHIP_FRAMES, Frame


# TODO: Перенести функции для мусора в animate


async def fly_garbage(canvas, frame: str, column, speed):
    canvas_rows, _ = canvas.getmaxyx()
    row = 0
    await animate.wait_for(randint(0, 110))

    while row < canvas_rows:
        animate.draw_frame(canvas, row, column, frame)
        await asyncio.sleep(0)
        animate.draw_frame(canvas, row, column, frame, True)
        row += speed


async def fill_orbit_with_garbage(canvas, frames: List[Frame]):
    _, canvas_columns = canvas.getmaxyx()
    count = 5
    garbage = []

    def append_random_garbage():
        frame = choice(frames)
        column = randint(0, canvas_columns - frame.columns - 1)
        speed = 0.2

        garbage.append(
            fly_garbage(canvas, frame.frame, column, speed)
        )

    for _ in range(count):
        append_random_garbage()

    while True:
        for coro in garbage.copy():
            try:
                coro.send(None)
            except StopIteration:
                garbage.remove(coro)
                append_random_garbage()

        await asyncio.sleep(0)


def draw(canvas):
    curses.use_default_colors()
    curses.curs_set(False)
    canvas.nodelay(True)

    stars = animate.get_stars(canvas, amount=50)
    ship = animate.get_ship(canvas, SHIP_FRAMES, speed=1)
    garbage = fill_orbit_with_garbage(canvas, GARBAGE_FRAMES)

    events.add_coroutine(*stars, ship, garbage)
    events.start_loop(canvas)


if __name__ == '__main__':
    curses.update_lines_cols()
    curses.wrapper(draw)
