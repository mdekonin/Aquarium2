

# 01/01/2023 Completely re-written DS18B20 handling usingW1ThermSensor
#
# This module has classes for  two sensors on the Raspberry Pi :
#  1. the 12 bit ADC module which in this project is used to read the pH probe.
#  2. the temperature sensor, a DS18B20 http://image.dfrobot.com/image/data/DFR0198/DS18B20.pdf
#     Using PyPI library W1ThermSensor availabe here https://pypi.org/project/w1thermsensor/
#
# Phase 1. DS18B20
# Phase 2. add MQTT client code to publish results
# trying to get conection to Domo.com working with certificate

import paho.mqtt.client as mqttClient
import time
from datetime import datetime
from w1thermsensor import W1ThermSensor, Sensor, Unit
import syslog
import ssl

MQTT_broker = "domo.import.domo.com"
MQTT_port = 8883
MQTT_topic = "Temperature"
INTERVAL = 300

def on_connect(client, userdata, flags, rc):
    print("Connection retunred " + str(rc))
    if rc == 0:
        print("Connected to broker")
        global Connected                #Use global variable
        Connected = True                #Signal connection 
    else:
        print("Connection failed")

def get_Temp(client):
    for sensor in W1ThermSensor.get_available_sensors([Sensor.DS18B20]):
        tempC = sensor.get_temperature()
        tag1 = "sensor_id=" + str(sensor.id)
        tag2 = "sensor_type=DS18B20"
        value = str(tempC)
        msg = str(datetime.now()) + "," + tag1 + "," + tag2 + "," + value
        print(msg)
        syslog.syslog(msg)
        client.publish(MQTT_topic, msg)
    return()

def get_pH():
    return()

if __name__ == '__main__':
    syslog.openlog(logoption=syslog.LOG_PID)
    syslog.syslog("Temperature logging started ...")
    Connected = False                                   #global variable for the state of the connection
    broker_address= MQTT_broker
    port = MQTT_port
    #user = "yourUser"
    #password = "yourPassword"
    client = mqttClient.Client()                        #create new instance
    print(client)
    #client.username_pw_set(user, password=password)    #set username and password
    client.on_connect= on_connect                      #attach function to callback
    print("tls_set")
    #client.tls_set("/etc/ssl/certs/ca-certificates.crt", tls_version=ssl.PROTOCOL_TLSv1_2)
    client.tls_set("/usr/local/share/ca-certificates/ca.crt")    #, tls_version=ssl.PROTOCOL_TLSv1_2)
    print("tls_insecure_set")
    client.tls_insecure_set(True)
    print("Connecting to MQTT broker")
    client.connect(broker_address, port=port)          #connect to broker
    print("Entering client loop")
    client.loop_start()                                #start the loop

    while Connected != True:    #Wait for connection
        print(". ", end="")
        time.sleep(0.5)
    try :
        while True:
            get_Temp(client)
            get_pH()
            time.sleep(INTERVAL)
    except KeyboardInterrupt:
        print("Terminating connection to MQTT broker")
        client.disconnect()
        client.loop_stop()
