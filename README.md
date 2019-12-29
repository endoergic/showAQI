#showAQI
little pi project to dislpay air quality index on a tiny monochrome by pulling data from RESTful interface hosted on thingspeak

setup:
* Use python3

install at startup:
crontab -e
add the following:
@reboot cd /home/pi/airmonitor/ && python3 ts_air_quality_logger_ext.py


howto: https://www.instructables.com/id/A-Low-cost-IoT-Air-Quality-Monitor-Based-on-Raspbe/
source: https://github.com/Mjrovai/Python4DS/tree/master/RPi_Air_Quality_Sensor
Author: Mjrovai
