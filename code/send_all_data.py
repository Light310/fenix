import logging
import threading
import time
import random
import socket
import json
import math
import sys

from modules.adc import ADC
from modules.led import LED
from modules.mpu6050 import mpu6050
from modules.cpu_temp import measure_temp


def send_data():
    HOST = '78.46.205.128'
    PORT = 60000
    time.sleep(0.5)

    while True:
        #print(adc.read_voltage_rpi(), adc.read_voltage_servos_normalized(), mpu.get_angles(), measure_temp())
        #time.sleep(0.5)
        
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.connect((HOST, PORT))
                while True:
                    mpu_angles = mpu.get_angles()
                    d = {'v_rpi': adc.read_voltage_rpi(), 
                         'v_srv': adc.read_voltage_servos_normalized(),
                         'x': mpu_angles[0],
                         'y': mpu_angles[1],
                         'z': mpu_angles[2],
                         'cpu': measure_temp()}
                    data = json.dumps(d).encode()
                    s.sendall(data)
                    time.sleep(0.2)
        except:
            time.sleep(1.0)
            logging.info('Socket offline. Sleeping 1 sec')
        


logging.basicConfig(format="%(asctime)s.%(msecs)03d: %(message)s", level=logging.INFO, datefmt="%H:%M:%S")
#logging.info('Starting indication.')

adc = ADC()
mpu = mpu6050()

m = threading.Thread(target=mpu.run_complementary_filter)
q = threading.Thread(target=send_data)

q.start()
m.start()

q.join()
m.join()
