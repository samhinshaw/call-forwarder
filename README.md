# Call Forwarder

Big shoutout to Pradeep Singh (@pradeesi) for blogging about his work.

## My Modem

Following the "[USB Analog Modem with Raspberry Pi](https://iotbytes.wordpress.com/usb-analog-modem-with-raspberry-pi/)" guide, I identified the following information about the [Startech USB Voice modem](https://www.startech.com/en-ca/networking-io/usb56kemh2) I purchased.

```sh
lsusb
# Bus 001 Device 004: ID 0572:1349 Conexant Systems (Rockwell), Inc. USB Modem
```

Modem Name: `Conexant Systems (Rockwell), Inc. USB Modem`
Device Number: `4`

```sh
lsusb -t
# Port 3: Dev 4, If 0, Class=Communications, Driver=cdc_acm, 12M
# Port 3: Dev 4, If 1, Class=CDC Data, Driver=cdc_acm, 12M
```

Device 4 (our modem) is using the `cdc_acm` kernel module driver, "Communication Device Class (Abstract Control Model)"

```sh
dmesg | grep tty
# cdc_acm 1-1.3:1.0: ttyACM0: USB ACM device
```

Here we can see a message from the cdc_acm kernel module referencing our USB ACM device at COM port `ttyACM0`. We can access this at `/dev/ttyACM0`.
