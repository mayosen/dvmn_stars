import curses

from events import EventLoop, Obstacles
from objects import get_stars, get_ship, fill_orbit_with_garbage, game_counter
from obstacles import show_obstacles


def draw(canvas: curses.window):
    curses.use_default_colors()
    curses.curs_set(False)
    canvas.nodelay(True)

    stars = get_stars(canvas)
    ship = get_ship(canvas)
    garbage_spawner = fill_orbit_with_garbage(canvas)
    game = game_counter(canvas)

    EventLoop.add_coroutine(*stars, ship, game, garbage_spawner)
    EventLoop.add_coroutine(show_obstacles(canvas, Obstacles.get()))

    EventLoop.start(canvas)


if __name__ == '__main__':
    curses.update_lines_cols()
    curses.wrapper(draw)
