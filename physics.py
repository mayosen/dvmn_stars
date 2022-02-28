import math


def _limit(value, min_value, max_value):
    """Limit value by min_value and max_value."""

    if value < min_value:
        return min_value
    if value > max_value:
        return max_value
    else:
        return value


def _apply_acceleration(speed, speed_limit, forward=True):
    """Change speed — accelerate or brake — according to force direction."""

    speed_limit = abs(speed_limit)

    speed_fraction = speed / speed_limit

    # Если корабль стоит на месте, дергаем резко
    # Если корабль уже летит быстро, прибавляем медленно
    delta = math.cos(speed_fraction) * 0.75

    if forward:
        result_speed = speed + delta
    else:
        result_speed = speed - delta

    result_speed = _limit(result_speed, -speed_limit, speed_limit)

    # Если скорость близка к нулю, то останавливаем корабль
    if abs(result_speed) < 0.1:
        result_speed = 0

    return result_speed


def update_speed(row_speed, column_speed,
                 rows_direction, columns_direction,
                 row_speed_limit=2, column_speed_limit=2,
                 fading=0.8):
    """Update speed smoothly to make control handy for player.
    Return new speed value (row_speed, column_speed)
    """

    if fading < 0 or fading > 1:
        raise ValueError(f'Wrong columns_direction value {fading}. '
                         f'Expects float between 0 and 1.')

    # Гасим скорость, чтобы корабль останавливался со временем
    row_speed *= fading
    column_speed *= fading

    row_speed_limit, column_speed_limit = \
        abs(row_speed_limit), abs(column_speed_limit)

    if rows_direction != 0:
        row_speed = _apply_acceleration(row_speed, row_speed_limit,
                                        rows_direction > 0)

    if columns_direction != 0:
        column_speed = _apply_acceleration(column_speed, column_speed_limit,
                                           columns_direction > 0)

    return row_speed, column_speed
