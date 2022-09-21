#!/usr/bin/env python
from modem import CX93001
from threading import Timer


with CX93001(
    modem_name="Conexant Systems (Rockwell), Inc. USB Modem",
    port="/dev/ttyACM0",
    baudrate=115200,
) as modem:
    modem.read_input()
