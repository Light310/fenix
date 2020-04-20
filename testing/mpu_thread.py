import threading
from mpu6050_new import mpu6050
import smbus
from mcp23017 import MCP23017

# class, which accepts an array of IMUs, and in cycle reads their data
# can return values on any of them

# calibration values

"""
gyro_calibration = {
    6 : [-426, -2339, 9],
    13 : [-316, 304, 227],
    19 : [-501, 204, -62],
    26 : [-164, -52, -707]
}

accel_calibration = {
    6 : [5705.5, 77.5, 2356.0],
    13 : [3039.0, 135.8, 402.79],
    19 : [627.59, -3.69, 2848.23],
    26 : [477.5, -460.0, -3647.0]
}
"""
gyro_calibration = {
    0 : [-316, 304, 227],
    1 : [-501, 204, -62],
    2 : [-164, -52, -707]
}

accel_calibration = {
    0 : [3039.0, 135.8, 402.79],
    1 : [627.59, -3.69, 2848.23],
    2 : [477.5, -460.0, -3647.0]
}



class fenix_imus(threading.Thread):

    def __init__(self):
        bus = smbus.SMBus(1)
        mcp = MCP23017(bus)
        self.imus = []
        # set all to 0x69
        for pin_number in [0, 1, 2]:
        #for pin_number in [6, 13, 19, 26, 6, 13, 19, 26, 6, 13, 19, 26]:
            self.imus.append(mpu6050(calibrate=False, 
                                mcp=mcp,
                                activation_pin=pin_number, 
                                gyro_offsets=gyro_calibration[pin_number],
                                accel_offsets=accel_calibration[pin_number]))

        self.angles = [[0, 0, 0] for _ in self.imus]

        self.terminated = False
        self.toTerminate = False

    @property
    def real_angles(self):
        r_angles = []
        for item in self.angles:
            r_angles.append(self.calculate_real_angle(item[0], item[2]))
        return r_angles


    def imu_data(self, id):
        # returns the angles from an imu with index = id
        return self.angles[id]
    
    @staticmethod
    def calculate_real_angle(angle_x, angle_z):
        # calculates real angle of an IMU
        if abs(angle_z) < 90 and abs(angle_x) < 45:
            return -angle_x

        angle = angle_z
        
        if angle_x > 0:
            angle *= -1
        return round(angle, 2)

    def get_real_angle(self, id):
        angles = self.imu_data(id)
        return self.calculate_real_angle(angles[0], angles[2])
    
    def start(self):
        self.thread = threading.Thread(None, self.run, None, (), {})
        self.thread.start()
        
    def run(self):
        while self.toTerminate == False:  
            # read IMUs raw data and apply complementary steps
            for index in range(len(self.imus)):
                self.angles[index] = self.imus[index].filter_step()[:]

        self.terminated = True

    def stop(self):
        # Stops reading IMUs
        self.toTerminate = True
        while self.terminated == False:
            # wait for termination
            time.sleep(0.01)

    def __del__(self):
        self.stop()

# example usage
"""
imus = fenix_imus()
imus.start()

import time
import datetime

print('Start : {0}'.format(datetime.datetime.now()))

for i in range(100):
    print('{0} : {1}'.format(datetime.datetime.now(), imus.real_angles))

    time.sleep(0.01)

print('End : {0}'.format(datetime.datetime.now()))

imus.stop()
"""