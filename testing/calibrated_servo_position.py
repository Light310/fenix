#!/usr/bin/env python

# servo_demo.py
# 2016-10-07
# Public Domain

# servo_demo.py          # Send servo pulses to GPIO 4.
# servo_demo.py 23 24 25 # Send servo pulses to GPIO 23, 24, 25.

import sys
import time
import random
import pigpio

calibration_dict = [
    [183, 95],
    [175, 89],
    [183, 94],
    [141, 90],
    [178, 95],
    [177, 90],
    [187, 95],
    [138, 94],
    [182, 95],
    [182, 90],
    [177, 99],
    [129, 92],
    [192, 95],
    [182, 95],
    [185, 93],
    [135, 90]
]


def calibrate(i, input_value):
    #print('input : {0}, i : {1}, input_value * calibration_dict[i][1]*1.0 / 90, {2} + calibration_dict[i][0] = {3}'.format(input_value, i, input_value * calibration_dict[i][1]*1.0 / 90, calibration_dict[i][0])) 
    return round(calibration_dict[i][0] + (input_value * calibration_dict[i][1]*1.0 / 90), 4)


output_seq = [None] * 16

NUM_GPIO = 32

MIN_WIDTH = 500
MAX_WIDTH = 2500
MAX_DIFF = 270  # angle 0 to 270
SLEEP_S = 0.035  # 6 ms for sleeping

step = [0] * NUM_GPIO
width = [0] * NUM_GPIO
used = [False] * NUM_GPIO

# s_dict = {10 : 0, 20 : 180, 25 : 90, 30 : 95}

servo_list = [4, 17, 27, 22, 18, 23, 24, 25, 6, 13, 19, 26, 12, 16, 20, 21]

# print ('Wtf : {0}'.format(s_dict))

pi = pigpio.pi()

if not pi.connected:
    exit()

while True:
    # for i in range (1, 2):
    try:
        try:
            with open('/nexus/fenix/wrk/servos.txt') as f:
                servo_data = [float(s) for s in f.read().split(',')]
            f.closed

            for i in range(0, len(servo_data)):
                output_seq[i] = calibrate(i, servo_data[i])
                # print('I : {0}. Data : {1}. Calibrated : {2}'.format(i, servo_data[i], output_seq[i]))

            for i in range(0, 16):
                pulse_width = int(MIN_WIDTH + (MAX_WIDTH - MIN_WIDTH) * output_seq[i] / MAX_DIFF)
                pi.set_servo_pulsewidth(servo_list[i], pulse_width)
            #print('Initial data : {0}'.format(servo_data))
            print('Calibrated data : {0}'.format(output_seq))
            #print('-----------------------')
        except:
            print("Unexpected error:", sys.exc_info()[0])
        time.sleep(SLEEP_S)

    except KeyboardInterrupt:
        break

print("\nTidying up")

pi.stop()
