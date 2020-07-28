#! /usr/bin/python

# Imports
import RPi.GPIO as GPIO
#GPIO.setmode(GPIO.BOARD)   # Use physical pin numbering
import time
import requests
import vlc
import random
import math
from time import sleep # Import the sleep function from the time module

# Define GPIO to LCD mapping
LCD_RS = 26
LCD_E  = 19
LCD_D4 = 13
LCD_D5 = 6
LCD_D6 = 5
LCD_D7 = 11
LED_ON = 15

# Define some device constants
LCD_WIDTH = 16    # Maximum characters per line
LCD_CHR = True
LCD_CMD = False

LCD_LINE_1 = 0x80 # LCD RAM address for the 1st line
LCD_LINE_2 = 0xC0 # LCD RAM address for the 2nd line

# Timing constants
E_PULSE = 0.0005
E_DELAY = 0.0005

# Set the GPIO naming convention
GPIO.setmode(GPIO.BCM)

# Turn off GPIO warnings
GPIO.setwarnings(False)

#SetGPIO pins for LED screen output
GPIO.setup(LCD_E, GPIO.OUT)  # E
GPIO.setup(LCD_RS, GPIO.OUT) # RS
GPIO.setup(LCD_D4, GPIO.OUT) # DB4
GPIO.setup(LCD_D5, GPIO.OUT) # DB5
GPIO.setup(LCD_D6, GPIO.OUT) # DB6
GPIO.setup(LCD_D7, GPIO.OUT) # DB7

#ultrasonic sensor
GPIO_TRIGGER = 18
GPIO_ECHO = 24
dist_trig = 7 # distance in inches to trigger the handwashing timer

#set GPIO direction (IN / OUT) for ultrasonic sensor
GPIO.setup(GPIO_TRIGGER, GPIO.OUT)
GPIO.setup(GPIO_ECHO, GPIO.IN)

# Set GPIO pin as output
#GPIO.setup(pinled, GPIO.OUT, initial=GPIO.LOW)

def main():
  # Main program block
  # Variables to hold the current and last states
	currentstate = 0
	previousstate = 0

#	GPIO.setwarnings(False)
#	GPIO.setmode(GPIO.BCM)       # Use BCM GPIO numbers


  # Intitialize display
	print("Initializing")
	lcd_init()
	lcd_string("Initializing",LCD_LINE_1)
	lcd_string("Sensor",LCD_LINE_2)
	time.sleep(1)
	dist = distance()

	# Loop until distance < dist_trig
	while dist >dist_trig:
	  currentstate = 0
	  print("    Ready")
	  dist = distance()
	  print ("Measured Distance = %.1f in" % dist)
	  lcd_init()
	  lcd_string("Distance = ",LCD_LINE_1)
	  display = str(dist)
	  display1 = display + " in"
	  lcd_string(display1,LCD_LINE_2)
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
				lcd_init()
				lcd_string("Wash your hands",LCD_LINE_1)
				display = str(sleft)
				display1 = 'for ' + display + " more sec"
				lcd_string(display1,LCD_LINE_2)
				time.sleep(1)
				if sleft == 1:
					break
				sleft -=1
			else:
			  time.sleep(1) # 1 second delay

    # Send text
			lcd_string("All Clean!",LCD_LINE_1)
			lcd_string("Great Job!",LCD_LINE_2)
			time.sleep(3) # 3 second delay
			currentstate = 0
			previousstate = 1
			#Wait 30 seconds before looping again
			print("Waiting 5 seconds")
			time.sleep(5)
			dist = distance()
			print ("Measured Distance = %.1f in" % dist)

		# When the sensor is ready again
		elif currentstate == 0 and previousstate == 1:

			print("Ready")
			dist = distance()
			print ("Measured Distance = %.1f in" % dist)
			lcd_init()
			lcd_string("Ready for",LCD_LINE_1)
			lcd_string("Motion",LCD_LINE_2)
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

def lcd_init():
  # Initialize display
  lcd_byte(0x33,LCD_CMD) # 110011 Initialize
  lcd_byte(0x32,LCD_CMD) # 110010 Initialize
  lcd_byte(0x06,LCD_CMD) # 000110 Cursor move direction
  lcd_byte(0x0C,LCD_CMD) # 001100 Display On,Cursor Off, Blink Off
  lcd_byte(0x28,LCD_CMD) # 101000 Data length, number of lines, font size
  lcd_byte(0x01,LCD_CMD) # 000001 Clear display
  time.sleep(E_DELAY)

def lcd_byte(bits, mode):
  # Send byte to data pins
  # bits = data
  # mode = True  for character
  #        False for command

  GPIO.output(LCD_RS, mode) # RS

  # High bits
  GPIO.output(LCD_D4, False)
  GPIO.output(LCD_D5, False)
  GPIO.output(LCD_D6, False)
  GPIO.output(LCD_D7, False)
  if bits&0x10==0x10:
    GPIO.output(LCD_D4, True)
  if bits&0x20==0x20:
    GPIO.output(LCD_D5, True)
  if bits&0x40==0x40:
    GPIO.output(LCD_D6, True)
  if bits&0x80==0x80:
    GPIO.output(LCD_D7, True)

  # Toggle 'Enable' pin
  lcd_toggle_enable()

  # Low bits
  GPIO.output(LCD_D4, False)
  GPIO.output(LCD_D5, False)
  GPIO.output(LCD_D6, False)
  GPIO.output(LCD_D7, False)
  if bits&0x01==0x01:
    GPIO.output(LCD_D4, True)
  if bits&0x02==0x02:
    GPIO.output(LCD_D5, True)
  if bits&0x04==0x04:
    GPIO.output(LCD_D6, True)
  if bits&0x08==0x08:
    GPIO.output(LCD_D7, True)

  # Toggle 'Enable' pin
  lcd_toggle_enable()

def lcd_toggle_enable():
  # Toggle enable
  time.sleep(E_DELAY)
  GPIO.output(LCD_E, True)
  time.sleep(E_PULSE)
  GPIO.output(LCD_E, False)
  time.sleep(E_DELAY)

def lcd_string(message,line):
  # Send string to display

  message = message.ljust(LCD_WIDTH," ")

  lcd_byte(line, LCD_CMD)

  for i in range(LCD_WIDTH):
    lcd_byte(ord(message[i]),LCD_CHR)

if __name__ == '__main__':

	try:
		main()
	except KeyboardInterrupt:
		pass
	finally:
		lcd_byte(0x01, LCD_CMD)
		lcd_string("Program not",LCD_LINE_1)
		lcd_string("running",LCD_LINE_2)
		GPIO.cleanup()
