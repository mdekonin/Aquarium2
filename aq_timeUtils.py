#
# This module simply provides some utilities for manipulating the time to make easy calculations for determining
# whether to switch a light or the CO2 injection on or off.
#


# accept number of minutes (int) since midnight and return time in hh:mm format
def min2hhmm(mins):
    hh = str(int(mins/60)) # throw away the remainder (minutes)
    mm = str(mins % 60)     # and now keep the minutes
    if len(hh) == 1:
        hh = "0" + hh
    elif len(hh) == 0:
        hh = "00"
    if len(mm) == 1:
        mm = "0" + mm
    elif len(mm) == 0:
        mm = "00"
    return(hh + ":" + mm)

# accept a time in hh:mm format and return number of minutes since midnight
def hhmm2min(t):
    t_bits = t.split(":")
    mm = t_bits.pop()
    hh = t_bits.pop()
    mins = int(hh)*60 + int(mm)
    return(mins)