#
# This module handles the Raspbeery Pi overrise switches. The switches control relays driving the
# two aquarium lights and the CO2 injection.
# Each of the three switches ahs three states : off (up), auto (centre) and on (down)
# Each switch uses two GPIO pins, one indicating "off" state, and one "on" state.
# A LOW state on a GPIO pin indicates the switch is in the corresponding position (the pins are pulled HIGH)
#  Therefore, if both pins corresponding to a switch are HIGH, the the switch is in the AUTO position
#
#  sw1_UP GPIO 23 Light 1 OFF
#  sw1_DN GPIO 22 Light 1 ON
#  sw2_UP GPIO 0  Light 2 OFF
#  sw2_DN GPIO 1  Light 2 ON
#  sw3_UP GPIO 12 CO2     OFF
#  sw3_DN GPIO 20 CO2     ON
#
#   sw4 is the pushbutton switch used to prime the dosing pump. It is on GPIO 19
#
# TESTED OK 30/01/2020
#
# CHANGE LOG :
# 08/02/2020 : Cleaned up the switch logic (get_state) to make it easier to read and understand

import RPi.GPIO as GPIO
import time

class PushButton:
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)

    def __init__(self,gpio):
        self.gpio = gpio
        try:
            GPIO.setup(self.gpio, GPIO.IN, pull_up_dowwn = GPIO.PUD_UP)
        except Exception as error:
            print("[-]" + error)

    def get_state(self):
        self.pressed = None
        try:
            self.pressed = bool(GPIO.input(self.gpio))
        except Exception as error:
            print("[-]" + error)
        return(self.pressed)


class Switch:
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)

    def __init__(self,gpio_up, gpio_down):
        try:
            self.gpio_up = gpio_up
            self.gpio_down = gpio_down
            GPIO.setup(self.gpio_up, GPIO.IN, pull_up_down = GPIO.PUD_UP)
            GPIO.setup(self.gpio_down, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        except Exception as error:
            print("[-]" + error)

    def get_state(self):
        try :
            self.up = bool(GPIO.input(self.gpio_up))
            self.down = bool(GPIO.input(self.gpio_down))
            #print(self.up, self.down)

            if self.up & self.down:     # "AUTO"
                self.state = "AUTO"
            elif self.down:             # "ON"
                self.state = True
            elif self.up:               # "OFF"
                self.state = False
            else :
                self.state = None       # Something went wrong!!!
        except Exception as error:
            print(error)
            self.state = "N/A"
        return(self.state)


if __name__ == '__main__':
    try:
        # sw1 = Switch(23,22)
        # sw2 = Switch(0, 1)
        # sw3 = Switch(12,20)
        # while True:
        #     print(sw1.get_state(), sw2.get_state(), sw3.get_state())
        #     time.sleep(2)
        pushButton = PushButton(19)
        while True:
            print(pushButton.get_state())
            time.sleep(0.1)
    except KeyboardInterrupt:
        pass
