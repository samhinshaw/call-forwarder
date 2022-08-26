import serial  # pip install pyserial
import atexit
import sys
import re
import wave
from datetime import datetime
import os
import fcntl
import subprocess


RINGS_BEFORE_AUTO_ANSWER = 2  # Must be greater than 1
MODEM_RESPONSE_READ_TIMEOUT = 120  # Time in Seconds (Default 120 Seconds)
MODEM_NAME = "Conexant Systems (Rockwell), Inc. USB Modem"  # Modem Manufacturer, For Ex: 'U.S. Robotics' if the 'lsusb' cmd output is similar to "Bus 001 Device 004: ID 0baf:0303 U.S. Robotics"


# Record Voice Mail Variables
REC_VM_MAX_DURATION = 120  # Time in Seconds

# Used in global event listener
disable_modem_event_listener = True

# Global Modem Object
analog_modem = serial.Serial()

audio_file_name = ""

# =================================================================
# Set COM Port settings
# =================================================================
def set_COM_port_settings(com_port):
    analog_modem.port = com_port
    analog_modem.baudrate = 57600  # 9600 #115200
    analog_modem.bytesize = serial.EIGHTBITS  # number of bits per bytes
    analog_modem.parity = serial.PARITY_NONE  # set parity check: no parity
    analog_modem.stopbits = serial.STOPBITS_ONE  # number of stop bits
    analog_modem.timeout = 3  # non-block read
    analog_modem.xonxoff = False  # disable software flow control
    analog_modem.rtscts = False  # disable hardware (RTS/CTS) flow control
    analog_modem.dsrdtr = False  # disable hardware (DSR/DTR) flow control
    analog_modem.writeTimeout = 3  # timeout for write


# =================================================================
# Read AT Command Response from the Modem
# =================================================================
def read_AT_cmd_response(expected_response="OK"):

    # Set the auto timeout interval
    start_time = datetime.now()

    try:
        while 1:
            # Read Modem Data on Serial Rx Pin
            modem_response = analog_modem.readline()
            print(modem_response)
            # Recieved expected Response
            if expected_response == modem_response.strip(" \t\n\r" + chr(16)):
                return True
            # Failed to execute the command successfully
            elif "ERROR" in modem_response.strip(" \t\n\r" + chr(16)):
                return False
            # Timeout
            elif (datetime.now() - start_time).seconds > MODEM_RESPONSE_READ_TIMEOUT:
                return False

    except:
        print("Error in read_modem_response function...")
        return False


# =================================================================
# Execute AT Commands at the Modem
# =================================================================
def exec_AT_cmd(modem_AT_cmd, expected_response="OK"):

    global disable_modem_event_listener
    disable_modem_event_listener = True

    try:
        # Send command to the Modem
        analog_modem.write((modem_AT_cmd + "\r").encode())
        # Read Modem response
        execution_status = read_AT_cmd_response(expected_response)
        disable_modem_event_listener = False
        # Return command execution status
        return execution_status

    except:
        disable_modem_event_listener = False
        print("Error: Failed to execute the command")
        return False


# =================================================================
# Close the Serial Port
# =================================================================
def close_modem_port():

    # Try to close any active call
    try:
        exec_AT_cmd("ATH")
    except:
        pass

    # Close the Serial COM Port
    try:
        if analog_modem.isOpen():
            analog_modem.close()
            print(("Serial Port closed..."))
    except:
        print("Error: Unable to close the Serial Port.")
        sys.exit()


# =================================================================


# =================================================================
# Initialize Modem
# =================================================================
def detect_COM_port():

    # List all the Serial COM Ports on Raspberry Pi
    proc = subprocess.Popen(
        ["ls /dev/tty[A-Za-z]*"], shell=True, stdout=subprocess.PIPE
    )
    com_ports = proc.communicate()[0]
    com_ports_list = com_ports.split("\n")

    # Find the right port associated with the Voice Modem
    for com_port in com_ports_list:
        if "tty" in com_port:
            # Try to open the COM Port and execute AT Command
            try:
                # Set the COM Port Settings
                set_COM_port_settings(com_port)
                analog_modem.open()
            except:
                print("Unable to open COM Port: " + com_port)
                pass
            else:
                # Try to put Modem in Voice Mode
                if not exec_AT_cmd("AT+FCLASS=8", "OK"):
                    print("Error: Failed to put modem into voice mode.")
                    if analog_modem.isOpen():
                        analog_modem.close()
                else:
                    # Found the COM Port exit the loop
                    print("Modem COM Port is: " + com_port)
                    analog_modem.flushInput()
                    analog_modem.flushOutput()
                    break


# Close the Modem Port when the program terminates
atexit.register(close_modem_port)

# see if we can detect the modem
detect_COM_port()
