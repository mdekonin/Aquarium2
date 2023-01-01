#
# This module provides the comms handling and command processing for a remote administration console
# It opens port 5540 and listens for a command to which it then responds and closes the connection.
# It then waits for another connection.
#

import aq_global as g
import socket
import os


# Initialise Socket Handler
def initSocketHandler():
    serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # close port when process exits
    serverSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    HOSTNAME = ""
    IP_PORT = 5540

    try:
        serverSocket.bind((HOSTNAME, IP_PORT))
    except socket.error as msg:
        m = "ERROR : Bind failed"
        print(m)
        #sys.exit()
    serverSocket.listen(10)
    #INFO : Waiting for connection
    isConnected = False
    return(serverSocket)

def socketHandler(serverSocket):
    while True:
        cmd = ""
        connection, address = serverSocket.accept()
        print("Connection established with " + address[0])
        isConnected = True
        try:
            cmd = connection.recv(1024)
        except socket.error as msg:
            # happens when connection is reset by peer"
            break
        print("Received cmd : " + str(cmd) + "len : " + str(len(cmd)))
        if len(cmd) != 0:
            cmd = cmd.decode('utf-8')
            response = executeCommand(cmd)
            connection.send(bytes(response, 'utf-8'))
            connection.close()
            isConnected = False


def set_cmd(cmd_string):
    cmd_bits = cmd_string.split('.')
    action_time = cmd_bits.pop()
    action = cmd_bits.pop()
    if action == "light1on":
        g.light1ontime = action_time
    elif action == "light1off":
        g.light1offtime = action_time
    elif action == "light2on":
        g.CO2offtime = action_time
    elif action == "light2off":
        g.light2offtime = action_time
    elif action == "CO2on":
        g.CO2ontime = action_time
    elif action == "CO2off":
        g.CO2offtime = action_time
    else:
        action = "INVALID ACTION " + action
    return (action + " : " + str(action_time))


def help_cmd():
    aq = []
    aq.append("The following commands ae available")
    aq.append("help      : This help")
    aq.append("status    : returns current status")
    aq.append("temp      : returns the water temperature")
    aq.append("pH        : returns the water pH")
    aq.append("flush     : flushes log data to disk")
    aq.append("auto      : displays current automation times for lights and CO2")
    aq.append("set       : allows the automation times to be set for lights and CO2")
    aq.append("          : format set.action.time")
    aq.append("          : actions light1on | light1off | light2on | light2off | CO2on | CO2off")
    aq.append("          : example set.light2on.08:50 (note leading zeroes are required)")
    resp = ""
    for i in range(0, 11):
        resp = resp + aq[i] + "\n"
    return (resp)


def status_cmd():
    r0 = "Software version : " + g.SW_VERSION
    r1 = "Temperature (C)  : " + str(g.temp_c)
    r2 = "pH               : " + str(g.pH_avg + " (Last reading : " + str(g.pH_last)) + ")"
    r3 = "Light1 Status    : " + str(g.sw1state)
    r4 = "Light2 Status    : " + str(g.sw2state)
    r5 = "CO2 Status       : " + str(g.sw3state)
    resp = r0 + "\n" + r1 + "\n" + r2 + "\n" + r3 + "\n" + r4 + "\n" + r5 + "\n"
    return (resp)


def auto_cmd():
    r0 = "Light 1 on time : " + g.light1ontime + "   |   Light 1 off time   : " + g.light1offtime
    r1 = "Light 2 on time : " + g.light2ontime + "   |   Light 2 off time   : " + g.light2offtime
    r2 = "CO2 on time     : " + g.CO2ontime + "   |   CO2 off time       : " + g.CO2offtime
    resp = r0 + "\n" + r1 + "\n" + r2 + "\n"
    return (resp)


def executeCommand(cmd):
    if cmd == "help":
        resp = help_cmd()
    elif cmd == 'status':
        resp = status_cmd()
    elif cmd == 'temp':
        resp = "Temperature (C)= " + str(g.temp_c)
    elif cmd == 'pH':
        resp = "pH = " + g.pH_avg + " (Last reading = " + g.pH_last + ")"
    elif cmd == 'flush':
        resp = "flushing output buffers"
        g.outFile.flush()
        os.fsync(g.outFile)
    elif cmd == 'auto':
        resp = auto_cmd()
    elif cmd.startswith("set"):
        resp = set_cmd(cmd)
    else:
        r0 = "Invalid command received : " + cmd
        r1 = "Valid commands are help | status | temp | pH | flush | auto | set"
        resp = r0 + "\n" + r1 + "\n"
    return (resp)
