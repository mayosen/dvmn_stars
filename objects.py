import asyncio
import curses
from itertools import cycle
from random import randint, choice

import events
from events import add_coroutine, obstacles, blown_obstacles
from frames import SHIP_FRAMES, GARBAGE_FRAMES
from obstacles import Obstacle
from physics import update_speed
from utils import read_controls, draw_frame

STAR_SYMBOLS = ('*', '+', '.', ':')


async def wait_for(ticks):
    for _ in range(ticks):
        await asyncio.sleep(0)


async def blink(canvas, row, column, symbol=STAR_SYMBOLS[0]):
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


def get_stars(canvas, amount=50, offset_row=1, offset_column=1):
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


async def fire(canvas, start_row, start_column, rows_speed=-0.3, columns_speed=0):
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
        for obstacle in obstacles.get():
            if obstacle.has_collision(row, column):
                blown_obstacles.add(obstacle)
                obstacles.remove(obstacle)
                # TODO: спавнить еще мусор через некоторое время
                return

        canvas.addstr(round(row), round(column), symbol)
        await asyncio.sleep(0)
        canvas.addstr(round(row), round(column), ' ')
        row += rows_speed
        column += columns_speed


async def get_ship(canvas, speed=3, ship_row=15, ship_column=20):
    canvas_rows, canvas_columns = canvas.getmaxyx()
    first, second = SHIP_FRAMES
    frame = first
    frame_rows, frame_columns = frame.sizes
    frames_iterator = cycle([first, first, second, second])
    row_speed = column_speed = 0

    bottom_limit = canvas_rows - frame.rows
    right_limit = canvas_columns - frame.columns

    while True:
        rows_dir, columns_dir, space_pressed = read_controls(canvas)
        row_speed, column_speed = update_speed(
            row_speed, column_speed, rows_dir, columns_dir
        )
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

        if space_pressed:
            bullet_column = ship_column + frame.center
            bullet_row_speed = - (speed + 0.8)

            if column_speed > 0:
                bullet_column_speed = column_speed + 0.1
            elif column_speed == 0:
                bullet_column_speed = 0
            else:
                bullet_column_speed = column_speed - 0.1

            add_coroutine(
                fire(canvas, ship_row, bullet_column,
                     rows_speed=bullet_row_speed,
                     columns_speed=bullet_column_speed,
                     )
            )

        frame = next(frames_iterator)
        draw_frame(canvas, ship_row, ship_column, frame.frame)
        await asyncio.sleep(0)
        draw_frame(canvas, ship_row, ship_column, frame.frame, negative=True)


async def fly_garbage(canvas, obstacle: Obstacle, column, speed=0.2):
    canvas_rows, _ = canvas.getmaxyx()

    while obstacle.row < canvas_rows:
        if obstacle in blown_obstacles.get():
            blown_obstacles.remove(obstacle)
            return

        draw_frame(canvas, obstacle.row, column, obstacle.frame)
        await asyncio.sleep(0)
        draw_frame(canvas, obstacle.row, column, obstacle.frame, True)
        obstacle.row += speed

    obstacles.remove(obstacle)


async def fill_orbit_with_garbage(canvas):
    _, canvas_columns = canvas.getmaxyx()

    while True:
        frame = choice(GARBAGE_FRAMES)
        column = randint(0 - frame.center, canvas_columns - frame.center)
        obstacle = Obstacle(frame, column)
        obstacles.add(obstacle)
        garbage = fly_garbage(canvas, obstacle, column)
        events.add_coroutine(garbage)
        await wait_for(randint(10, 110))
