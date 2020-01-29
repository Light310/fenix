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
from calibration import calibrate

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

def read_calibration_dict():    
    with open ('/fenix/wrk/calibration_dict.txt', 'r') as f:
        contents = [x.strip().split(',') for x in f.readlines()]

    for k, v in enumerate(contents):
        contents[k] = [int(x) for x in v]

    return contents

while True:
    # for i in range (1, 2):
    try:
        try:
            with open('/fenix/wrk/servos.txt') as f:
                servo_data = [float(s) for s in f.read().split(',')]
            f.closed

            calibration_dict = read_calibration_dict()

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
