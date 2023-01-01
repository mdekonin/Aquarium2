#
# This module has classes for  two sensors on the Raspberry Pi :
#  1. the 12 bit ADC module which in this project is used to read the pH probe.
#  2. the temperature sensor, a DS18B20 http://image.dfrobot.com/image/data/DFR0198/DS18B20.pdf
#
# TESTED OK 30/01/2020
#
import time
import board
import busio
import adafruit_ads1x15.ads1015 as ADS
from adafruit_ads1x15.analog_in import AnalogIn
from collections import deque
from decimal import Decimal
import os  # import os module
import glob  # import glob module
import aq_global as g

from datetime import datetime
from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import SYNCHRONOUS

        

class M_ADS1015:
    # Class Object Attributes
    # calibration figures of the pH probe - linear response
    VpH4 = 1.232
    VpH7 = 0.74

    def __init__(self):
        self.pH = 0
        self.pH_last = 0
        self.pH_avg = 0
        # Initialise ads1015 ADC
        try:
            self.i2c = busio.I2C(board.SCL, board.SDA)
            print(self.i2c)
            self.ads = ADS.ADS1015(self.i2c)
            print(self.ads)
            self.pH_probe = True
        except:
            print("ADS1015 ADC initialisation failed; continuing with no pH measurement")
            self.pH_probe = False
            pass

        # calculate gradient (m) and intercept (c) of pH graph usiing latest calibration data
        self.m = (self.VpH7 - self.VpH4) / (7 - 4)
        self.c = self.VpH7 - (self.m * 7)
        print(f"m = {self.m}  |  c = {self.c}")

        # Initialise the queue with a max length of 10 and all entries at neutral pH
        self.pH_array = deque(10 * [Decimal(7.0)], 10)

    def read_pH(self):

        try:
            # get the pH of the water
            self.pH = Decimal(0)
            for self.i in range(1, 11):  # take 10 readings and average them
                self.chan = AnalogIn(self.ads, ADS.P0)
                self.pH = self.pH + Decimal((self.chan.voltage - self.c) / self.m)
                time.sleep(0.1)
            self.pH = round(Decimal(self.pH / self.i), 3)
            self.pH_last = self.pH  # save this for comparison to the running average
            self.pH_array.appendleft(self.pH)
            self.pH = Decimal(0)
            for self.i in range(0, 10):  # now average the last 10 averages
                self.pH = self.pH + self.pH_array[self.i]
            self.pH_avg = round(Decimal(self.pH / (self.i + 1)), 3)
            g.pH_avg = str(self.pH_avg)     # save a copy for the admin console
            g.pH_last = str(self.pH_last )  # save a copy for the admin console
            print("pH average  : " + g.pH_avg)
            print("pH last     : " + g.pH_last)
        # trap the error if pG ADC is not found
        except Exception as error:
            print("Unexpected error in pH probe/ADC ",error)
            self.pH_avg = "N/A"
            self.pH_last = "N/A"
            pass
        return self.pH_avg, self.pH_last



class M_DS18B20:

    def __init__(self):
        # initialise 1-wire device (Thermometer)
        os.system('modprobe w1-gpio')  # load one wire communication device kernel modules
        os.system('modprobe w1-therm')
        self.base_dir = '/sys/bus/w1/devices/'  # point to the address
        try:
            self.device_folder = glob.glob(self.base_dir + '28*')[0]  # find device with address starting from 28*
            self.device_file = self.device_folder + '/w1_slave'  # store the details
            self.device = open(self.device_file, 'r')
            self.oneWire = True
            print("DFR0198 initialised")
        except:
            self.oneWire = False
            print("No one wire devices found; continuing with no temperature measurement")
            pass

    def read_temp(self):
        self.device.seek(0)  # go to start of file
        self.lines = self.device.readlines()
        while self.lines[0].strip()[-3:] != 'YES':  # ignore first line
            time.sleep(0.2)
            self.device.seek(0)
            self.lines = self.device.readlines()
        self.equals_pos = self.lines[1].find('t=')  # find temperature in the details
        if self.equals_pos != -1:
            self.temp_string = self.lines[1][self.equals_pos + 2:]
            self.temp_c = float(self.temp_string) / 1000.0  # convert to Celsius
            self.temp_f = self.temp_c * 9.0 / 5.0 + 32.0  # convert to Fahrenheit
            g.temp_c = str(self.temp_c) # save a copy for the admin console
            print("Temperature : " + g.temp_c)            
        return(self.temp_c)

if __name__ == '__main__':
    # You can generate an API token from the "API Tokens Tab" in the UI
    token = os.getenv("INFLUX_TOKEN")
    org = "mdekonin62@outlook.com"
    bucket = "Aquarium Bucket"
    try :
        temp1 = M_DS18B20()
        pH1 = M_ADS1015()
        M_influxdb_client_init()
        with InfluxDBClient(url="https://ap-southeast-2-1.aws.cloud2.influxdata.com", token=token, org=org) as client:
            while True:
                if temp1.oneWire:
                    t = temp1.read_temp()
                if pH1.pH_probe:
                    p = pH1.read_pH()                
                write_api = client.write_api(write_options=SYNCHRONOUS)
                data = "temperature",t,"pH",p
                write_api.write(bucket, org, data)
                time.sleep(30)
    except KeyboardInterrupt:
        client.close()
        pass
