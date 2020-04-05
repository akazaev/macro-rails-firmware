from libs.lcd import LCD

_lcd = None


def lcd_print(row1, row2):
    global _lcd
    if not _lcd:
        _lcd = LCD(port=1)
    row1 = str(row1)
    row2 = str(row2)
    _lcd.lcd_display_string(row1 + (16 - len(row1))*' ', 1)
    _lcd.lcd_display_string(row2 + (16 - len(row2))*' ', 2)
