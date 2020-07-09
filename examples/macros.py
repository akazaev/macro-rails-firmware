try:
    import RPi.GPIO as GPIO
except ImportError:
    import OPi.GPIO as GPIO
    GPIO.setboard(GPIO.ZERO)

from time import sleep

from libs.control import take_shot


GPIO.setwarnings(False)
GPIO.setmode(GPIO.BOARD)

control_pins = (31, 33, 35, 37)
for pin in control_pins:
  GPIO.setup(pin, GPIO.OUT)
  GPIO.output(pin, 0)


ir_pin = 29
GPIO.setup(ir_pin, GPIO.OUT)


seq = [
    [1, 0, 0, 1],
    [1, 1, 0, 0],
    [0, 1, 1, 0],
    [0, 0, 1, 1],
]

abs_position = 0
finish_position = 512*4
position = 0
step = 41  # 39-40

print(abs_position)

try:
    while abs_position < finish_position:
        for i in range(step):
            for halfstep in range(len(seq)):
                for pin in range(4):
                    GPIO.output(control_pins[pin], seq[halfstep][pin])
                sleep(0.004)
                position += -1
                abs_position += 1
                if position < 0:
                    position = 3
                if position > 3:
                    position = 0
        print(abs_position)
        sleep(2)
        take_shot(ir_pin)
        sleep(0.063)
        take_shot(ir_pin)  # double command to ensure command was received
        sleep(1)
except KeyboardInterrupt:
    pass
except Exception as err:
    print(err)


for pin in control_pins:
    GPIO.output(pin, 0)
