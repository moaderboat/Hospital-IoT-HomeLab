from sense_hat import SenseHat
import time

sense = SenseHat()

try:
    while True:
        temp = round(sense.get_temperature(), 1)
        sense.show_message(str(temp) + "C", scroll_speed=0.1)
        time.sleep(2)

except KeyboardInterrupt:
    sense.clear()
    print("\nStopped.")
