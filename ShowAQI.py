import time
import Adafruit_GPIO.SPI as SPI
import Adafruit_SSD1306
import paho.mqtt.publish as publish
import requests
import aqi
import psutil
from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont
from datetime import datetime
from sds011 import *



#
#local function definitions
#

def datetime_from_utc_to_local(utc_datetime):
	now_timestamp = time.time()
	offset = datetime.fromtimestamp(now_timestamp) - datetime.utcfromtimestamp(now_timestamp)
	return utc_datetime + offset
	
def get_data(n=3):
	sensor.sleep(sleep=False)
	pmt_2_5 = 0
	pmt_10 = 0
	time.sleep(10)
	for i in range (n):
		x = sensor.query()
		pmt_2_5 = pmt_2_5 + x[0]
		pmt_10 = pmt_10 + x[1]
		time.sleep(2)
	pmt_2_5 = round(pmt_2_5/n, 1)
	pmt_10 = round(pmt_10/n, 1)
	sensor.sleep(sleep=True)
	time.sleep(2)
	return pmt_2_5, pmt_10
	
def conv_aqi(pmt_2_5, pmt_10):
	aqi_2_5 = aqi.to_iaqi(aqi.POLLUTANT_PM25, str(pmt_2_5))
	aqi_10 = aqi.to_iaqi(aqi.POLLUTANT_PM10, str(pmt_10))
	return aqi_2_5, aqi_10

def save_log():        
	with open("air_quality.csv", "a") as log:
		dt = datetime.now()
		log.write("{},{},{},{},{}\n".format(dt, pmt_2_5, aqi_2_5, pmt_10, aqi_10))
	log.close()

#
# setup air sensor & IOT comms
#	

#init air sensor from USB port
sensor = SDS011("/dev/ttyUSB0", use_query_mode=True)

#thinkspeak constants
channelID = '898510'
apiKey = '5EG4SZ384VG3RK6I' #write key
topic = "channels/" + channelID + "/publish/" + apiKey
mqttHost = "mqtt.thingspeak.com"
tTransport = "tcp"
tPort = 1883
tTLS = None	

#field names in thingspeak
field1Name = 'PMT2.5[μm/m3]'
field2Name = 'PMT2.5[AQI-Index]'
field3Name = 'PMT10[μm/m3]'
field4Name = 'PMT10[AQI-Index]'

#
# setup OLED display & I2C bus
#
	
# Raspberry Pi pin configuration:
RST = None     # on the PiOLED this pin isnt used
# Note the following are only used with SPI:
DC = 23
SPI_PORT = 0
SPI_DEVICE = 0

# 128x32 display with hardware I2C:
#disp = Adafruit_SSD1306.SSD1306_128_32(rst=RST)

# 128x64 display with hardware I2C:
disp = Adafruit_SSD1306.SSD1306_128_64(rst=RST)

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
#font = ImageFont.load_default()




while True:

	#
	# get sample from air sensor and format payload for sending
	#
	
	pmt_2_5, pmt_10 = get_data()
	
	try:
		aqi_2_5, aqi_10 = conv_aqi(pmt_2_5, pmt_10)
	except:
		print("unhandled error occured")
		
	field2Data = aqi_2_5
	field4Data = aqi_10
	tPayload = "field1=" + str(pmt_2_5)+ "&field2=" + str(aqi_2_5)+ "&field3=" + str(pmt_10)+ "&field4=" + str(aqi_10)
	lastTime = time.strftime('%X %x')
	#print(tPayload)


	# #RESTful call to get latest data from thingspeak (not needed when running local)
	
	# response = requests.get('https://api.thingspeak.com/channels/898510/feeds.json')
	# data = response.json()
	
	# #parse JSON
	# chanData = data['channel']
	# lastEntryID = chanData['last_entry_id']
	# fieldData = data['feeds']
	# lastFieldData = fieldData[(len(fieldData)-1)]
	# #field1Data = lastFieldData['field1'] #'PMT2.5[μm/m3]'
	# field2Data = lastFieldData['field2'] #'PMT2.5[AQI-Index]'
	# #field3Data = lastFieldData['field3'] #'PMT10[μm/m3]'
	# field4Data = lastFieldData['field4'] #'PMT10[AQI-Index]'
	# timefield = str(lastFieldData['created_at'])

	# #convert UTC ISO to local time
	# lastTime = datetime_from_utc_to_local(datetime.fromisoformat(timefield[0:19]))
	
	#
	# update OLED screen
	#
	
	# Draw a black filled box to clear the image.
	draw.rectangle((0,0,width,height), outline=0, fill=0)
	
	font = ImageFont.truetype('VCR_OSD_MONO.ttf', 40)
	draw.text((x, top),str(field2Data) + "," + str(field4Data),  font=font, fill=255)
	
	font = ImageFont.truetype('VCR_OSD_MONO.ttf', 12)
	draw.text((x, top+40),"2.5AQI,10AQI",  font=font, fill=255)
	
	font = ImageFont.truetype('VCR_OSD_MONO.ttf', 12)
	draw.text((x, top+52),str(lastTime),  font=font, fill=255)
	
	print("AQI2.5: " + str(field2Data))
	print("AQI10: " + str(field4Data))
	print("time: " + str(lastTime))
	

	# Display image.
	disp.image(image)
	disp.display()
	time.sleep(.1)
	
	try:
		publish.single(topic, payload=tPayload, hostname=mqttHost, port=tPort, tls=tTLS, transport=tTransport)
		#save_log()
		print("[INFO] Publishing...")
		time.sleep(60)
	except:
		print ("[INFO] Failure in sending data")
		time.sleep(12)
