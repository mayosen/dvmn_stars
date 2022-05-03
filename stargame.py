import curses
from _curses import window

import events
from objects import get_stars, get_ship, fill_orbit_with_garbage, game_counter
from obstacles import show_obstacles


def draw(canvas: window):
    curses.use_default_colors()
    curses.curs_set(False)
    canvas.nodelay(True)

    stars = get_stars(canvas)
    ship = get_ship(canvas)
    garbage_spawner = fill_orbit_with_garbage(canvas)
    # obstacle_viewer = show_obstacles(canvas, events.Obstacles.get())
    game = game_counter(canvas)

    events.add_coroutine(*stars, ship, game, garbage_spawner)
    # events.add_coroutine(*stars, ship, obstacle_viewer, game, garbage_spawner)
    events.loop(canvas)


if __name__ == '__main__':
    curses.update_lines_cols()
    curses.wrapper(draw)
