from libs.lcd import LCD


class PinsEnum:
    DRIVER = (31, 33, 35, 37)
    IR = 21
    SHOT = 19
    FORWARD_BTN = 36
    RESET_BTN = 32
    BACKWARD_BTN = 38
    RESTART_BTN = 29
    A_BTN = 22
    B_BTN = 24
    C_BTN = 26


SEQUENCE = [
    [1, 0, 0, 0],
    [1, 1, 0, 0],
    [0, 1, 0, 0],
    [0, 1, 1, 0],
    [0, 0, 1, 0],
    [0, 0, 1, 1],
    [0, 0, 0, 1],
    [1, 0, 0, 1],
]


_lcd = None


def lcd_print(row1, row2):
    global _lcd
    if not _lcd:
        try:
            _lcd = LCD(port=1)
        except Exception as err:
            print(err)
    row1 = str(row1)
    row2 = str(row2)
    try:
        _lcd.lcd_display_string(row1 + (16 - len(row1))*' ', 1)
        _lcd.lcd_display_string(row2 + (16 - len(row2))*' ', 2)
    except Exception as err:
        print(err)
