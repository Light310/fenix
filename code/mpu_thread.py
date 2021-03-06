import threading
from modules.mpu6050_new import mpu6050
import smbus
from modules.mcp23017 import MCP23017
import time

# class, which accepts an array of IMUs, and in cycle reads their data
# can return values on any of them

# calibration values

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
    12 : [-270, -905, 6],
    13 : [0, 0, 0],
    14 : [-426, -2339, 9]
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
    12 : [-771.5, 594.58, 2592.4],
    13 : [0, 0, 0],
    14 : [5705.5, 77.5, 2356.0]
}



class fenix_imus(threading.Thread):

    def __init__(self):
        bus = smbus.SMBus(1)
        mcp = MCP23017(bus)
        self.imus = []
        # set all to 0x69
        # crunch while not working correct initialization
        # setting all high (off) by default
        #mcp.set_a_values(0b11111111)
        #mcp.set_b_values(0b11111111)

        for pin_number in [0, 4, 5, 6, 14]:
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
    
    @staticmethod
    def convert_mpus_to_servos(mpu_angles):
        # accepts array of 4 mpu angles and returns 3 real servo values
        servos = [0, 0, 0]
        for i in range(3):
            servos[i] = round(mpu_angles[i+1] - mpu_angles[i], 2)

        # changing order to correspond to servos order
        servos[0], servos[2] = servos[2], servos[0]
        return servos

    def get_leg_servo_angles(self):
        # returns 4 arrays of angles, each for the corresponding leg
        angles = self.real_angles
        leg_2_angles = self.convert_mpus_to_servos([angles[4], angles[1], angles[2], angles[3]])
        return [None, None, None, None,
                *leg_2_angles,    None, 
                None, None, None, None,
                None, None, None, None]

    
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


"""
# example usage
imus = fenix_imus()
imus.start()
import time
import datetime
print('Start : {0}'.format(datetime.datetime.now()))
while True:
    #print('mpus : {0}'.format(imus.real_angles))
    print('Servos : {0}'.format(imus.get_leg_servo_angles()))
    #print('planes: {0}'.format([round(joint1, 2), round(joint2, 2), round(joint3, 2)]))
    print('----------------------------------')
    time.sleep(0.1)
print('End : {0}'.format(datetime.datetime.now()))
imus.stop()
"""