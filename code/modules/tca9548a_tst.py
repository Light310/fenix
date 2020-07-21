import time
import board
import busio
import adafruit_tca9548a
from as5600 import as5600

# Create I2C bus as normal
i2c = busio.I2C(board.SCL, board.SDA)

# Create the TCA9548A object and give it the I2C bus
tca = adafruit_tca9548a.TCA9548A(i2c)

AS = as5600()

strengths = [0, 0, 0, 0]
angles = [0, 0, 0, 0]

while True:
    try:
        for i in range(4):
            tca.i2c.writeto(0x70, bytearray([1 << i]))

            strengths[i] = AS.get_magnet_strength()
            angles[i] = AS.get_real_angle()

        print(strengths, angles)
    except:
        print('Error')
    time.sleep(0.1)

    