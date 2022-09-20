from modem import CX93001

with CX93001(
    modem_name="Conexant Systems (Rockwell), Inc. USB Modem",
    port="/dev/ttyACM0",
    baudrate=115200,
) as modem:
    # this loop won't re-initiate until wait_call returns, since it's synchronous
    # wait_call will loop until it gets a response.
    while True:
        res = modem.wait_call()
        print(res)
