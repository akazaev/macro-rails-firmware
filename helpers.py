from libs.lcd import LCD


SCREW_PITCH = 1.25


class PinsEnum:
    DRIVER = (31, 33, 35, 37)
    SHOT = 21
    TEST_SHOT_BTN = 19
    FORWARD_BTN = 36
    RESET_BTN = 15
    BACKWARD_BTN = 38
    RESTART_BTN = 29
    INC_BTN = 22
    INC2_BTN = 16
    START_BTN = 24
    STOP_BTN = 32
    BACK_BTN = 13
    DEC_BTN = 26
    DEC2_BTN = 18


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
    if len(row1) > 16:
        row1 = row1[:15] + '_'
    if len(row2) > 16:
        row2 = row2[:15] + '_'
    try:
        _lcd.lcd_clear()
        _lcd.lcd_display_string(row1 + (16 - len(row1))*' ', 1)
        _lcd.lcd_display_string(row2 + (16 - len(row2))*' ', 2)
    except Exception as err:
        print(err)


def calc_distance(position):
    return round(SCREW_PITCH * (position / (8 * 512)), 2)
