import logging
import threading
import sys
import time
import argparse
import pigpio
sys.path.append('/nexus/fenix/')
from common.BasicConfig import BasicConfig


cfg = BasicConfig()
sequence_file = cfg.sequence_file
#sequence_file = 'C:\\Users\\Sergey\\PycharmProjects\\fenix\\wrk\\sequence.txt'
#sequence_file = "D:\\Development\\Python\\sequence.txt"

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
#servo_signal_sleep = 0.35
servo_list = [4, 17, 27, 22, 18, 23, 24, 25, 6, 13, 19, 26, 12, 16, 20, 21]
sequence_sleep_time = 0.00875
initial_position_sleep_time = 1.0
#sequence_sleep_time = 0.8
global stop_thread
stop_thread = False


class FenixServos(threading.Thread):
    def __init__(self):
        self.pi = pigpio.pi()
        if not self.pi.connected:
            exit()

        threading.Thread.__init__(self, daemon=True)
        self.start()

    def run(self):
        global stop_thread, servo_data
        while True:
            if 'servo_data' not in globals():
                logging.info('Servo_data not yet defined. Skipping')
                time.sleep(servo_signal_sleep)
                continue
            calibrated_data = []
            for i in range(16):
                calibrated_servo = self.calibrate_servo(i, servo_data[i])
                pulse_width = int(MIN_WIDTH + (MAX_WIDTH - MIN_WIDTH) * calibrated_servo / MAX_DIFF)
                self.pi.set_servo_pulsewidth(servo_list[i], pulse_width)
                calibrated_data.append(calibrated_servo)
            #logging.info('Initial    data : {0}'.format(servo_data))
            logging.info('Calibrated data : {0}'.format(calibrated_data))
            if stop_thread:
                break
            time.sleep(servo_signal_sleep)

    @staticmethod
    def calibrate_servo(i, input_value):
        return round(calibration_dict[i][0] + (input_value * calibration_dict[i][1] * 1.0 / 90), 4)

    def __del__(self):
        logging.info("Closing pigpio connection")
        self.pi.stop()


def execute_sequence(activation_only):
    global servo_data, stop_thread
    with open(sequence_file) as f:
        sequence = f.readlines()
    sequence = [x.strip().replace('[', '').replace(']', '') for x in sequence]

    if activation_only:
        sequence = [sequence[0]]

    for index in range(len(sequence)):
        item = sequence[index]
        servo_data = [float(s) for s in item.split(',')]
        logging.info("Writing : {0}".format(servo_data))
        if index == 0 and not activation_only:
            time.sleep(initial_position_sleep_time)
        else:
            time.sleep(sequence_sleep_time)

    stop_thread = True


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Fenix Movement")
    parser.add_argument('-a', '--act', dest='activation_only', default=False, required=False, action='store_true')
    args = parser.parse_args()

    logging.basicConfig(format="%(asctime)s.%(msecs)03d: %(message)s", level=logging.INFO, datefmt="%H:%M:%S")
    logging.info('Starting sequence.')
    
    servos_thread = FenixServos()
    x = threading.Thread(target=execute_sequence, args=(args.activation_only,))
    x.start()
    x.join()
    servos_thread.join()
    
    logging.info('Sequence complete')