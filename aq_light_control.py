#
# Ths module controls the lights and CO2 injection based on pre-defined ON/OFF times GPIO Pins :
#   Light1        - 26
#   Light2        - 21
#   CO2           - 13
#   Dosing Pump   - 27

# TESTED OK 2/2/2020
#
# 02/03/2020    add support for relay #4 on gpio 26 to control 12V DC motor for fertiliser dosing pump

import time
import aq_relays as relays
import aq_switches as switches
from aq_timeUtils import hhmm2min as hhmm2min
import aq_global as g

def light_control():
    # Instantiate the light and CO2 objects and associate with the appropriate GPIO pins
    # Then set the on times and off times
    light1 = relays.Relay(26)
    g.light1ontime = "06:40"
    g.light1offtime = "21:00"

    light2 = relays.Relay(21)
    g.light2ontime = "10:00"
    g.light2offtime = "17:00"

    CO2 = relays.Relay(13)
    g.CO2ontime = "08:00"
    g.CO2offtime = "16:00"

    # Instantiate the fertiliser dosing pump
    pump = relays.Relay(27)

    # Instantiate the switch obects and associate them with two GPIO pins each, One for "off", one for "on"
    sw1 = switches.Switch(23, 22)
    sw2 = switches.Switch(0, 1)
    sw3 = switches.Switch(12, 20)


    light2.on()
    time.sleep(2)
    light2.off()
    time.sleep(2)
    light2.on()


    dose_today = False
    dosing = False

    while True:
        
        localtime = time.localtime(time.time())
        current_mins = localtime.tm_hour * 60 + localtime.tm_min
        # ===============================================================
        # Light1 - Low level LED simulating dawn/dusk
        # ===============================================================
        g.sw1state = sw1.get_state()
        if g.sw1state == "AUTO":  # light 1 over-ride set to "AUTO"
            if hhmm2min(g.light1ontime) <= current_mins < hhmm2min(g.light1offtime):
                light1.on()
            else:
                light1.off()
        elif g.sw1state:  # light 1 over-ride set to "ON"
            light1.on()
        elif not g.sw1state:  # light 1 over-ride set to "OFF"
            light1.off()

        # ===============================================================
        # light2 - Daylight level
        # ===============================================================
        g.sw2state = sw2.get_state()
        if g.sw2state == "AUTO":  # light 2 over-ride set to "AUTO"
            if hhmm2min(g.light2ontime) <= current_mins < hhmm2min(g.light2offtime):
                light2.on()
            else:
                light2.off()
        elif g.sw2state:  # light 2 over-ride set to "ON"
            light2.on()
        elif not g.sw2state:  # light 2 over-ride set to "OFF"
            light2.off()


        # ===============================================================
        # CO2 Injection
        # ===============================================================
        g.sw3state = sw3.get_state()
        if g.sw3state == "AUTO":  # CO2 over-ride set to "AUTO"
            if hhmm2min(g.CO2ontime) <= current_mins < hhmm2min(g.CO2offtime):
                CO2.on()
            else:
                CO2.off()
        elif g.sw3state:  # CO2 over-ride set to "ON"
            CO2.on()
        elif not g.sw3state:  # CO2 over-ride set to "OFF"
            CO2.off()

        # ===============================================================
        # Fertiliser dosing pump
        # ===============================================================
        #
        # if current_mins >= hhmm2min(g.dose_time):
        #     if not dosing:
        #         dose_start = time.monotonic()
        #         dosing = True
        #         dose_end = dose_start + g.dose_duration
        #         doser.on()
        #         dose_elapsed = int(time.monotonic()) - dose_end
        #     else:
        #         if dose_elapsed > g.dose_duration:
        #             doser.off()
        #             dosing = False

#        print("sw1 : ", g.sw1state)
#        print("sw2 : ", g.sw2state)
#        print("sw3 : ", g.sw3state)
        time.sleep(0.1)

if __name__ == '__main__':
    try:
        t = time.localtime()
        print("Starting  aq_lightControl.py")
        print(time.asctime(t))
        light_control()

    except KeyboardInterrupt:
        pass
