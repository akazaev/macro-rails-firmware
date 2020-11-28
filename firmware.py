import os
import sys
import time

import RPi.GPIO as GPIO

from libs.control import take_shot
from libs.lcd import LCD


GPIO.setwarnings(False)
GPIO.setmode(GPIO.BOARD)


class PinsEnum:
    DRIVER = (31, 33, 35, 37)
    RESTART_BTN = 29
    POWER = 40

    FORWARD_BTN = 36
    BACKWARD_BTN = 38
    RESET_BTN = 15

    SHOT = 21
    TEST_SHOT_BTN = 19

    START_BTN = 24
    STOP_BTN = 32
    BACK_BTN = 13

    INC_BTN = 22
    INC2_BTN = 16
    DEC_BTN = 26
    DEC2_BTN = 18

    IN_PINS = (RESTART_BTN,
               TEST_SHOT_BTN,
               FORWARD_BTN,
               RESET_BTN,
               BACKWARD_BTN,
               INC_BTN,
               INC2_BTN,
               START_BTN,
               STOP_BTN,
               BACK_BTN,
               DEC_BTN,
               DEC2_BTN, )
    OUT_PINS = (SHOT, POWER, ) + DRIVER


DRIVER_SEQUENCE = [
    [1, 0, 0, 0],
    [1, 1, 0, 0],
    [0, 1, 0, 0],
    [0, 1, 1, 0],
    [0, 0, 1, 0],
    [0, 0, 1, 1],
    [0, 0, 0, 1],
    [1, 0, 0, 1],
]


class Process:
    BOUNCE_TIME = 400
    MIN_STEP = 0.01
    MIN2_STEP = 0.001
    SCREW_PITCH = 1.25

    direction = abs_position = position = shots = 0
    step = 0.1
    lcd = None
    progress = False
    btn_pressed = None

    def __init__(self):
        self._setup_pins()
        self._setup_callbacks()
        self._power()
        self.lcd_print('Ready...')
        time.sleep(2)

    def calc_distance(self, position):
        return round(self.SCREW_PITCH * (position / (8 * 512)), 2)

    def lcd_print(self, row1, row2=''):
        if not self.lcd:
            try:
                self.lcd = LCD(port=1)
            except Exception as err:
                print(err)

        row1 = str(row1)
        row2 = str(row2)
        if len(row1) > 16:
            row1 = row1[:15] + '_'
        if len(row2) > 16:
            row2 = row2[:15] + '_'

        try:
            self.lcd.lcd_clear()
            self.lcd.lcd_display_string(row1 + (16 - len(row1)) * ' ', 1)
            self.lcd.lcd_display_string(row2 + (16 - len(row2)) * ' ', 2)
        except Exception as err:
            print(err)

    def _setup_pins(self):
        for pin in PinsEnum.IN_PINS:
            GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

        for pin in PinsEnum.OUT_PINS:
            GPIO.setup(pin, GPIO.OUT)
            GPIO.output(pin, 0)

    def _add_event_detect(self, pin, callback, edge=GPIO.RISING):
        GPIO.add_event_detect(pin, edge, callback=callback)

    def _setup_callbacks(self):
        self._add_event_detect(PinsEnum.FORWARD_BTN, self.manual_callback,
                               edge=GPIO.BOTH)
        self._add_event_detect(PinsEnum.BACKWARD_BTN, self.manual_callback,
                               edge=GPIO.BOTH)
        self._add_event_detect(PinsEnum.RESET_BTN, self.reset_callback)
        self._add_event_detect(PinsEnum.RESTART_BTN, self.restart_callback)
        self._add_event_detect(PinsEnum.TEST_SHOT_BTN, self.shot_callback)

        self._add_event_detect(PinsEnum.INC_BTN, self.step_callback)
        self._add_event_detect(PinsEnum.INC2_BTN, self.step_callback)
        self._add_event_detect(PinsEnum.DEC_BTN, self.step_callback)
        self._add_event_detect(PinsEnum.DEC2_BTN, self.step_callback)

        self._add_event_detect(PinsEnum.START_BTN, self.start_callback)
        self._add_event_detect(PinsEnum.BACK_BTN, self.back_callback)

    def _power(self):
        GPIO.output(PinsEnum.POWER, 1)

    def manual_callback(self, pin):
        self.direction = 0
        if GPIO.input(PinsEnum.FORWARD_BTN):
            self.direction = 1
        if GPIO.input(PinsEnum.BACKWARD_BTN):
            self.direction = -1

    def reset_callback(self, pin):
        self.abs_position = self.shots = 0
        self.step = 0.1

    def restart_callback(self, pin):
        self.lcd_print('Restart...')
        os.execl(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                              'run.py'), *sys.argv)

    def step_callback(self, pin):
        if GPIO.input(PinsEnum.INC_BTN):
            self.step += self.MIN_STEP
        if GPIO.input(PinsEnum.DEC_BTN):
            self.step = max(self.MIN_STEP, self.step - self.MIN_STEP)
        if GPIO.input(PinsEnum.INC2_BTN):
            self.step += self.MIN2_STEP
        if GPIO.input(PinsEnum.DEC2_BTN):
            self.step = max(self.MIN2_STEP, self.step - self.MIN2_STEP)

    def shot_callback(self, pin):
        take_shot(PinsEnum.SHOT)

    def start_callback(self, pin):
        if not self.progress:
            self.progress = True
            self.abs_position = self.shots = 0
            self.lcd_print('Start...')
            time.sleep(4)
            self.run()

    def back_callback(self, pin):
        if not self.progress:
            self.progress = True
            self.lcd_print('Back...')
            time.sleep(1)
            self.back()

    def back(self):
        """ Mode camera back to home """
        while True:
            if not self.abs_position:
                self.lcd_print('Home...')
                time.sleep(2)
                self.progress = False
                break

            for pin in range(4):
                GPIO.output(PinsEnum.DRIVER[pin],
                            DRIVER_SEQUENCE[self.position][pin])
            time.sleep(0.003)
            self.position += -1 if self.abs_position > 0 else 1
            self.abs_position += -1 if self.abs_position > 0 else 1

            if self.position < 0:
                self.position = len(DRIVER_SEQUENCE) - 1
            if self.position > len(DRIVER_SEQUENCE) - 1:
                self.position = 0

            if GPIO.input(PinsEnum.STOP_BTN):
                self.lcd_print('Stop...')
                time.sleep(2)
                self.progress = False
                break

    def run(self):
        """ Start macro stack process """
        run_template1 = '=>Step={}mm'
        run_template2 = '=>D={},S={}'

        take_shot(PinsEnum.SHOT)
        time.sleep(3)
        self.shots = 1

        self.lcd_print(
            run_template1.format(round(self.step, 3)),
            run_template2.format(self.calc_distance(self.abs_position),
                                 self.shots))
        try:
            while self.progress:
                for i in range(round(512 * 8 * self.step / self.SCREW_PITCH)):
                    for pin in range(4):
                        GPIO.output(PinsEnum.DRIVER[pin],
                                    DRIVER_SEQUENCE[self.position][pin])
                    time.sleep(0.003)
                    self.position += 1
                    self.abs_position += 1
                    if self.position < 0:
                        self.position = len(DRIVER_SEQUENCE) - 1
                    if self.position > len(DRIVER_SEQUENCE) - 1:
                        self.position = 0

                for pin in range(4):
                    GPIO.output(PinsEnum.DRIVER[pin], 0)

                distance = self.calc_distance(self.abs_position)
                self.lcd_print(
                    run_template1.format(round(self.step, 3)),
                    run_template2.format(distance, self.shots + 1))

                if GPIO.input(PinsEnum.STOP_BTN):
                    self.lcd_print('Stop...')
                    time.sleep(4)
                    self.progress = False
                    self.shots = 0
                    break

                time.sleep(2)
                take_shot(PinsEnum.SHOT)
                time.sleep(1)
                self.shots += 1
        except KeyboardInterrupt:
            pass
        except Exception as err:
            print(err)

    def start(self):
        """ Start main process loop """
        try:
            while True:
                if not self.direction:
                    time.sleep(0.2)
                    if self.progress:
                        continue

                    for pin in range(4):
                        GPIO.output(PinsEnum.DRIVER[pin], 0)

                    inc_btn = GPIO.input(PinsEnum.INC_BTN)
                    dec_btn = GPIO.input(PinsEnum.DEC_BTN)
                    inc2_btn = GPIO.input(PinsEnum.INC2_BTN)
                    dec2_btn = GPIO.input(PinsEnum.DEC2_BTN)

                    if self.btn_pressed:
                        if time.time() - self.btn_pressed > 1:
                            if inc_btn:
                                self.step += self.MIN_STEP
                            if dec_btn:
                                self.step = max(self.MIN_STEP,
                                                self.step - self.MIN_STEP)
                            if inc2_btn:
                                self.step += self.MIN2_STEP
                            if dec2_btn:
                                self.step = max(self.MIN2_STEP,
                                                self.step - self.MIN2_STEP)
                    else:
                        if inc_btn or inc2_btn or dec_btn or dec2_btn:
                            self.btn_pressed = time.time()
                        else:
                            self.btn_pressed = None

                    distance = self.calc_distance(self.abs_position)
                    self.lcd_print(
                        'Step={}mm'.format(round(self.step, 3)),
                        'D={},T={}'.format(distance, self.abs_position))
                else:
                    for pin in range(4):
                        GPIO.output(PinsEnum.DRIVER[pin],
                                    DRIVER_SEQUENCE[self.position][pin])
                    time.sleep(0.003)
                    self.position += self.direction
                    self.abs_position += self.direction
                    if self.position < 0:
                        self.position = len(DRIVER_SEQUENCE) - 1
                    if self.position > len(DRIVER_SEQUENCE) - 1:
                        self.position = 0
        except KeyboardInterrupt:
            pass
        except Exception as err:
            print(err)

        for pin in PinsEnum.DRIVER:
            GPIO.output(pin, 0)
