import curses
import asyncio
from random import randint, choice
from itertools import cycle

from physics import update_speed
from event_loop import add_coroutines


def read_frame(name):
    """Read oneline animation from project folder."""

    with open(f'frames/{name}', 'r') as file:
        text = file.read()

    return text


def get_frame_size(text):
    """Calculate size of multiline text fragment.
    Return pair — number of rows and columns."""

    lines = text.splitlines()
    rows = len(lines)
    columns = max([len(line) for line in lines])

    return rows, columns


async def wait_for(ticks):
    for _ in range(ticks):
        await asyncio.sleep(0)


async def blink(canvas, row, column, symbol='*'):
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


def get_stars(canvas, amount=15, offset_row=1, offset_column=1):
    rows, columns = canvas.getmaxyx()
    symbols = ('+', '*', '.', ':')
    stars = [
        blink(
            canvas,
            randint(offset_row, rows - offset_row),
            randint(offset_column, columns - offset_column),
            choice(symbols)
        ) for _ in range(amount)
    ]

    return stars


def draw_frame(canvas, start_row, start_column, text, negative=False):
    rows_number, columns_number = canvas.getmaxyx()

    for row, line in enumerate(text.splitlines(), round(start_row)):
        if row < 0:
            continue
        elif row >= rows_number:
            break

        for column, symbol in enumerate(line, round(start_column)):
            if column < 0:
                continue
            if column >= columns_number:
                break
            if symbol == ' ':
                continue
            if row == rows_number - 1 and column == columns_number - 1:
                continue

            symbol = symbol if not negative else ' '
            canvas.addch(row, column, symbol)


def read_controls(canvas):
    SPACE_KEY_CODE = 32
    LEFT_KEY_CODE = 260
    RIGHT_KEY_CODE = 261
    UP_KEY_CODE = 259
    DOWN_KEY_CODE = 258

    rows_direction = columns_direction = 0
    space_pressed = False

    while True:
        pressed_key_code = canvas.getch()

        if pressed_key_code == -1:
            break
        elif pressed_key_code == UP_KEY_CODE:
            rows_direction = -1
        elif pressed_key_code == DOWN_KEY_CODE:
            rows_direction = 1
        elif pressed_key_code == RIGHT_KEY_CODE:
            columns_direction = 1
        elif pressed_key_code == LEFT_KEY_CODE:
            columns_direction = -1
        elif pressed_key_code == SPACE_KEY_CODE:
            space_pressed = True

    return rows_direction, columns_direction, space_pressed


async def fire(canvas, start_row, start_column, 
               rows_speed=-0.3, columns_speed=0):
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
        canvas.addstr(round(row), round(column), symbol)
        await asyncio.sleep(0)
        canvas.addstr(round(row), round(column), ' ')
        row += rows_speed
        column += columns_speed


async def get_ship(canvas, frames, speed=3, ship_row=15, ship_column=20):
    canvas_rows, canvas_columns = canvas.getmaxyx()
    frame_rows, frame_columns = get_frame_size(frames[0])
    frame_half = frame_columns // 2
    frames = cycle([frames[0], frames[0], frames[1], frames[1]])
    row_speed = column_speed = 0

    while True:
        delta_rows, delta_columns, space_pressed = read_controls(canvas)
        row_speed, column_speed = update_speed(
            row_speed, column_speed, delta_rows, delta_columns
        )
        ship_row += row_speed
        ship_column += column_speed

        if ship_row < 0:
            ship_row = 0
        elif ship_row + frame_rows > canvas_rows:
            ship_row = canvas_rows - frame_rows

        if ship_column < 0:
            ship_column = 0
        elif ship_column + frame_columns > canvas_columns:
            ship_column = canvas_columns - frame_columns

        if space_pressed:
            bullet_column = ship_column + frame_half
            bullet_r_speed = -speed - 0.8
            if column_speed > 0:
                bullet_c_speed = column_speed + 0.1
            elif column_speed == 0:
                bullet_c_speed = 0
            else:
                bullet_c_speed = column_speed - 0.1
            add_coroutines(
                fire(canvas, ship_row, bullet_column,
                     rows_speed=bullet_r_speed,
                     columns_speed=bullet_c_speed)
            )

        frame = next(frames)
        draw_frame(canvas, ship_row, ship_column, frame)
        await asyncio.sleep(0)
        draw_frame(canvas, ship_row, ship_column, frame, negative=True)
