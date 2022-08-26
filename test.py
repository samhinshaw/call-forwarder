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
    analog_modem.baudrate = 57600 # 57600  # 9600 #115200
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
            print(modem_response.decode().strip(" \t\n\r" + chr(16)))
            # Recieved expected Response
            if expected_response == modem_response.decode().strip(" \t\n\r" + chr(16)):
                return True
            # Failed to execute the command successfully
            elif "ERROR" in modem_response.decode().strip(" \t\n\r" + chr(16)):
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
    com_ports_list = com_ports.decode().split("\n")

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


# =================================================================
# Initialize Modem
# =================================================================
def init_modem_settings():

    # Detect and Open the Modem Serial COM Port
    try:
        detect_COM_port()
    except:
        print("Error: Unable to open the Serial Port.")
        sys.exit()

    # Initialize the Modem
    try:
        # Flush any existing input outout data from the buffers
        analog_modem.flushInput()
        analog_modem.flushOutput()

        # Test Modem connection, using basic AT command.
        if not exec_AT_cmd("AT"):
            print("Error: Unable to access the Modem")

        # reset to factory default.
        if not exec_AT_cmd("ATZ3"):
            print("Error: Unable reset to factory default")

        # Display result codes in verbose form
        if not exec_AT_cmd("ATV1"):
            print("Error: Unable set response in verbose form")

        # Enable Command Echo Mode.
        if not exec_AT_cmd("ATE1"):
            print("Error: Failed to enable Command Echo Mode")

        # Enable formatted caller report.
        if not exec_AT_cmd("AT+VCID=1"):
            print("Error: Failed to enable formatted caller report.")

        # Flush any existing input outout data from the buffers
        analog_modem.flushInput()
        analog_modem.flushOutput()

    except:
        print("Error: unable to Initialize the Modem")
        sys.exit()


# =================================================================


# =================================================================
# Reset Modem
# =================================================================
def reset_USB_Device():

    # Close the COM Port if it's open
    try:
        if analog_modem.isOpen():
            analog_modem.close()
    except:
        pass

    # Equivalent of the _IO('U', 20) constant in the linux kernel.
    USBDEVFS_RESET = ord("U") << (4 * 2) | 20
    dev_path = ""

    # Bases on 'lsusb' command, get the usb device path in the following format -
    # /dev/bus/usb/<busnum>/<devnum>
    proc = subprocess.Popen(["lsusb"], stdout=subprocess.PIPE)
    out = proc.communicate()[0]
    lines = out.decode().split("\n")
    for line in lines:
        if MODEM_NAME in line:
            parts = line.split()
            bus = parts[1]
            dev = parts[3][:3]
            dev_path = "/dev/bus/usb/%s/%s" % (bus, dev)

    # Reset the USB Device
    fd = os.open(dev_path, os.O_WRONLY)
    try:
        fcntl.ioctl(fd, USBDEVFS_RESET, 0)
        print("Modem reset successful")
    finally:
        os.close(fd)

    # Re-initialize the Modem
    init_modem_settings()




# =================================================================
# Data Listener
# =================================================================
def read_data():

    global disable_modem_event_listener
    ring_data = ""

    while 1:

        if not disable_modem_event_listener:
            modem_data = analog_modem.readline()

            if modem_data != "":
                print(modem_data)

                # Check if <DLE>b is in the stream
                if (chr(16) + chr(98)) in modem_data:
                    # Terminate the call
                    if not exec_AT_cmd("ATH"):
                        print("Error: Busy Tone - Failed to terminate the call")
                        print("Trying to revoer the serial port")
                        recover_from_error()
                    else:
                        print("Busy Tone: Call Terminated")

                # Check if <DLE>s is in the stream
                if (chr(16) + chr(115)) == modem_data:
                    # Terminate the call
                    if not exec_AT_cmd("ATH"):
                        print("Error: Silence - Failed to terminate the call")
                        print("Trying to revoer the serial port")
                        recover_from_error()
                    else:
                        print("Silence: Call Terminated")

                if ("-s".encode() in modem_data) or (
                    ("<DLE>-s").encode() in modem_data
                ):
                    print("silence found during recording")
                    analog_modem.write(("<DLE>-!" + "\r").encode())

                if (
                    ("RING" in modem_data)
                    or ("DATE" in modem_data)
                    or ("TIME" in modem_data)
                    or ("NMBR" in modem_data)
                ):
                    global audio_file_name
                    if "NMBR" in modem_data:
                        from_phone = (modem_data[5:]).strip()
                    if "DATE" in modem_data:
                        call_date = (modem_data[5:]).strip()
                    if "TIME" in modem_data:
                        call_time = (modem_data[5:]).strip()
                    if "RING" in modem_data.strip(chr(16)):
                        ring_data = ring_data + modem_data
                        ring_count = ring_data.count("RING")
                        if ring_count == 1:
                            pass
                        elif ring_count == RINGS_BEFORE_AUTO_ANSWER:
                            ring_data = ""
                            audio_file_name = (
                                from_phone
                                + "_"
                                + call_date
                                + "_"
                                + call_time
                                + "_"
                                + str(datetime.strftime(datetime.now(), "%S"))
                                + ".wav"
                            )
                            from_phone = ""
                            call_date = ""
                            call_time = ""

                            record_audio()


# Run the program!


# Initialize the modem
init_modem_settings()

# Close the Modem Port when the program terminates
atexit.register(close_modem_port)

# see if we can detect the modem
detect_COM_port()
