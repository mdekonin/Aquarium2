#
# This module handles the Raspbeery Pi relays. The relays control two aquarium lights, one simulating
# dawn/dusk, the other full daylight. A third relay controls the CO2 injection.
# Each of the three relays has an ON time and an OFF time which are defined in constants but can be over-ridden
# via the admin console
#
import RPi.GPIO as GPIO
import time

class Relay:
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)

    def __init__(self, gpio):
        self.gpio = gpio
        GPIO.setup(self.gpio, GPIO.OUT)
        self.ontime = "00:00"
        self.offtime = "00:01"

    def on(self):
        GPIO.output(self.gpio,GPIO.HIGH)

    def off(self):
        GPIO.output(self.gpio, GPIO.LOW)


if __name__ == '__main__':
    light1 = Relay(26)
    while True:
        try:
            light1.on()
            time.sleep(2)
            light1.off()

        except KeyboardInterrupt:
            pass


        time.sleep(1)

