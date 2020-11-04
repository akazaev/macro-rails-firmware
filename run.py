#!/usr/bin/env python3

import os
import sys

try:
    import RPi.GPIO as GPIO
except ImportError:
    import OPi.GPIO as GPIO
    GPIO.setboard(GPIO.ZERO)

from time import sleep, time

from libs.control import take_shot
from helpers import lcd_print, PinsEnum, SEQUENCE, SCREW_PITCH, calc_distance


GPIO.setwarnings(False)
GPIO.setmode(GPIO.BOARD)

GPIO.setup(PinsEnum.SHOT, GPIO.OUT)
GPIO.setup(PinsEnum.RESTART_BTN, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(PinsEnum.TEST_SHOT_BTN, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

GPIO.setup(PinsEnum.FORWARD_BTN, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(PinsEnum.RESET_BTN, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(PinsEnum.BACKWARD_BTN, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

GPIO.setup(PinsEnum.INC_BTN, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(PinsEnum.INC2_BTN, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(PinsEnum.START_BTN, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(PinsEnum.STOP_BTN, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(PinsEnum.BACK_BTN, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(PinsEnum.DEC_BTN, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(PinsEnum.DEC2_BTN, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

for pin in PinsEnum.DRIVER:
    GPIO.setup(pin, GPIO.OUT)
    GPIO.output(pin, 0)


def manual_callback(pin):
    global DIRECTION
    DIRECTION = 0
    if GPIO.input(PinsEnum.FORWARD_BTN):
        DIRECTION = 1
    if GPIO.input(PinsEnum.BACKWARD_BTN):
        DIRECTION = -1


def reset_callback(pin):
    global ABS_POSITION, STEP, SHOTS
    ABS_POSITION = SHOTS = 0
    STEP = 0.1


def restart_callback(pin):
    lcd_print('Restart...', '')
    os.execl(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                          'run.py'), *sys.argv)


def step_callback(pin):
    global STEP, MIN_STEP, MIN2_STEP
    if GPIO.input(PinsEnum.INC_BTN):
        STEP += MIN_STEP
    if GPIO.input(PinsEnum.DEC_BTN):
        STEP = max(MIN_STEP, STEP - MIN_STEP)
    if GPIO.input(PinsEnum.INC2_BTN):
        STEP += MIN2_STEP
    if GPIO.input(PinsEnum.DEC2_BTN):
        STEP = max(MIN2_STEP, STEP - MIN2_STEP)


def shot_callback(pin):
    take_shot(PinsEnum.SHOT)


def start_callback(pin):
    global ABS_POSITION, PROGRESS, SHOTS
    if not PROGRESS:
        PROGRESS = True
        ABS_POSITION = SHOTS = 0
        lcd_print('Start...', '')
        sleep(4)
        run()


def back_callback(pin):
    global PROGRESS

    if not PROGRESS:
        PROGRESS = True
        lcd_print('Back...', '')
        sleep(1)
        back()


def back():
    global ABS_POSITION, POSITION, PROGRESS

    while True:
        for pin in range(4):
            GPIO.output(PinsEnum.DRIVER[pin], SEQUENCE[POSITION][pin])
        sleep(0.003)
        POSITION -= 1
        ABS_POSITION -= 1

        if not ABS_POSITION:
            lcd_print('Home', '')
            sleep(2)
            PROGRESS = False
            break

        if GPIO.input(PinsEnum.STOP_BTN):
            lcd_print('Stop...', '')
            sleep(2)
            PROGRESS = False
            break

        if POSITION < 0:
            POSITION = len(SEQUENCE) - 1
        if POSITION > len(SEQUENCE) - 1:
            POSITION = 0


def run():
    global POSITION, ABS_POSITION, PROGRESS, SHOTS
    direction = 1

    run_template1 = '=>Step={}mm'
    run_template2 = '=>D={},S={}'

    take_shot(PinsEnum.SHOT)
    sleep(3)
    SHOTS = 1

    lcd_print(run_template1.format(round(STEP, 3)),
              run_template2.format(calc_distance(ABS_POSITION), SHOTS))

    try:
        while PROGRESS:
            for i in range(round(512 * 8 * STEP / SCREW_PITCH)):
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
            lcd_print(run_template1.format(round(STEP, 3)),
                      run_template2.format(distance, SHOTS + 1))

            if GPIO.input(PinsEnum.STOP_BTN):
                lcd_print('Stop...', '')
                sleep(4)
                PROGRESS = False
                SHOTS = 0
                break

            sleep(2)
            take_shot(PinsEnum.SHOT)
            sleep(1)
            SHOTS += 1
    except KeyboardInterrupt:
        pass
    except Exception as err:
        print(err)


GPIO.add_event_detect(PinsEnum.FORWARD_BTN, GPIO.BOTH,
                      callback=manual_callback)
GPIO.add_event_detect(PinsEnum.BACKWARD_BTN, GPIO.BOTH,
                      callback=manual_callback)
GPIO.add_event_detect(PinsEnum.RESET_BTN, GPIO.RISING,
                      callback=reset_callback, bouncetime=400)

GPIO.add_event_detect(PinsEnum.RESTART_BTN, GPIO.RISING,
                      callback=restart_callback, bouncetime=400)

GPIO.add_event_detect(PinsEnum.TEST_SHOT_BTN, GPIO.RISING,
                      callback=shot_callback, bouncetime=400)

GPIO.add_event_detect(PinsEnum.INC_BTN, GPIO.RISING,
                      callback=step_callback, bouncetime=400)
GPIO.add_event_detect(PinsEnum.INC2_BTN, GPIO.RISING,
                      callback=step_callback, bouncetime=400)
GPIO.add_event_detect(PinsEnum.DEC_BTN, GPIO.RISING,
                      callback=step_callback, bouncetime=400)
GPIO.add_event_detect(PinsEnum.DEC2_BTN, GPIO.RISING,
                      callback=step_callback, bouncetime=400)

GPIO.add_event_detect(PinsEnum.START_BTN, GPIO.RISING,
                      callback=start_callback, bouncetime=1000)
GPIO.add_event_detect(PinsEnum.BACK_BTN, GPIO.RISING,
                      callback=back_callback, bouncetime=1000)


DIRECTION = 0
ABS_POSITION = POSITION = SHOTS = 0
STEP = 0.1
MIN_STEP = 0.01
MIN2_STEP = 0.001
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

            if GPIO.input(PinsEnum.INC_BTN):
                if btn_pressed:
                    if time() - btn_pressed > 1:
                        STEP += MIN_STEP
                else:
                    btn_pressed = time()
            elif GPIO.input(PinsEnum.DEC_BTN):
                if btn_pressed:
                    if time() - btn_pressed > 1:
                        STEP = max(MIN_STEP, STEP - MIN_STEP)
                else:
                    btn_pressed = time()
            elif GPIO.input(PinsEnum.INC2_BTN):
                if btn_pressed:
                    if time() - btn_pressed > 1:
                        STEP += MIN2_STEP
                else:
                    btn_pressed = time()
            elif GPIO.input(PinsEnum.DEC2_BTN):
                if btn_pressed:
                    if time() - btn_pressed > 1:
                        STEP = max(MIN2_STEP, STEP - MIN2_STEP)
                else:
                    btn_pressed = time()
            else:
                btn_pressed = None

            distance = calc_distance(ABS_POSITION)
            lcd_print('Step={}mm'.format(round(STEP, 3)),
                      'D={},T={}'.format(distance, ABS_POSITION))
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
