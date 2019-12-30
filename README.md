#showAQI
little pi project to dislpay air quality index on a tiny monochrome by pulling data from RESTful interface hosted on thingspeak

setup:
* Use python3
* follow this exactly: https://www.raspberrypi-spy.co.uk/2018/04/i2c-oled-display-module-with-raspberry-pi/


//the rest is for monitoring using sensor

install at startup:
crontab -e
add the following:
@reboot cd /home/pi/showAQI && python3 ShowAQI.py

python3 -m pip install Adafruit-SSD1306




howto: https://www.instructables.com/id/A-Low-cost-IoT-Air-Quality-Monitor-Based-on-Raspbe/
source: https://github.com/Mjrovai/Python4DS/tree/master/RPi_Air_Quality_Sensor
Author: Mjrovai
