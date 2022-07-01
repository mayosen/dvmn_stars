from curses import window

SPACE_KEY_CODE = 32
LEFT_KEY_CODE = 260
RIGHT_KEY_CODE = 261
UP_KEY_CODE = 259
DOWN_KEY_CODE = 258


def draw_frame(canvas: window, start_row, start_column, text: str, negative=False):
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


def read_controls(canvas: window):
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
