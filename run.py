#!/usr/bin/env python3

import os
import sys

try:
    import RPi.GPIO as GPIO
except ImportError:
    import OPi.GPIO as GPIO
    GPIO.setboard(GPIO.ZERO)

from time import sleep, time

from libs.ir import take_shot
from helpers import lcd_print, PinsEnum, SEQUENCE

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BOARD)


GPIO.setup(PinsEnum.IR, GPIO.OUT)
GPIO.setup(PinsEnum.FORWARD_BTN, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(PinsEnum.RESET_BTN, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(PinsEnum.BACKWARD_BTN, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(PinsEnum.RESTART_BTN, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(PinsEnum.SHOT, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(PinsEnum.A_BTN, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(PinsEnum.B_BTN, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(PinsEnum.C_BTN, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)


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
    lcd_print('Restart...', '')
    os.execl(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                          'run.py'), *sys.argv)


def step_callback(pin):
    global STEP
    if GPIO.input(PinsEnum.A_BTN):
        STEP += 0.01
    if GPIO.input(PinsEnum.C_BTN):
        STEP = max(0.01, STEP - 0.01)


def shot_callback(pin):
    take_shot(PinsEnum.IR)


def calc_distance(position):
    return round(1.25 * (position / (8 * 512)), 2)


def run():
    global POSITION, ABS_POSITION, PROGRESS
    direction = 1

    distance = calc_distance(ABS_POSITION)
    distance = '=>D={}'.format(distance)
    step = 'Step={}mm'.format(round(STEP, 2))
    lcd_print(step, distance)

    try:
        while PROGRESS:
            for i in range(round(512 * 8 * STEP / 1.25)):
                for pin in range(4):
                    GPIO.output(PinsEnum.DRIVER[pin], SEQUENCE[POSITION][pin])
                sleep(0.003)
                POSITION += direction
                ABS_POSITION += direction
                if POSITION < 0:
                    POSITION = len(SEQUENCE) - 1
                if POSITION > len(SEQUENCE) - 1:
                    POSITION = 0

            for pin in range(4):
                GPIO.output(PinsEnum.DRIVER[pin], 0)

            distance = calc_distance(ABS_POSITION)
            distance = '=>D={}'.format(distance)
            step = 'Step={}mm'.format(round(STEP, 2))
            lcd_print(step, distance)

            if GPIO.input(PinsEnum.RESET_BTN):
                lcd_print('Stop...', '')
                sleep(4)
                PROGRESS = False
                break

            sleep(2)
            take_shot(PinsEnum.IR)
            sleep(0.0632)
            take_shot(PinsEnum.IR)  # double command to ensure it was received
            sleep(1)
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

GPIO.add_event_detect(PinsEnum.SHOT, GPIO.RISING,
                      callback=shot_callback,
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
                        STEP += 0.01
                else:
                    btn_pressed = time()
            elif GPIO.input(PinsEnum.C_BTN):
                if btn_pressed:
                    if time() - btn_pressed > 1:
                        STEP = max(0.01, STEP - 0.01)
                else:
                    btn_pressed = time()
            else:
                btn_pressed = None

            distance = calc_distance(ABS_POSITION)
            distance = 'D={},T={}'.format(distance, ABS_POSITION)
            step = 'Step={}mm'.format(round(STEP, 2))
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
