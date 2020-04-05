#!/usr/bin/env python3

import os
import sys

try:
    import RPi.GPIO as GPIO
except ImportError:
    import OPi.GPIO as GPIO
    GPIO.setboard(GPIO.ZERO)

from time import sleep, time

from helpers import lcd_print

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BOARD)


class PinsEnum:
    DRIVER = (31, 33, 35, 37)
    IR = 29

    FORWARD_BTN = 36
    RESET_BTN = 32
    BACKWARD_BTN = 38

    RESTART_BTN = 29

    A_BTN = 22
    B_BTN = 24
    C_BTN = 26


GPIO.setup(PinsEnum.IR, GPIO.OUT)

GPIO.setup(PinsEnum.FORWARD_BTN, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(PinsEnum.RESET_BTN, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(PinsEnum.BACKWARD_BTN, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(PinsEnum.RESTART_BTN, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(PinsEnum.A_BTN, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(PinsEnum.B_BTN, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(PinsEnum.C_BTN, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)


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


def manual_callback(pin):
    global DIRECTION
    DIRECTION = 0
    if GPIO.input(PinsEnum.FORWARD_BTN):
        DIRECTION = 1
    if GPIO.input(PinsEnum.BACKWARD_BTN):
        DIRECTION = -1


def reset_callback(pin):
    global ABS_POSITION, STEP
    ABS_POSITION = 0
    STEP = 0.1


def restart_callback(pin):
    os.execl('./run.py', *sys.argv)


def step_callback(pin):
    global STEP
    if GPIO.input(PinsEnum.A_BTN):
        STEP += 0.05
    if GPIO.input(PinsEnum.C_BTN):
        STEP -= 0.05


def run():
    global POSITION, ABS_POSITION, PROGRESS
    direction = 1
    try:
        while PROGRESS:
            for i in range(int(512*8*STEP/1.25)):
                for pin in range(4):
                    GPIO.output(PinsEnum.DRIVER[pin], SEQUENCE[POSITION][pin])
                sleep(0.003)
                POSITION += direction
                ABS_POSITION += direction
                if POSITION < 0:
                    POSITION = len(SEQUENCE) - 1
                if POSITION > len(SEQUENCE) - 1:
                    POSITION = 0

            distance = round(1.25 * (ABS_POSITION / (8 * 512)), 2)
            distance = '>D={}'.format(distance)
            step = '>S={}'.format(round(STEP, 2))
            lcd_print(step, distance)

            if GPIO.input(PinsEnum.RESET_BTN):
                lcd_print('Stop...', '')
                sleep(4)
                PROGRESS = False
    except KeyboardInterrupt:
        pass
    except Exception as err:
        print(err)


def start_callback(pin):
    global ABS_POSITION, PROGRESS, STOPPING
    if not PROGRESS:
        PROGRESS = True
        ABS_POSITION = 0
        lcd_print('Start...', '')
        sleep(4)
        run()


for pin in PinsEnum.DRIVER:
  GPIO.setup(pin, GPIO.OUT)
  GPIO.output(pin, 0)


GPIO.add_event_detect(PinsEnum.FORWARD_BTN, GPIO.BOTH,
                      callback=manual_callback)
GPIO.add_event_detect(PinsEnum.BACKWARD_BTN, GPIO.BOTH,
                      callback=manual_callback)
GPIO.add_event_detect(PinsEnum.RESET_BTN, GPIO.RISING,
                      callback=reset_callback,
                      bouncetime=400)

GPIO.add_event_detect(PinsEnum.RESTART_BTN, GPIO.RISING,
                      callback=restart_callback,
                      bouncetime=400)

GPIO.add_event_detect(PinsEnum.A_BTN, GPIO.RISING,
                      callback=step_callback, bouncetime=400)
GPIO.add_event_detect(PinsEnum.B_BTN, GPIO.RISING,
                      callback=start_callback, bouncetime=400)
GPIO.add_event_detect(PinsEnum.C_BTN, GPIO.RISING,
                      callback=step_callback, bouncetime=400)

DIRECTION = 0
ABS_POSITION = 0
POSITION = 0
STEP = 0.1
PROGRESS = False

btn_pressed = None

lcd_print('Ready...', '')
sleep(2)

try:
    while True:
        if not DIRECTION:
            sleep(0.2)
            if PROGRESS:
                continue

            for pin in range(4):
                GPIO.output(PinsEnum.DRIVER[pin], 0)

            if GPIO.input(PinsEnum.A_BTN):
                if btn_pressed:
                    if time() - btn_pressed > 1:
                        STEP += 0.05
                else:
                    btn_pressed = time()
            elif GPIO.input(PinsEnum.C_BTN):
                if btn_pressed:
                    if time() - btn_pressed > 1:
                        STEP -= 0.05
                else:
                    btn_pressed = time()
            else:
                btn_pressed = None

            distance = round(1.25 * (ABS_POSITION / (8 * 512)), 2)
            distance = 'D={}'.format(distance)
            step = 'S={}'.format(round(STEP, 2))
            lcd_print(step, distance)
        else:
            for pin in range(4):
                GPIO.output(PinsEnum.DRIVER[pin], SEQUENCE[POSITION][pin])
            sleep(0.003)
            POSITION += DIRECTION
            ABS_POSITION += DIRECTION
            if POSITION < 0:
                POSITION = len(SEQUENCE) - 1
            if POSITION > len(SEQUENCE) - 1:
                POSITION = 0
except KeyboardInterrupt:
    pass
except Exception as err:
    print(err)


for pin in PinsEnum.DRIVER:
    GPIO.output(pin, 0)
