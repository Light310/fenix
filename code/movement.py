import logging
import threading
import requests
import sys
import time
import argparse
import os
import pigpio
from os import listdir
from os.path import isfile, join
from modules.calibration import calibrate

wrk_path = '/fenix/tmp/'
sequence_path = '/fenix/static/sequences/'

command_file = f'{wrk_path}command.txt'
speed_file = f'{wrk_path}speed.txt'
log_file = f'{wrk_path}movement.log'

MIN_WIDTH = 500
MAX_WIDTH = 2500
MAX_DIFF = 270  # angle 0 to 270
servo_signal_sleep = 0.035
servo_list = [4, 17, 27, 22, 18, 23, 24, 25, 6, 13, 19, 26, 12, 16, 20, 21]
sequence_sleep_time = 0.035
fixed_sequence_sleep_time = 0.01
global stop_thread
stop_thread = False


def load_sequences(sequence_path):    
    sequence_files = [f for f in listdir(sequence_path) if isfile(join(sequence_path, f))]
    sequence_dict = {}


    for item in sequence_files:
        with open(f'{sequence_path}{item}') as f:
            sequence = f.readlines()
        
        sequence = [eval(x) for x in sequence]
        sequence_dict[item.replace('.txt','')] = sequence[:]
    
    return sequence_dict


def read_command():
    r = requests.get('http://78.46.205.128/read_command')
    print(r.json()['data'])
    return r.json()['data']
    #with open(command_file, 'r') as f:
    #    command = f.readline()
    #return command


class FenixServos(threading.Thread):
    def __init__(self):
        self.pi = pigpio.pi()
        if not self.pi.connected:
            exit()

        threading.Thread.__init__(self, daemon=True)
        self.start()

    def run(self):
        global stop_thread, servo_data
        time.sleep(sequence_sleep_time)
        while True:
            if 'servo_data' not in globals():
                logging.info('Servo_data not yet defined. Skipping')
                time.sleep(servo_signal_sleep)
                continue
            
            for i in range(16):
                calibrated_servo = calibrate(i, servo_data[i])
                pulse_width = int(MIN_WIDTH + (MAX_WIDTH - MIN_WIDTH) * calibrated_servo / MAX_DIFF)
                if pulse_width > 2500 or pulse_width < 500:
                    print(i, servo_data[i], pulse_width)
                self.pi.set_servo_pulsewidth(servo_list[i], pulse_width)
            if stop_thread:
                break
            time.sleep(servo_signal_sleep)

    def __del__(self):
        logging.info("Closing pigpio connection")
        self.pi.stop()


def read_speed():
    global stop_thread, sequence_sleep_time

    while True:        
        #with open(speed_file, 'r') as f:
        #    speed_value = int(f.readline())
        r = requests.get('http://78.46.205.128/get_speed')
        speed_value = int(r.json()['speed'])
        print(speed_value)

        sequence_sleep_time = round(0.01 + (100 - speed_value) * 0.005, 5)
        """
        tmp = round(0.0175 + (100 - speed_value) * 0.00875, 5)
        if abs(tmp - sequence_sleep_time) > 0.001:
            sequence_sleep_time = tmp
            logging.info(f'Speed changed to {speed_value}. Sleep time changed to {sequence_sleep_time}')
        """

        if stop_thread:
            break
        time.sleep(0.5)


def execute_sequence(sequence_name):
    global servo_data

    logging.info(f'Running sequence : {sequence_name}')
    sequence = sequence_dict[sequence_name]

    for servo_data in sequence:
        logging.info("Angles : {0}".format(servo_data))
        slow_movement = ['up', 'down', 'look']
        if any(x in sequence_name for x in slow_movement):
            time.sleep(fixed_sequence_sleep_time)
        else:
            time.sleep(sequence_sleep_time)

def get_sequence(command, state):
    grounds_z = [3, 10, 15, 20]

    if state == 0 and command != 'up':
        return None, state

    if command == 'up':
        if state == 3:
            return None, state
        else:
            return f'sq_{command}_{grounds_z[state]}_{grounds_z[state+1]}', state + 1
    elif command == 'down':
        if state == 0:
            return None, state
        else:
            return f'sq_{command}_{grounds_z[state]}_{grounds_z[state-1]}', state - 1

    if command == 'exit':
        return f'sq_down_{grounds_z[state]}_{grounds_z[0]}', 0
    
    return f'sq_{command}_{grounds_z[state]}', state
			

def run_command():
    global stop_thread

    time.sleep(1.0)

    command = 'None'
    state = 0
    while command != 'exit':
        command = read_command()
        try:
            sq_name, state = get_sequence(command, state)
            sequence_dict[sq_name]
        except KeyError as e:
            print(f'Got unexpected value : {e}')
            sq_name = None

        print(sq_name, state)

        if sq_name is None:
            time.sleep(0.5)
            continue
            
        execute_sequence(sq_name)
    
    stop_thread = True   


if __name__ == "__main__":

    logging.basicConfig(format="%(asctime)s.%(msecs)05d: %(message)s",
                        level=logging.INFO,
                        datefmt="%H:%M:%S",
                        filename=log_file)
    global sequence_dict
    sequence_dict = load_sequences(sequence_path)

    logging.info('Starting movement.')
    try:
        os.system("sudo pigpiod")
        time.sleep(1.0)
    except Exception as e:
        print('Exception : ', e)
    try:                
        servos_thread = FenixServos()
        x = threading.Thread(target=run_command)
        x.start()

        y = threading.Thread(target=read_speed)
        y.start()

        x.join()
        y.join()

        servos_thread.join()
    finally:
        del servos_thread
        #os.system("sudo killall pigpiod")
        logging.info('Movement complete')