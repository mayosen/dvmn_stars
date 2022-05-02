import curses
from curses import window
from random import randint, choice

import events
import objects
from frames import GARBAGE_FRAMES
from obstacles import show_obstacles, Obstacle


async def fill_orbit_with_garbage(canvas):
    _, canvas_columns = canvas.getmaxyx()

    while True:
        frame = choice(GARBAGE_FRAMES)
        column = randint(0 - frame.center, canvas_columns - frame.center)
        obstacle = Obstacle(frame, column)
        events.add_obstacle(obstacle)
        garbage = objects.fly_garbage(canvas, obstacle, column)
        events.add_coroutine(garbage)
        await objects.wait_for(randint(10, 110))


def draw(canvas: window):
    curses.use_default_colors()
    curses.curs_set(False)
    canvas.nodelay(True)

    stars = objects.get_stars(canvas)
    ship = objects.get_ship(canvas, speed=1)
    garbage_spawner = fill_orbit_with_garbage(canvas)
    obstacle_viewer = show_obstacles(canvas, events.get_obstacles())

    events.add_coroutine(*stars, ship, obstacle_viewer, garbage_spawner)
    events.loop(canvas)


if __name__ == '__main__':
    curses.update_lines_cols()
    curses.wrapper(draw)
