try:
    import RPi.GPIO as GPIO
except ImportError:
    import OPi.GPIO as GPIO
    GPIO.setboard(GPIO.ZERO)

from time import sleep

GPIO.setmode(GPIO.BOARD)


control_pins = (31, 33, 35, 37)

for pin in control_pins:
  GPIO.setup(pin, GPIO.OUT)
  GPIO.output(pin, 0)

halfstep_seq = [
    [1, 0, 0, 1],
    [1, 1, 0, 0],
    [0, 1, 1, 0],
    [0, 0, 1, 1],
]

back = True
if not back:
    halfstep_seq = list(reversed(halfstep_seq))


# do full loop
try:
    for i in range(512):
        for halfstep in range(len(halfstep_seq)):
            for pin in range(4):
                GPIO.output(control_pins[pin], halfstep_seq[halfstep][pin])
            sleep(0.002)
except KeyboardInterrupt:
    pass
except Exception as err:
    print err


for pin in control_pins:
    GPIO.output(pin, 0)
