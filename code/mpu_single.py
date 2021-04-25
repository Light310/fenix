from modules.mpu6050_new import mpu6050
import time


gyro_calibration = [326, -329, 136]
accel_calibration = [502.81, 230.21, -1009.7]

mpu = mpu6050(gyro_offsets=gyro_calibration, accel_offsets=accel_calibration)

while True:
    print(mpu.filter_step())
    time.sleep(0.01)
