#! /usr/bin/python

# Imports
import i2c_lcd_driver
import RPi.GPIO as GPIO
import time
import requests
import vlc
import random
import math
from time import sleep # Import the sleep function from the time module

# Timing constants
E_PULSE = 0.0005
E_DELAY = 0.0005

# Set the GPIO naming convention
GPIO.setmode(GPIO.BCM)

# Turn off GPIO warnings
GPIO.setwarnings(False)

#ultrasonic sensor
GPIO_TRIGGER = 18
GPIO_ECHO = 24
dist_trig = 7 # distance in inches to trigger the handwashing timer

#set GPIO direction (IN / OUT) for ultrasonic sensor
GPIO.setup(GPIO_TRIGGER, GPIO.OUT)
GPIO.setup(GPIO_ECHO, GPIO.IN)

#define mylcd
mylcd = i2c_lcd_driver.lcd()

def main():
  # Main program block
  # Variables to hold the current and last states
	currentstate = 0
	previousstate = 0

  # Intitialize display
	print("Initializing")
	mylcd.lcd_display_string("Initializing", 1)
	mylcd.lcd_display_string("Sensor", 2)
	time.sleep(1)
	dist = distance()

	# Loop until distance < dist_trig
	while dist >dist_trig:
	  currentstate = 0
	  print("    Ready")
	  dist = distance()
	  print ("Measured Distance = %.1f in" % dist)
	  mylcd.lcd_display_string("Distance", 1)
	  display = str(dist)
	  display1 = display + " in"
	  mylcd.lcd_display_string(display1, 2)
	  time.sleep(.05)

	# Loop until users quits with CTRL-C
	while True:

		# Read current distance
		dist = distance()
		print ("Measured Distance = %.1f in" % dist)
		if dist < dist_trig:
		  currentstate = 1

		# If the hand sensed
		if currentstate == 1 and previousstate == 0:

			print("Motion detected!")
		#Generate a Random Integer
			x = random.randint(1,10)
			song = '/home/pi/Handwashing_Timer_Display/music/'+ str(x) +'.mp3'
		# VLC player on motion
			media = vlc.MediaPlayer(song)
			media.play()
		# Initialize display
			sleft = 19

			while sleft > 0:
				mylcd.lcd_clear()
				mylcd.lcd_display_string("Wash your hands", 1)
				display = str(sleft)
				display1 = 'for ' + display + " more sec"
				mylcd.lcd_display_string(display1, 2)
				time.sleep(1)
				if sleft == 1:
					break
				sleft -=1
			else:
			  time.sleep(1) # 1 second delay

		    # Send finish text to lcd display
			mylcd.lcd_clear()
			mylcd.lcd_display_string("All Clean!", 1)
			mylcd.lcd_display_string("Great Job!", 2)
			time.sleep(3) # 3 second delay
			currentstate = 0
			previousstate = 1
			#Wait 5 seconds before looping again
			print("Waiting 5 seconds")
			time.sleep(5)
			dist = distance()
			print ("Measured Distance = %.1f in" % dist)

		# When the sensor is ready again
		elif currentstate == 0 and previousstate == 1:

			print("Ready")
			dist = distance()
			print ("Measured Distance = %.1f in" % dist)
			mylcd.lcd_clear()
			mylcd.lcd_display_string("Ready for", 1)
			mylcd.lcd_display_string("Motion", 2)
			time.sleep(.05)
			previousstate = 0

		# Wait for 10 milliseconds
		time.sleep(0.1)

def distance():
    # set Trigger to HIGH
    GPIO.output(GPIO_TRIGGER, True)

    # set Trigger after 0.01ms to LOW
    time.sleep(0.00001)
    GPIO.output(GPIO_TRIGGER, False)

    StartTime = time.time()
    StopTime = time.time()

    # save StartTime
    while GPIO.input(GPIO_ECHO) == 0:
        StartTime = time.time()

    # save time of arrival
    while GPIO.input(GPIO_ECHO) == 1:
        StopTime = time.time()

    # time difference between start and arrival
    TimeElapsed = StopTime - StartTime
    # multiply with the sonic speed (34300 cm/s)
    # and divide by 2, because there and back
    #distance = (TimeElapsed * 34300) / 2  #distance in cm
    distance = ((TimeElapsed * 34300) / 2) * 0.393701 #dist in inches
    distance = round(distance,2)

    return distance


if __name__ == '__main__':

	try:
		main()
	except KeyboardInterrupt:
		pass
	finally:
		mylcd.lcd_clear()
		mylcd.lcd_display_string("Program not", 1)
		mylcd.lcd_display_string("running", 2)
		GPIO.cleanup()
