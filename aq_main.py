#========================================================================================
#
# Aquarium Controller 2.0
#
# Author : Michael de Koning
#  Date : 02/02/2020
#
#  This program consists of a number of threads, all running independently and asynchronously :
#  1. readSwitches : monitors the front panel over-ride switches
#  2. light_control     :  switches lights and CO2 injection ON/OFF based on schedule and state of over-ride switches
#  3. outLCD : displays messages on the front panel  16x2 LCD display
#  4. socketHandler: Admin console to communicate with a client to display status and set timers
#  5. read_sensors reads the analog pH probe and the oneWire temperature probe
#  6. mClock that simply displays the time on the LCD
#
# CHANGE LOG :
# 02/02/2020    New version 2.0 version to modularise and implement OOP in some areas
# 10/02/2020    v2.01 pass paramters for writing to data logger rather than using global variables
# 02/03/2020    add support for relay #4 on gpio 26 to control 12V DC motor for fertiliser dosing pump



# import


import time
import threading
import subprocess
from queue import Queue
import aq_logging as log
import aq_sensors as sensor
import aq_light_control as lights
import aq_LCD as LCD
import aq_admin_console as admin
import locale

import aq_global as g




# LCD.lcd_init()
qLCD = Queue()  # create the queue to pass LCD messages to LCD thread

# ==================================== BEGIN MAIN LOOP ===========================================

def main():

    locale.setlocale(locale.LC_ALL, "")
    g.SW_VERSION = 'Aquarium v2.02T'

    data_fd = log.open_datafile()
    log_fd = log.open_logfile()
    
    qLCD.put({'LCD1': g.SW_VERSION})
    qLCD.put({'LCD2': 'Initialising ... '})

    m = "INFO : ***** RESTARTING : " + g.SW_VERSION + " *****"
    print(m)
    log.write_logfile(log_fd, m)

   
    # Create LCD thread
    mLCD = threading.Thread(target=outLCD, args=(log_fd,))
    mLCD.daemon = True
    mLCD.start()

    # Create the clock thread
    clk = threading.Thread(target=mClock, args=(log_fd,))
    clk.daemon = True
    clk.start()

    # Create readSensors thread to read water temperature and pH
    rt = threading.Thread(target=read_sensors, args=(log_fd,data_fd))
    rt.daemon = True
    rt.start()

    # Create Light Control thread
    m = "INFO : Starting Light Control thread."
    print(m)
    log.write_logfile(log_fd, m)
    time.sleep(5)  # just make sure everything else has had time to start up
    try:
        lc = threading.Thread(target=lights.light_control, args=())
        lc.daemon = True
        lc.start()
    except:
        m = "ERROR: light control thread failed to start"
        print(m)
        log.write_logfile(log_fd, m)
        pass


    # Create message server thread to handle admin requests
    m = "INFO : Starting  message server thread."
    print(m)
    log.write_logfile(log_fd, m)
    adminSocket = admin.initSocketHandler()
    sh = threading.Thread(target=admin.socketHandler, args=(adminSocket,))
    sh.daemon = True
    sh.start()

    # Get the IP address
    IP = subprocess.check_output(["hostname", "-I"]).split()[0]
    IP = str(IP)
    IP = IP[2:len(IP) - 1]
    m = "INFO : IP address : " + IP
    print(m)
    log.write_logfile(log_fd, m)
    qLCD.put({'LCD3': IP})  # add it to the LCD queue

    # try:
    #   print("INFO : Setting trigger on RESET button")
    #   GPIO.add_event_detect(reset, GPIO.FALLING, callback=m5_reset, bouncetime=300)
    # except:
    #   print("ERROR : Failed to se trigger on RESET button")
    #   pass

    m = "INFO : Initialisation complete"
    print(m)
    log.write_logfile(log_fd, m)
    qLCD.put({'LCD2': 'Running ...'})

    while True:
        time.sleep(0.01)


# ----------------------
# Debug handler
# ----------------------
def debug(text):
    if VERBOSE:
        print("DEBUG : --- ", text)


# --------------------------------- read the temperature and pH -------------------------------------------
def read_sensors(fd, dfd):
    m = "INFO : Starting  read_sensors thread."
    print(m)
    log.write_logfile(fd, m)
    temp1 = sensor.M_DS18B20()
    pH1 = sensor.M_ADS1015()
    while True:
        if temp1.oneWire :
            tempC = temp1.read_temp()
        else:
            tempC = "N/A"
        if pH1.pH_probe:
            pH, last_pH = pH1.read_pH()
        else:
            pH = "N/A"
            last_pH = "N/A"

        outString = "Temperature " + str(tempC)
        print(outString)
        qLCD.put({'LCD5': outString})  # output to LCD
        outString = "pH          " + str(pH)
        qLCD.put({'LCD6': outString})  # output to LCD
        log.write_datafile(dfd, tempC, pH, last_pH)
        time.sleep(60)

# -------------------------------- update the clock every 30 seconds or so --------------------------------
def mClock(fd):
    m = "INFO : Starting clock thread."
    print(m)
    log.write_logfile(fd, m)
    while True:
        datetime = time.asctime()
        mtime = datetime[11:16]
        mdate = datetime[8:10] + datetime[4:7] + datetime[22:24]
        qLCD.put({'LCD4': mdate + '   ' + mtime})  # add it to the LCD queue
        time.sleep(29.9)


# -------------------- Read the Queue for LCD variables and output to LCD Display -----------------------
#
# Queue format :
#
# 
#


def outLCD(fd):
    return ### temporarily bypass
    m = "INFO : Starting LCD thread."
    print(m)
    log.write_logfile(fd, m)
    LCD_LINE_1 = 0x80  # LCD RAM address for the 1st line
    LCD_LINE_2 = 0xC0  # LCD RAM address for the 2nd line
    LCD1 = "                "
    LCD2 = "                "
    LCD3 = "                "
    LCD4 = "                "
    LCD5 = "                "
    LCD6 = "                "
    m = "INFO : LCD thread started"
    print(m)
    log.write_logfile(fd, m)
    while True:
        if qLCD.qsize() >> 10:
            m = "WARNING : Queue size = " + str(qLCD.qsize())
            print(m)
            log.write_logfile(fd, m)
        try:
            inputDict = qLCD.get_nowait()
            if inputDict is not None:
                for key, value in inputDict.items():
                    if key == 'LCD1':
                        LCD1 = value
                    elif key == 'LCD2':
                        LCD2 = value
                    elif key == 'LCD3':
                        LCD3 = value
                    elif key == 'LCD4':
                        LCD4 = value
                    elif key == 'LCD5':
                        LCD5 = value
                    elif key == 'LCD6':
                        LCD6 = value
        except:
            pass
        LCD.lcd_string(LCD1, LCD_LINE_1)
        LCD.lcd_string(LCD2, LCD_LINE_2)
        time.sleep(3)
        LCD.lcd_string(LCD3, LCD_LINE_1)
        LCD.lcd_string(LCD4, LCD_LINE_2)
        time.sleep(3)
        LCD.lcd_string(LCD5, LCD_LINE_1)
        LCD.lcd_string(LCD6, LCD_LINE_2)
        time.sleep(3)

    # ----------------------------------------< Begin Logging Code >-------------------------------------




# ----------------------------------------< End Logging Code >-------------------------------------


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        pass
    finally:
        m = "ERROR : Unexpected termination"
        print(m)
