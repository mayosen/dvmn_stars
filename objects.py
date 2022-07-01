import asyncio
import curses
from _curses import window
from itertools import cycle
from random import randint, choice

from events import TICS_PER_SECOND, EventLoop, Obstacles, BlownObstacles, Game
from frames import SHIP_FRAMES, GARBAGE_FRAMES, EXPLOSION_FRAMES, GAME_OVER_FRAME
from obstacles import Obstacle
from physics import update_speed
from utils import read_controls, draw_frame

STAR_SYMBOLS = ('*', '+', '.', ':')


async def wait_for(ticks):
    for _ in range(ticks):
        await asyncio.sleep(0)


async def blink(canvas: window, row, column, symbol):
    canvas.addstr(row, column, symbol, curses.A_DIM)
    await wait_for(randint(0, 30))

    while True:
        canvas.addstr(row, column, symbol)
        await wait_for(3)
        canvas.addstr(row, column, symbol, curses.A_BOLD)
        await wait_for(5)
        canvas.addstr(row, column, symbol)
        await wait_for(3)
        canvas.addstr(row, column, symbol, curses.A_DIM)
        await wait_for(20)


def get_stars(canvas: window, amount=50, offset_row=2, offset_column=2):
    rows, columns = canvas.getmaxyx()
    stars = [
        blink(
            canvas,
            randint(offset_row, rows - offset_row),
            randint(offset_column, columns - offset_column),
            choice(STAR_SYMBOLS)
        ) for _ in range(amount)
    ]

    return stars


async def fire(canvas: window, start_row, start_column, rows_speed=-0.3, columns_speed=0):
    row, column = start_row, start_column

    canvas.addstr(round(row), round(column), '*')
    await asyncio.sleep(0)
    canvas.addstr(round(row), round(column), 'O')
    await asyncio.sleep(0)
    canvas.addstr(round(row), round(column), ' ')

    row += rows_speed
    column += columns_speed
    symbol = '-' if columns_speed else '|'

    rows, columns = canvas.getmaxyx()
    max_row, max_column = rows - 1, columns - 1
    curses.beep()

    while 0 < row < max_row and 0 < column < max_column:
        for obstacle in Obstacles.get():
            if obstacle.has_collision(row, column):
                BlownObstacles.add(obstacle)
                Obstacles.remove(obstacle)
                EventLoop.add_coroutine(explode(canvas, row, column))
                return

        canvas.addstr(round(row), round(column), symbol)
        await asyncio.sleep(0)
        canvas.addstr(round(row), round(column), ' ')
        row += rows_speed
        column += columns_speed


async def get_ship(canvas: window, ship_row=15, ship_column=20):
    canvas_rows, canvas_columns = canvas.getmaxyx()
    first, second = SHIP_FRAMES
    frame = first
    frame_rows, frame_columns = frame.sizes
    frames_iterator = cycle([first, first, second, second])
    row_speed = column_speed = 0

    bottom_limit = canvas_rows - frame.rows
    right_limit = canvas_columns - frame.columns

    while True:
        for obstacle in Obstacles.get():
            if obstacle.has_collision(ship_row, ship_column, frame.rows, frame.columns):
                EventLoop.add_coroutine(show_game_over(canvas))
                return

        rows_dir, columns_dir, space_pressed = read_controls(canvas)
        row_speed, column_speed = update_speed(row_speed, column_speed, rows_dir, columns_dir)
        ship_row += row_speed
        ship_column += column_speed

        if ship_row < 0:
            ship_row = 0
        elif ship_row + frame_rows > canvas_rows:
            ship_row = bottom_limit

        if ship_column < 0:
            ship_column = 0
        elif ship_column + frame_columns > canvas_columns:
            ship_column = right_limit
        
        if space_pressed and Game.get_year() >= 1970:
            bullet_column = ship_column + frame.center
            bullet_row_speed = -(row_speed + 0.8)

            if column_speed > 0:
                bullet_column_speed = column_speed + 0.1
            elif column_speed == 0:
                bullet_column_speed = 0
            else:
                bullet_column_speed = column_speed - 0.1

            EventLoop.add_coroutine(fire(canvas, ship_row, bullet_column, bullet_row_speed, bullet_column_speed))

        frame = next(frames_iterator)
        draw_frame(canvas, ship_row, ship_column, frame.frame)
        await asyncio.sleep(0)
        draw_frame(canvas, ship_row, ship_column, frame.frame, negative=True)


async def fly_garbage(canvas: window, obstacle: Obstacle, column, speed=0.2):
    canvas_rows, _ = canvas.getmaxyx()

    while obstacle.row < canvas_rows:
        if obstacle in BlownObstacles.get():
            BlownObstacles.remove(obstacle)
            return

        draw_frame(canvas, obstacle.row, column, obstacle.frame)
        await asyncio.sleep(0)
        draw_frame(canvas, obstacle.row, column, obstacle.frame, True)
        obstacle.row += speed

    Obstacles.remove(obstacle)


async def fill_orbit_with_garbage(canvas: window):
    _, canvas_columns = canvas.getmaxyx()
    speeds = (0.1, 0.2, 0.3)

    while True:
        tics = get_garbage_delay_tics()

        if tics is not None:
            frame = choice(GARBAGE_FRAMES)
            column = randint(0 - frame.center, canvas_columns - frame.center)
            obstacle = Obstacle(frame, column)
            Obstacles.add(obstacle)
            garbage = fly_garbage(canvas, obstacle, column, choice(speeds))
            EventLoop.add_coroutine(garbage)
            await wait_for(tics)
        else:
            await asyncio.sleep(0)


async def explode(canvas: window, center_row, center_column):
    rows, columns = EXPLOSION_FRAMES[0].sizes
    corner_row = center_row - rows // 2
    corner_column = center_column - columns // 2
    curses.beep()

    for frame in EXPLOSION_FRAMES:
        draw_frame(canvas, corner_row, corner_column, frame.frame)
        await asyncio.sleep(0)
        draw_frame(canvas, corner_row, corner_column, frame.frame, negative=True)


async def show_game_over(canvas: window):
    for _ in range(3):
        curses.beep()
        await asyncio.sleep(0)

    Game.finish()
    frame = GAME_OVER_FRAME
    canvas_rows, canvas_columns = canvas.getmaxyx()
    row = (canvas_rows - frame.rows) // 2
    column = (canvas_columns - frame.columns) // 2

    while True:
        draw_frame(canvas, row, column, frame.frame)
        await asyncio.sleep(0)


def get_garbage_delay_tics():
    year = Game.get_year()

    if year < 1961:
        return None
    elif year < 1969:
        return 20
    elif year < 1981:
        return 14
    elif year < 1995:
        return 10
    elif year < 2010:
        return 8
    elif year < 2020:
        return 6
    else:
        return 2


async def game_counter(canvas: window):
    rows, _ = canvas.getmaxyx()

    def draw_info():
        message = f"Score: {Game.get_score():2d} | Year: {Game.get_year():4d}{Game.get_phrase():40s}"
        canvas.addstr(rows - 2, 2, message)

    while True:
        for _ in range(TICS_PER_SECOND - 1):
            draw_info()
            await asyncio.sleep(0)

        Game.increment()
        draw_info()
        await asyncio.sleep(0)
