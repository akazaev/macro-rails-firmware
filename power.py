#!/usr/bin/env python3

try:
    import RPi.GPIO as GPIO
except ImportError:
    import OPi.GPIO as GPIO
    GPIO.setboard(GPIO.ZERO)

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BOARD)

pin = 40
GPIO.setup(pin, GPIO.OUT)
GPIO.output(pin, 1)
