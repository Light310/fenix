import logging
import threading
import requests
import sys
import time
import argparse
import os
import pigpio

wrk_path = '/fenix/tmp/'
sequence_path = '/fenix/static/sequences/'
sequence_dict = {
    'Back': 'sq_backw_8',    
    'Forward': 'sq_forw_8',
    'LeftBackwards': 'sq_backw_left_5',
    'RightBackwards': 'sq_backw_right_5',
    'LeftForward': 'sq_forw_left_5',
    'RightForward': 'sq_forw_right_5',    
    'StrafeLeft': 'sq_strafe_left_8',
    'StrafeRight': 'sq_strafe_right_8',
    'TurnRight': 'sq_turn_cw_30',
    'TurnLeft': 'sq_turn_ccw_30',
    'Activate': 'sq_activation',
    'Deactivate': 'sq_deactivation'
}
"""
'LeftBackwards': 'look_down_3',
'RightBackwards': 'look_up_3',
'LeftForward': 'look_down_6',
'RightForward': 'look_up_6',
"""

command_file = f'{wrk_path}command.txt'
speed_file = f'{wrk_path}speed.txt'
log_file = f'{wrk_path}movement.log'

calibration_dict = [
    [183, 95], [175, 89], [183, 94], [141, 90],
    [178, 95], [177, 90], [187, 95], [138, 94],
    [182, 95], [182, 90], [177, 99], [129, 92],
    [197, 95], [187, 95], [185, 93], [135, 90]
]

MIN_WIDTH = 500
MAX_WIDTH = 2500
MAX_DIFF = 270  # angle 0 to 270
servo_signal_sleep = 0.035
servo_list = [4, 17, 27, 22, 18, 23, 24, 25, 6, 13, 19, 26, 12, 16, 20, 21]
sequence_sleep_time = 0.035
fixed_sequence_sleep_time = 0.035
global stop_thread
stop_thread = False


def load_sequences():
    for key, value in sequence_dict.items():
        with open(f'{sequence_path}{value}.txt') as f:
            sequence = f.readlines()
        sequence = [x.strip().replace('[', '').replace(']', '') for x in sequence]
        sequence_dict[key] = sequence[:]


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
            #calibrated_data = []
            for i in range(16):
                calibrated_servo = self.calibrate_servo(i, servo_data[i])
                pulse_width = int(MIN_WIDTH + (MAX_WIDTH - MIN_WIDTH) * calibrated_servo / MAX_DIFF)
                #pulse_width = max(min(pulse_width, MAX_WIDTH), MIN_WIDTH) # wtf?
                self.pi.set_servo_pulsewidth(servo_list[i], pulse_width)
                #calibrated_data.append(calibrated_servo)
            #logging.info('Initial    data : {0}'.format(servo_data))
            #logging.info('Calibrated data : {0}'.format(calibrated_data))
            if stop_thread:
                break
            time.sleep(servo_signal_sleep)

    @staticmethod
    def calibrate_servo(i, input_value):
        return round(calibration_dict[i][0] + (input_value * calibration_dict[i][1] * 1.0 / 90), 4)

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

        sequence_sleep_time = round(0.0175 + (100 - speed_value) * 0.00875, 5)
        """
        tmp = round(0.0175 + (100 - speed_value) * 0.00875, 5)
        if abs(tmp - sequence_sleep_time) > 0.001:
            sequence_sleep_time = tmp
            logging.info(f'Speed changed to {speed_value}. Sleep time changed to {sequence_sleep_time}')
        """

        if stop_thread:
            break
        time.sleep(0.5)


def execute_sequence(command):
    global servo_data

    sequence = sequence_dict[command]

    logging.info(f'Running sequence : {command}')
    for index in range(len(sequence)):
        item = sequence[index]
        servo_data = [float(s) for s in item.split(',')]
        logging.info("Angles : {0}".format(servo_data))
        if command in ['Activate', 'Deactivate']:
            time.sleep(fixed_sequence_sleep_time)
        else:
            time.sleep(sequence_sleep_time)


def run_command():
    global stop_thread

    time.sleep(1.0)
    active, shutdown = False, False

    while True:
        if shutdown:
            print('Shutting down')
            break

        command = read_command()

        if command == 'Exit':
            shutdown = True
            command = 'Deactivate'
            print('Got command to shut down')

        if command == 'None':
            time.sleep(0.5)
            continue

        if not active and command != 'Activate':
            print(f'Ignoring command {command}, while not Active')
            time.sleep(0.5)
            continue

        if command == 'Activate':
            if active:
                print('Active, but got command to activate, skipping')
                time.sleep(0.5)
                continue
            print('Processing command to activate')
            active = True        

        if command == 'Deactivate':
            if not active:
                print('Not Active, but got command to deactivate, skipping')
                time.sleep(0.5)
                continue
            active = False
            print('Processing command to deactivate')

        execute_sequence(command)

    stop_thread = True


if __name__ == "__main__":

    logging.basicConfig(format="%(asctime)s.%(msecs)05d: %(message)s",
                        level=logging.INFO,
                        datefmt="%H:%M:%S",
                        filename=log_file)
    load_sequences()

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