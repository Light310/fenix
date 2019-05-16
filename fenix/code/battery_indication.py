# Simple example of reading the MCP3008 analog input channels and printing
# them all out.
# Author: Tony DiCola
# License: Public Domain
import time

# Import SPI library (for hardware SPI) and MCP3008 library.
import Adafruit_GPIO.SPI as SPI
import Adafruit_MCP3008

import RPi.GPIO as GPIO # Import Raspberry Pi GPIO library

GPIO.setwarnings(False) # Ignore warning for now
GPIO.setmode(GPIO.BOARD) # Use physical pin numbering
GPIO.setup(29, GPIO.OUT, initial=GPIO.LOW) # Set pin 8 to be an output pin and set initial value to low (off)

def convert_to_voltage(adc_value):
    return round(3.3*adc_value/1024, 2)


def single_battery_voltage(adc_value):
    return round(1.5*convert_to_voltage(adc_value),2)

# Hardware SPI configuration:
SPI_PORT   = 0
SPI_DEVICE = 0
mcp = Adafruit_MCP3008.MCP3008(spi=SPI.SpiDev(SPI_PORT, SPI_DEVICE))


# Main program loop.
while True:
    # Read all the ADC channel values in a list.
    values = [0]*8
    for i in range(8):
        # The read_adc function will get the value of the specified channel (0-7).
        values[i] = mcp.read_adc(i)
    rpi_battery_voltage = single_battery_voltage(values[0])
    print(f'rpi_battery_voltage : {rpi_battery_voltage}')
    sleep_time = 3 * (rpi_battery_voltage - 3.3)
    GPIO.output(29, GPIO.HIGH) # Turn on        
    time.sleep(sleep_time)
    GPIO.output(29, GPIO.LOW) # Turn off
    time.sleep(sleep_time)