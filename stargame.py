import curses

import events
from objects import get_stars, get_ship, fill_orbit_with_garbage
from obstacles import show_obstacles


def draw(canvas):
    curses.use_default_colors()
    curses.curs_set(False)
    canvas.nodelay(True)

    stars = get_stars(canvas)
    ship = get_ship(canvas, speed=3)
    garbage_spawner = fill_orbit_with_garbage(canvas)
    obstacle_viewer = show_obstacles(canvas, events.obstacles.get())

    events.add_coroutine(*stars, ship, obstacle_viewer, garbage_spawner)
    events.loop(canvas)


if __name__ == '__main__':
    curses.update_lines_cols()
    curses.wrapper(draw)
