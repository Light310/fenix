#!/usr/bin/env python

import sys
import time
import pigpio
from modules.calibration import calibrate
from mpu_thread import fenix_imus
import datetime

imus = fenix_imus()
imus.start()

""" 
servos
"""
output_seq = [None] * 16

NUM_GPIO = 32

MIN_WIDTH = 500
MAX_WIDTH = 2500
MAX_DIFF = 270  # angle 0 to 270
#SLEEP_S = 0.035  # 6 ms for sleeping
SLEEP_S = 0.035 # 6 ms for sleeping

servo_list = [4, 17, 27, 22, 18, 23, 24, 25, 6, 13, 19, 26, 12, 16, 20, 21]

pi = pigpio.pi()

if not pi.connected:
    exit()

cur_servo = imus.get_leg_servo_angles()
 
angle_step = 3

while True:
    try:
        #try:
            # Get desired servo angles from file
            try:
                with open('/fenix/wrk/servos.txt') as f:
                    servo_data = [float(s) for s in f.read().split(',')]
            except ValueError:
                print('Exception. Servo Data : {0}'.format(servo_data))
            
            mpu_angles = imus.get_leg_servo_angles()
            
            for idx in range(16):
                if mpu_angles[idx] is None:
                    cur_servo[idx] = servo_data[idx]
                else:
                    # calculate diff between target and real
                    print('{0}. mpu angles : {1}. Target : {2}'.format(idx, mpu_angles[idx], servo_data[idx]))
                    diff = round(servo_data[idx] - mpu_angles[idx], 2)
                    print('Diff : {0}'.format(diff))
                    print('Target data before : {0}'.format(cur_servo[idx]))
                    # if diff is too small, ignore it
                    if abs(diff) < 1.0: # max(1, angle_step/2): 
                        continue

                    # if diff is not small, make a step towards target position
                    if abs(diff) < angle_step:
                        cur_servo[idx] += diff/4
                    elif abs(diff) < 3 * angle_step:
                        if diff > 0:
                            cur_servo[idx] += angle_step/2
                        else:
                            cur_servo[idx] -= angle_step/2
                    else:                    
                        if diff > 0:
                            cur_servo[idx] += angle_step
                        else:
                            cur_servo[idx] -= angle_step
                    
                    cur_servo[idx] = round(cur_servo[idx], 2)
                    print('Target data after  : {0}'.format(cur_servo[idx]))
                
            # calibrate new data according to different starting points.  
            for i in range(16):
                output_seq[i] = calibrate(i, cur_servo[i])
                #output_seq[i] = calibrate(i, servo_data_init[i])

            for i in range(16):
                pulse_width = int(MIN_WIDTH + (MAX_WIDTH - MIN_WIDTH) * output_seq[i] / MAX_DIFF)
                pi.set_servo_pulsewidth(servo_list[i], pulse_width)
            print('Calibrated     Data : {0}'.format(output_seq))
            print('Initial Servo  Data : {0}'.format(servo_data))
            print('Adjusted Servo Data : {0}'.format(cur_servo))

            print('-----------------------')
        #except:
        #    print("Unexpected error:", sys.exc_info()[0])

            time.sleep(SLEEP_S)

    except KeyboardInterrupt:        
        break

print("\nTidying up")

imus.stop()
pi.stop()