# Call Forwarder

This project is in development. I'll be taking notes along the way: [NOTES.md](./NOTES.md)

## Shoutouts

Thanks to Pradeep Singh (@pradeesi) for blogging about his work.
Thanks to @havocsec for adapting Pradeep's work into a Python3 API for the Conexant CX93001 modem.

## Get Started

* direnv
* install reqs

## Usage 

Here we use `nohup` as a simple way to keep the process alive on our Pi

```sh
nohup python test.py > call_details.log &
```

## References

* Initial Inspiration: [Forward Your Landline Apartment Buzzer to your Cell Phone](https://www.ryansteele.ca/2019/07/15/forward-your-landline-apartment-buzzer-to-your-cell-phone/)
* [RasPBX: Asterisk for Raspberry Pi](http://www.raspberry-asterisk.org/faq/#analog)
* [USB Analog Modem with Raspberry Pi (first in a series of several guides with accompanying python code)](https://iotbytes.wordpress.com/usb-analog-modem-with-raspberry-pi/)
* Rotary Phone Conversion to VoIP with Raspberry Pi
  * [Blog Post](https://hackaday.com/2015/03/09/convert-a-rotary-phone-to-voip-using-raspberry-pi/)
  * [Source Code (GitHub)](https://github.com/hnesland/aselektriskbureau)
* How I turned my old rotary phone into a virtual assistant
  * [Blog Post](https://tcz.medium.com/how-i-turned-my-old-rotary-phone-into-a-virtual-assistant-24f35ca9884f)
  * [Source Code (GitHub)](https://github.com/tcz/rotary)
* [Python3 API for Conexant CX93001 modem](https://github.com/havocsec/cx93001)

### Conversation Threads
* https://forums.raspberrypi.com/viewtopic.php?t=40326&p=330143
* https://groups.google.com/g/comp.sys.raspberry-pi/c/OJyrq1-_Xm8?pli=1
* https://groups.google.com/g/uk.telecom.voip/c/AcJJLLUgA4w/m/_B4xZbpfIAYJ
* https://arstechnica.com/civis/viewtopic.php?f=11&t=1453581
* https://www.reddit.com/r/vancouver/comments/tlvefd/old_vancouver_apartments_question/
