

# 01/01/2023 Completely re-written DS18B20 handling usingW1ThermSensor
#
# This module has classes for  two sensors on the Raspberry Pi :
#  1. the 12 bit ADC module which in this project is used to read the pH probe.
#  2. the temperature sensor, a DS18B20 http://image.dfrobot.com/image/data/DFR0198/DS18B20.pdf
#     Using PyPI library W1ThermSensor availabe here https://pypi.org/project/w1thermsensor/
#
# Phase 1. DS18B20
# Phase 2. add MQTT client code to publish results
#
# to be done :
# a. handling for sensor not ready error
# Oct 12 11:44:56 aquarium python3[15227]:   File "/home/pi/aquarium2/2.02/aq_sensors.py", line 38, in get_Temp
# Oct 12 11:44:56 aquarium python3[15227]:     tempC = sensor.get_temperature()
# Oct 12 11:44:56 aquarium python3[15227]:   File "/usr/local/lib/python3.9/dist-packages/w1thermsensor/core.py", line 26>
# Oct 12 11:44:56 aquarium python3[15227]:     raw_temperature_line = self.get_raw_sensor_strings()[1]
# Oct 12 11:44:56 aquarium python3[15227]:   File "/usr/local/lib/python3.9/dist-packages/w1thermsensor/core.py", line 25>
# Oct 12 11:44:56 aquarium python3[15227]:     raise SensorNotReadyError(self)
# Oct 12 11:44:56 aquarium python3[15227]: w1thermsensor.errors.SensorNotReadyError: Sensor 0416c0f6b7ff is not yet ready>
# Oct 12 11:44:56 aquarium systemd[1]: aq_sensors.service: Main process exited, code=exited, status=1/FAILURE
# Oct 12 11:44:56 aquarium systemd[1]: aq_sensors.service: Failed with result 'exit-code'.
# Oct 12 11:44:56 aquarium systemd[1]: aq_sensors.service: Consumed 17min 55.394s CPU time.

import paho.mqtt.client as mqttClient
import time
from datetime import datetime
from w1thermsensor import W1ThermSensor, Sensor, Unit
import syslog
import json

MQTT_broker = "Pi-Hole"
MQTT_port = 1883
MQTT_topic = "Temperature"
INTERVAL = 240

def log(msg):
    print(msg)
    syslog.syslog(msg)


# give everything a chance to start up
def startup(seconds):
    log("INFO : Pausing while system starts up")
    for i in range(0,seconds):
        print
        time.sleep(1)
    log("INFO : OK to go now")


def on_connect(client, userdata, flags, rc):
    if rc == 0:
        log("INFO : Connected to MQTT broker " + MQTT_broker + " : " + str(MQTT_port))
        global Connected                #Use global variable
        Connected = True                #Signal connection 
    else:
        log("ERROR : Connection failed with return code : " + str(rc))

def get_Temp(client):
    log("DEBUG : entering get_temp")
    for sensor in W1ThermSensor.get_available_sensors([Sensor.DS18B20]):
        log("DEBUG : in the sensor loop ... " + sensor.id)
        try :
            tempC = sensor.get_temperature()
            sensor_ok = True
        except:
            log("ERROR : Undefined sensor error. Sensor ID " + sensor.id)
            sensor_ok = False
            continue                      # ... and try the remaining sensors and loop and try again.
        if sensor_ok:
            msg_payload = {"timestamp" : str(datetime.now()), "sensor_id" : sensor.id, "sensor_type" : "DS18B20", "temp_C" : tempC}
            msg_json = json.dumps(msg_payload)
            log(msg_json)
            client.publish(MQTT_topic, msg_json)

    return()

def get_pH():
    return()

if __name__ == '__main__':
    startup(10)
    log("INFO : logging interval " + str(INTERVAL) + " seconds")
    syslog.openlog(logoption=syslog.LOG_PID)
    log("INFO : Temperature logging started ...")
    Connected = False                                   #global variable for the state of the connection
    broker_address= MQTT_broker
    port = MQTT_port
    user = "mdekonin"
    password = "Ru$$ia2day00"
    
    client = mqttClient.Client()                        #create new instance
    client.username_pw_set(user, password=password)    #set username and password
    client.on_connect= on_connect                      #attach function to callback
    client.connect(broker_address, port=port)          #connect to broker
    client.loop_start()                                #start the loop
    log("DEBUG : Connected? " + str(Connected))
    while Connected != True:    #Wait for connection
        time.sleep(0.1)
    log("DEBUG : Connected? " + str(Connected))
    
    try :
        while True:
            get_Temp(client)
            get_pH()
            time.sleep(INTERVAL)
    except KeyboardInterrupt:
        log("INFO : Terminating connection to MQTT broker")
        log("INFO : Terminated.")
        client.disconnect()
        client.loop_stop()
