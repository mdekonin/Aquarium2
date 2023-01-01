#
# This module logs data to a csv file and operational messages to a log file
#
# TESTED OK 31/1/2020
#
import locale
import datetime
import csv
import aq_global as g

locale.setlocale(locale.LC_ALL,"")


LOGFILE_NAME = "/home/pi/aquarium2/2.02/aq_logfile.log"
DATAFILE_NAME = "/home/pi/aquarium2/2.02/aq_datafile.csv"

# Open the log  and data files
def open_datafile():
    try:
        outFile = open(DATAFILE_NAME, 'a')
        g.outFile = outFile
        outData = csv.writer(outFile, delimiter=',')

    except IOError as err:
        print("ERROR : can't open data file")
        print(err)
        pass
    return(outData)

def write_datafile(out,temp_c, pH_avg, pH_last):
    d = datetime.datetime.now().strftime("%x")
    t = datetime.datetime.now().strftime("%X")
    out.writerow([d, t, temp_c, pH_avg, pH_last])
    


#---------------------------------------------------------------------------


def open_logfile():
    try:
        logfile = (open(LOGFILE_NAME, "a+", 1))
    except IOError as err:
        print("ERROR : Can't open logfile")
        print(err)
        logfile = None
        pass
    return(logfile)


def close_logfile(logfile):
    logfile.close()


def write_logfile(logfile, l_record):
    m_date = datetime.datetime.now().strftime("%x")
    m_time = datetime.datetime.now().strftime("%X")
    logrecord = m_date + " " + m_time + " " + l_record + "\n"
    logfile.write(logrecord)  # Write to log file
    logfile.flush()



if __name__ == '__main__':
    try:
        out = open_datafile()
        log = open_logfile()
        while True:
            t = str(25.0)
            p = str(6.6)
            write_datafile(out, t, p)
            log_rec = 'temp = ' + t + ' pH = ' + p
            write_logfile(log, log_rec)
            time.sleep(1)
    except KeyboardInterrupt:
        pass
