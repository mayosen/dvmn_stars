import curses
import asyncio
from random import randint, choice

import event_loop
import animate
from frames import read_frame, ship_frames, garbage_frames


# TODO: Перенести функции для мусора в animate


async def fly_garbage(canvas, garbage_frame, column, speed):
    canvas_rows, canvas_columns = canvas.getmaxyx()
    row = 0
    await animate.wait_for(randint(0, 30))

    while row < canvas_rows:
        animate.draw_frame(canvas, row, column, garbage_frame)
        await asyncio.sleep(0)
        animate.draw_frame(canvas, row, column, garbage_frame, True)
        row += speed


async def fill_orbit_with_garbage(canvas, frames):
    _, canvas_columns = canvas.getmaxyx()
    count = 5
    garbage = []

    def append_random_garbage():
        frame = choice(frames)
        _, frame_columns = animate.get_frame_size(frame)
        column = randint(0, canvas_columns - frame_columns - 1)
        # TODO: Баг с застреванием фрейма вверху
        # speed = choice((0.1, 0.2, 0.3, 0.4, 0.5))
        speed = 0.5

        garbage.append(
            fly_garbage(canvas, frame, column, speed)
        )
    
    for i in range(count):
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

    frames = read_frame(*ship_frames)
    ship = animate.get_ship(canvas, frames, speed=1)

    frames = read_frame(*garbage_frames)
    garbage = fill_orbit_with_garbage(canvas, frames)

    event_loop.add_coroutine(*stars, garbage, ship)
    event_loop.loop(canvas)


if __name__ == '__main__':
    curses.update_lines_cols()
    curses.wrapper(draw)
