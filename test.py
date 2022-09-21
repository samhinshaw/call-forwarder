#!/usr/bin/env python
from modem import CX93001
from threading import Timer


with CX93001(
    modem_name="Conexant Systems (Rockwell), Inc. USB Modem",
    port="/dev/ttyACM0",
    baudrate=115200,
) as modem:
    print('start')
    modem.__output.subscribe(lambda x: print(x))
    print('subscribed')
    def push():
        modem.push("hi")

    Timer(1.0, push).start()
    Timer(2.0, push).start()
    Timer(3.0, push).start()
