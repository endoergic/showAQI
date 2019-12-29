import time
from datetime import datetime

import Adafruit_GPIO.SPI as SPI
import Adafruit_SSD1306

import requests


from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont


def datetime_from_utc_to_local(utc_datetime):
	now_timestamp = time.time()
	offset = datetime.fromtimestamp(now_timestamp) - datetime.utcfromtimestamp(now_timestamp)
	return utc_datetime + offset
	
	
# Raspberry Pi pin configuration:
RST = None     # on the PiOLED this pin isnt used
# Note the following are only used with SPI:
DC = 23
SPI_PORT = 0
SPI_DEVICE = 0

# 128x32 display with hardware I2C:
disp = Adafruit_SSD1306.SSD1306_128_32(rst=RST)

# Initialize library.
disp.begin()

# Clear display.
disp.clear()
disp.display()

# Create blank image for drawing.
# Make sure to create image with mode '1' for 1-bit color.
width = disp.width
height = disp.height
image = Image.new('1', (width, height))

# Get drawing object to draw on image.
draw = ImageDraw.Draw(image)

# Draw a black filled box to clear the image.
draw.rectangle((0,0,width,height), outline=0, fill=0)

# Draw some shapes.
# First define some constants to allow easy resizing of shapes.
padding = -2
top = padding
bottom = height-padding
# Move left to right keeping track of the current x position for drawing shapes.
x = 0


# Load default font.
font = ImageFont.load_default()

#string constants
field1Name = 'PMT2.5[μm/m3]'
field2Name = 'PMT2.5[AQI-Index]'
field3Name = 'PMT10[μm/m3]'
field4Name = 'PMT10[AQI-Index]'

while True:

	# Draw a black filled box to clear the image.
	draw.rectangle((0,0,width,height), outline=0, fill=0)

	# Write two lines of text.

	#draw.text((x, top),       "IP: " + str(IP),  font=font, fill=255)
	#draw.text((x, top+8),     str(CPU), font=font, fill=255)
	#draw.text((x, top+16),    str(MemUsage),  font=font, fill=255)
	#draw.text((x, top+25),    str(Disk),  font=font, fill=255)
	
	# draw.text((x, top),"AQI: " + srt(rxData),  font=font, fill=255)

	response = requests.get('https://api.thingspeak.com/channels/898510/feeds.json')
	data = response.json()
	
	#parse JSON
	chanData = data['channel']
	lastEntryID = chanData['last_entry_id']
	fieldData = data['feeds']
	lastFieldData = fieldData[(len(fieldData)-1)]
	#field1Data = lastFieldData['field1'] #'PMT2.5[μm/m3]'
	field2Data = lastFieldData['field2'] #'PMT2.5[AQI-Index]'
	#field3Data = lastFieldData['field3'] #'PMT10[μm/m3]'
	field4Data = lastFieldData['field4'] #'PMT10[AQI-Index]'
	timefield = str(lastFieldData['created_at'])

	#datetime.fromisoformat('2019-12-29T19:15:26Z'[0:19])

	lastTime = datetime_from_utc_to_local(datetime.fromisoformat(timefield[0:19]))
	
	draw.text((x, top),"AQI2.5: " + str(field2Data),  font=font, fill=255)
	draw.text((x, top+8),"AQI10: " + str(field4Data),  font=font, fill=255)
	draw.text((x, top+16),str(lastTime),  font=font, fill=255)
	#print("AQI2.5: " + str(field2Data))
	#print("AQI10: " + str(field4Data))
	#print("time: " + str(lastTime))
	

	# Display image.
	disp.image(image)
	disp.display()
	time.sleep(2)
