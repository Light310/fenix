#!/usr/bin/env python

import sys
import time
import pigpio
from calibration import calibrate
from mpu_thread import fenix_imus
import datetime

imus = fenix_imus()
imus.start()

""" 
servos
"""
output_seq = [None] * 3

NUM_GPIO = 32

MIN_WIDTH = 500
MAX_WIDTH = 2500
MAX_DIFF = 270  # angle 0 to 270
#SLEEP_S = 0.035  # 6 ms for sleeping
SLEEP_S = 0.01  # 6 ms for sleeping

servo_list = [17, 27, 22]

pi = pigpio.pi()

if not pi.connected:
    exit()

cur_servo = imus.real_angles

cur_servo[2] = round(cur_servo[2] - cur_servo[1], 2)
cur_servo[1] = round(cur_servo[1] - cur_servo[0], 2)

angle_step = 3

while True:
    try:
        #try:
            # Get desired servo angles from file
            try:
                with open('/fenix/tmp/servos4.txt') as f:
                    servo_data = [float(s) for s in f.read().split(',')]
            except ValueError:
                print('Exception. Servo Data : {0}'.format(servo_data))
            
            # for testing w/o adjustment
            #servo_data_init = servo_data[:]

            mpu_angles = imus.real_angles

            # Calculate each servo target data according to real values of previous joint
            print('Target Angles before : {0}'.format(servo_data))
            servo_data[2] = round(servo_data[2] + mpu_angles[1], 2)
            servo_data[1] = round(servo_data[1] + mpu_angles[0], 2)
            # 1st joint is inverted
            #mpu_angles[1] = -1 * mpu_angles[1]
            print('Target Angles after : {0}'.format(servo_data))
            
            for idx in range(3):
                
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
            for i in range(0, 3):
                output_seq[i] = calibrate(i, cur_servo[i])
                #output_seq[i] = calibrate(i, servo_data_init[i])

            for i in range(0, 3):
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
