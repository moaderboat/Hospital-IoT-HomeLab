import time
from sense_hat import SenseHat

sense = SenseHat()

while True:
	sense.show_letter("1")
	sense.low_light = False
	time.sleep(.12)
	sense.low_light = True
	time.sleep(.18)
	sense.low_light = False
	time.sleep(.05)
	sense.low_light = True
	time.sleep(.62)
