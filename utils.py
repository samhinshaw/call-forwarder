import subprocess
import os
import fcntl


def reset(modem_name: str):
    # Equivalent of the _IO('U', 20) constant in the linux kernel.
    USBDEVFS_RESET = ord("U") << (4 * 2) | 20
    dev_path = ""

    # Bases on 'lsusb' command, get the usb device path in the following format -
    # /dev/bus/usb/<busnum>/<devnum>
    proc = subprocess.Popen(["lsusb"], stdout=subprocess.PIPE)
    out = proc.communicate()[0]
    lines = out.decode().split("\n")
    for line in lines:
        if modem_name in line:
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
