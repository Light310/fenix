import logging
import threading
import requests
import sys
import time
import argparse
import pigpio
sys.path.append('/nexus/fenix/')
from common.BasicConfig import BasicConfig


#cfg = BasicConfig()
#sequence_file = cfg.sequence_file
#sequence_file = 'C:\\Users\\Sergey\\PycharmProjects\\fenix\\wrk\\sequence.txt'
#sequence_path = "D:\\Development\\Python\\"
wrk_path = '/nexus/fenix/wrk/'
sequence_path = '/nexus/fenix/wrk/sequences/'
sequence_dict = {
    'Back': 'sq_backw_8',
    'LeftBackwards': 'sq_backw_left_5',
    'RightBackwards': 'sq_backw_right_5',
    'Forward': 'sq_forw_8',
    'LeftForward': 'sq_forw_left_5',
    'RightForward': 'sq_forw_right_5',
    'StrafeLeft': 'sq_strafe_left_8',
    'StrafeRight': 'sq_strafe_right_8',
    'TurnRight': 'sq_turn_cw_30',
    'TurnLeft': 'sq_turn_ccw_30',
    'Activate': 'sq_activation',
    'Deactivate': 'sq_deactivation'
}

command_file = f'{wrk_path}command.txt'
speed_file = f'{wrk_path}speed.txt'
log_file = f'{wrk_path}movement.log'

calibration_dict = [
    [183, 95], [175, 89], [183, 94], [141, 90],
    [178, 95], [177, 90], [187, 95], [138, 94],
    [182, 95], [182, 90], [177, 99], [129, 92],
    [192, 95], [182, 95], [185, 93], [135, 90]
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
            calibrated_data = []
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



def execute_sequence():
    global servo_data, stop_thread

    time.sleep(1.0)

    command = 'Activate'
    activation = True

    while True and command != 'Deactivate':
        if activation:
            activation = False
        else:
            command = read_command()

        if command == 'None':
            time.sleep(0.5)
        else:
            sequence = sequence_dict[command]

            logging.info(f'Running sequence : {command}')
            for index in range(len(sequence)):
                item = sequence[index]
                servo_data = [float(s) for s in item.split(',')]
                logging.info("Angles : {0}".format(servo_data))
                if command in ['act', 'deact']:
                    time.sleep(fixed_sequence_sleep_time)
                else:
                    time.sleep(sequence_sleep_time)

    stop_thread = True


if __name__ == "__main__":

    logging.basicConfig(format="%(asctime)s.%(msecs)05d: %(message)s",
                        level=logging.INFO,
                        datefmt="%H:%M:%S",
                        filename=log_file)
    load_sequences()

    logging.info('Starting movement.')
    try:
        servos_thread = FenixServos()
        x = threading.Thread(target=execute_sequence)
        x.start()

        y = threading.Thread(target=read_speed)
        y.start()

        x.join()
        y.join()

        servos_thread.join()
    finally:
        del servos_thread
        logging.info('Movement complete')