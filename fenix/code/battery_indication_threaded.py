import logging
import threading
import time
import random

# Import SPI library (for hardware SPI) and MCP3008 library.
import Adafruit_GPIO.SPI as SPI
import Adafruit_MCP3008
import RPi.GPIO as GPIO # Import Raspberry Pi GPIO library


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


class ADC:
    def __init__(self):
        # Hardware SPI configuration:
        SPI_PORT = 0
        SPI_DEVICE = 0
        self.mcp = Adafruit_MCP3008.MCP3008(spi=SPI.SpiDev(SPI_PORT, SPI_DEVICE))

    @staticmethod
    def _convert_to_voltage(adc_value):
        return round(3.3 * adc_value / 1024, 2)

    def read_voltage_rpi(self):
        return round(1.5 * self._convert_to_voltage(self.read_values(channel=0)), 2)

    def read_voltage_servos_normalized(self):
        # normalizing to a single battery (3.3 - 4.2V), tho there are 2 batteries
        return round(1.5 * self._convert_to_voltage(self.read_values(channel=1)), 2)

    def read_values(self, channel=None):
        if channel is None:
            values = [0] * 8
            for i in range(8):
                # The read_adc function will get the value of the specified channel (0-7).
                values[i] = self.mcp.read_adc(i)
            return values
        else:
            return self.mcp.read_adc(channel)


voltages = [0]*2
pins = {0 : 29, 1 : 10}

def read_adc():
    adc = ADC()
    while True:
        voltages[0], voltages[1] = adc.read_voltage_rpi(), adc.read_voltage_servos_normalized()
        logging.info(voltages)
        time.sleep(1.0)


def led(channel):
    pin = pins[channel]
    led = LED(pin)
    while True:
        value = voltages[channel]
        logging.info(f'pin : {pin}, channel : {channel}, value : {value}')
        if value > 3.8:
            time.sleep(1.0)
            continue
        elif value > 3.7:
            time.sleep(2.875)
        elif value > 3.6:
            time.sleep(0.875)
        elif value > 3.5:
            time.sleep(0.375)
        else:
            time.sleep(0.125)
        led.blink()


logging.basicConfig(format="%(asctime)s.%(msecs)03d: %(message)s", level=logging.INFO, datefmt="%H:%M:%S")
logging.info('Starting indication.')


x = threading.Thread(target=read_adc)
y = threading.Thread(target=led, args=(0,))
z = threading.Thread(target=led, args=(1,))

x.start()
y.start()
z.start()

x.join()
y.join()
z.join()
