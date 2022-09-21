import { SerialPort } from "serialport";
import { ReadlineParser } from "@serialport/parser-readline";

const MODEM_PORT = "/dev/ttyACM0";

const portOptions = {
  baudRate: 115200,
  dataBits: 8,
  stopBits: 1,
  parity: "none",
  line_end: "\r\n",
  read_time: 1000,
};

// port=port,
// baudrate=57600,  # 57600  # 9600 #115200
// bytesize=serial.EIGHTBITS,  # number of bits per bytes
// parity=serial.PARITY_NONE,  # set parity check: no parity
// stopbits=serial.STOPBITS_ONE,  # number of stop bits
// timeout=3,  # non-block read
// xonxoff=False,  # disable software flow control
// rtscts=False,  # disable hardware (RTS/CTS) flow control
// dsrdtr=False,  # disable hardware (DSR/DTR) flow control
// writeTimeout=3,  # timeout for write

const port = new SerialPort(
  {
    path: MODEM_PORT,
    baudRate: 115200,
    dataBits: 8,
    stopBits: 1,
    parity: "none",
    xon: false,
    xoff: false,
    rtscts: false,
    xany: false,
  },
  (err: unknown) => {
    if (err) {
      return console.error(err);
    }
  }
);



// Switches the port into "flowing mode"
port.on('data', function (data) {
  console.log('Data:', data)
})