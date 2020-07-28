import vlc
import random
from time import sleep # Import the sleep function from the time module

while True:
    x = random.randint(1,10)
    song = '/home/pi/Handwashing_Timer_Display/music/' + str(x) + '.mp3'
    media = vlc.MediaPlayer(song)
    media.play()
    sleep(25) # Pause for 5 seconds between songs
