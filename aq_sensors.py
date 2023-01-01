

# 01/01/2023 Completely re-written DS18B20 handling usingW1ThermSensor
#
# This module has classes for  two sensors on the Raspberry Pi :
#  1. the 12 bit ADC module which in this project is used to read the pH probe.
#  2. the temperature sensor, a DS18B20 http://image.dfrobot.com/image/data/DFR0198/DS18B20.pdf
#     Using PyPI library W1ThermSensor availabe here https://pypi.org/project/w1thermsensor/
#
# Phase 1. DS18B20
#
#from collections import deque
#from decimal import Decimal
#import aq_global as g



import time
from datetime import datetime
from w1thermsensor import W1ThermSensor, Sensor, Unit
import syslog

def get_Temp():
    for sensor in W1ThermSensor.get_available_sensors([Sensor.DS18B20]):
      print(datetime.now(), sensor.id, sensor.get_temperature(),"degrees C")
      syslog.syslog(str(datetime.now()) + " " + str(sensor.id) + " " + str(sensor.get_temperature()) + "degrees C")
    return()

def get_pH():
    return()

if __name__ == '__main__':
    syslog.openlog(logoption=syslog.LOG_PID)
    syslog.syslog("Temperature logging started ...")
    try :
        while True:
            get_Temp()
            get_pH()
            time.sleep(300)
    except KeyboardInterrupt:
        pass