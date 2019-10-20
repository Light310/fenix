import RPi.GPIO as GPIO
import time


class LED:
    def __init__(self, pin):
        self.pin = pin
        GPIO.setwarnings(False) # Ignore warning for now
        GPIO.setmode(GPIO.BOARD) # Use physical pin numbering
        GPIO.setup(pin, GPIO.OUT, initial=GPIO.LOW) # Set pin to be an output pin and set initial value to low (off)
        time.sleep(1.0)
        GPIO.output(self.pin, GPIO.HIGH) # Turn on

    def blink(self):
        GPIO.output(self.pin, GPIO.LOW)  # Turn off
        time.sleep(0.125)
        GPIO.output(self.pin, GPIO.HIGH) # Turn on
