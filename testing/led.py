import RPi.GPIO as GPIO # Import Raspberry Pi GPIO library
from time import sleep # Import the sleep function from the time module
GPIO.setwarnings(False) # Ignore warning for now
GPIO.setmode(GPIO.BOARD) # Use physical pin numbering
GPIO.setup(10, GPIO.OUT, initial=GPIO.LOW) # 10, 29
while True: # Run forever
    GPIO.output(10, GPIO.HIGH) # Turn on
    sleep(1) # Sleep for 1 second
    GPIO.output(10, GPIO.LOW) # Turn off
    sleep(1) # Sleep for 1 second