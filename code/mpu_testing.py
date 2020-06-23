import smbus
from modules.mcp23017 import MCP23017
from modules.mpu6050_new import mpu6050
import time


gyro_calibration = {
    0  : [-105, 199, -184],
    1  : [-348, -113, 131],
    2  : [-406, 41, -39],
    3  : [-118, 307, 41],
    4  : [-77, -87, -483],
    5  : [55, 61, -41],
    6  : [-331, 51, 278],
    7  : [-316, 304, 227],
    8  : [-501, 204, -62],
    9  : [-164, -52, -707],
    10 : [-109, 110, -124],
    11 : [-166, 201, 4],
    12 : [-270, -905, 6]
}

accel_calibration = {
    0  : [1589.76, -1.99, -2447.02],
    1  : [807.61, 296.6, 881.99],
    2  : [10475.81, 271.38, 187.23],
    3  : [475.85, 72.36, 130.25],
    4  : [1613.6, -83.67, -352.14],
    5  : [12087.16, -35.59, -2052.18],
    6  : [-1.53, 51.99, -217.49],
    7  : [3039.0, 135.8, 402.79],
    8  : [627.59, -3.69, 2848.23],
    9  : [477.5, -460.0, -3647.0],
    10 : [1718.0, 111.71, -412.89],
    11 : [536.01, -5.97, -2090.6],
    12 : [-771.5, 594.58, 2592.4]
}

bus = smbus.SMBus(1)
mcp = MCP23017(bus)
#activation_pin = 0
#mcp.set_pin(activation_pin, 1)
# 0 

for pin_number in range(13):
    try: 
        print('============================')
        print('Pin : {0}'.format(pin_number))
        mcp.set_a_values(0b11111111)
        #print('1')
        mcp.set_b_values(0b11111111)
        #print('2')
                
        
        i = 0
        mpu = mpu6050(calibrate=False, 
                    mcp=mcp,
                    activation_pin=pin_number, 
                    gyro_offsets=gyro_calibration[pin_number],
                    accel_offsets=accel_calibration[pin_number])

        for i in range(100):
            #print(mpu.filter_step())            
            mpu.filter_step()
            time.sleep(0.01)
            #mpu.deactivate()
        print('Pin {0} Ok'.format(pin_number))
    except Exception as e:
        print('Pin {0} failed after {1} iterations'.format(pin_number, i))
        #print(str(e))
