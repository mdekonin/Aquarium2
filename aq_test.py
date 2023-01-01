# Test the modules so far
import time
import aq_relays as relays
import aq_switches as switches
#import aq_sensors as sensors

sw1 = switches.Switch(23, 22)
sw2 = switches.Switch(0, 1)
sw3 = switches.Switch(12, 20)

light1 = relays.Relay(26)
light2 = relays.Relay(21)
CO2 = relays.Relay(13)

while True:
    if sw1.get_state():
        light1.on()
    elif not sw1.get_state():
        light1.off()
    else:
        pass

    if sw2.get_state():
        light2.on()
    elif not sw2.get_state():
        light2.off()
    else:
        pass

    if sw3.get_state():
        CO2.on()
    elif not sw3.get_state():
        CO2.off()
    else:
        pass

    time.sleep(.5)



