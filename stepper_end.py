try:
    import RPi.GPIO as GPIO
except ImportError:
    import OPi.GPIO as GPIO
    GPIO.setboard(GPIO.ZERO)

from time import sleep
import Adafruit_ADS1x15

adc = Adafruit_ADS1x15.ADS1115(address=0x48, busnum=3)
GPIO.setmode(GPIO.BOARD)
GAIN = 2
control_pins = (31, 33, 35, 37)

halfstep_seq = [
    [1, 0, 0, 1],
    [1, 1, 0, 0],
    [0, 1, 1, 0],
    [0, 0, 1, 1],
]

for pin in control_pins:
    GPIO.setup(pin, GPIO.OUT)
    GPIO.output(pin, 0)

halfstep_seq = list(reversed(halfstep_seq))
stop = False

value = 0
try:
    while True:
        print value
        for i in range(512):
            for halfstep in range(len(halfstep_seq)):
                for pin in range(4):
                    GPIO.output(control_pins[pin], halfstep_seq[halfstep][pin])
                sleep(0.002)
            value = adc.read_adc(0, gain=GAIN)
            if value >= 24500:
                stop = True
                break
        if stop:
            break
except KeyboardInterrupt:
    pass
except Exception as err:
    print err


for pin in control_pins:
    GPIO.output(pin, 0)
