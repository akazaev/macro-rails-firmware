try:
    import RPi.GPIO as GPIO
except ImportError:
    import OPi.GPIO as GPIO
    GPIO.setboard(GPIO.ZERO)

from time import sleep

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BOARD)

control_pins = (31, 33, 35, 37)

ir_pin = 29
GPIO.setup(ir_pin, GPIO.OUT)

forward_pin = 38
backward_pin = 36
GPIO.setup(forward_pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(backward_pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

button_pin = 32
GPIO.setup(button_pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)


seq = [
    [1, 0, 0, 1],
    [1, 1, 0, 0],
    [0, 1, 1, 0],
    [0, 0, 1, 1],
]


def callback(pin):
    global step
    step = 0
    if GPIO.input(forward_pin):
        step = 1
    if GPIO.input(backward_pin):
        step = -1
    print abs_position


def button_callback(channel):
    global run
    if run:
        return
    run = True
    steps = 512

    rseq = list(reversed(seq))
    try:
        for i in range(steps):
            for halfstep in range(len(rseq)):
                for pin in range(4):
                    GPIO.output(control_pins[pin], rseq[halfstep][pin])
                sleep(0.003)
    except KeyboardInterrupt:
        pass
    except Exception as err:
        print err

    for pin in control_pins:
        GPIO.output(pin, 0)

    run = False


for pin in control_pins:
  GPIO.setup(pin, GPIO.OUT)
  GPIO.output(pin, 0)


GPIO.add_event_detect(forward_pin, GPIO.BOTH, callback=callback)
GPIO.add_event_detect(backward_pin, GPIO.BOTH, callback=callback)

GPIO.add_event_detect(button_pin, GPIO.RISING, callback=button_callback)

step = 0
abs_position = 0
position = 0
run = False

print abs_position

try:
    while True:
        if not step:
            run = False
            sleep(0.05)
        else:
            run = True
            for pin in range(4):
                GPIO.output(control_pins[pin], seq[position][pin])
            sleep(0.003)
            position += step
            abs_position += step
            if position < 0:
                position = 3
            if position > 3:
                position = 0
except KeyboardInterrupt:
    pass
except Exception as err:
    print err


for pin in control_pins:
    GPIO.output(pin, 0)
