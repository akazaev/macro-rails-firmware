try:
    import RPi.GPIO as GPIO
except ImportError:
    import OPi.GPIO as GPIO
    GPIO.setboard(GPIO.ZERO)


from time import sleep


def take_shot(ir_pin):
    """
    Nikon's remote ir controller code
    2.0ms on
    27.8ms off
    0.5ms on
    1.5ms off
    0.5ms on
    3.5ms off
    0.5 ms on
    """
    GPIO.output(ir_pin, 0)

    codes = [
        (0.002, 1),
        (0.028, 0),
        (0.0004, 1),
        (0.00158, 0),
        (0.0004, 1),
        (0.00358, 0),
        (0.0004, 1),
    ]

    for code in codes:
        time, value = code
        GPIO.output(ir_pin, value)
        sleep(time)

    GPIO.output(ir_pin, 0)
