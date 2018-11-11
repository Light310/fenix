import time
import os
import math
from common.BasicConfig import BasicConfig
from common.utils import *
from fenix.code.gyro_accel import get_ga_value
#from fenix.code.ga_dummy import get_ga_value
from datetime import datetime
import csv

sleep_time = 0.05
step_divider = 1

#control_file = '/nexus/files/servos.txt'

cfg = BasicConfig()
servos_file = cfg.servos_file
results_path = cfg.results_dir
species_path = cfg.species_dir


def isclose(x, y):
    if abs(float(x) - float(y)) < 0.01:
        return True
    else:
        return False


def positions_equal(array1, array2):
    for i in range(0, len(array1)):
        if not isclose(array1[i], array2[i]):
            return False
    return True


def max_diff(array1, array2):
    md = 0
    ln = len(array1)
    for i in range(0, ln):
        md = max(md, abs(array1[i] - array2[i]))

    return md


def execute_sequence(specie=None, path=None, logging=0):
    if specie is None:
        sequence = []
        sequence.append(cfg.start_position[:])
    else:
        sequence = read_specie(specie)
    current_position = read_servos()[:]
    steps_performed = 0
    initial_position = current_position[:]
    index = 0
    if len(sequence) == 0:
        target_position = current_position[:]
    else:
        target_position = sequence[index]

    md = max_diff(initial_position, target_position)
    step_amt = int(md / step_divider)

    while True:
        steps_performed += 1
        if positions_equal(target_position, current_position) or steps_performed > 200:
            steps_performed = 0
            index += 1
            if index >= len(sequence):
                print("Sequence completed")
                break
            print('Switched index to {0}'.format(index))
            target_position = sequence[index][:]
            initial_position = current_position[:]
            md = max_diff(initial_position, target_position)
            step_amt = int(md / step_divider)

        for m in range(0, len(target_position)):
            if isclose(target_position[m], current_position[m]):
                pass
            else:
                cur_step = round(float(abs(initial_position[m] - target_position[m]) * 1.0 / step_amt), 2)
                if current_position[m] > target_position[m]:
                    current_position[m] = round(current_position[m] - cur_step, 2)
                    if current_position[m] < target_position[m]:
                        current_position[m] = int(math.ceil(current_position[m]))
                if current_position[m] < target_position[m]:
                    current_position[m] = round(current_position[m] + cur_step, 2)
                    if current_position[m] > target_position[m]:
                        current_position[m] = int(math.floor(current_position[m]))

        write_servos(current_position)
        time.sleep(sleep_time)
        if logging == 1:
            print_data_to_file(now_str(), current_position[:], get_ga_value()[:], path, specie)



def write_servos(array):
    with open(servos_file, 'w') as f:
        servos_txt = ','.join(str(int(e)) for e in array)
        f.write(servos_txt)


def read_servos():
    if not os.path.isfile(servos_file):
        write_servos(cfg.start_position)

    with open(servos_file, 'r') as f:
        line = f.readline()

    split = line.split(',')
    result = []
    for item in split:
        result.append(int(item))
    return result


def read_specie(specie):
    sequence = []
    with open(os.path.join(species_path, specie), 'r') as f:
        content = f.readlines()
    content = [x.strip() for x in content]
    for feature in content:
        feature_str = feature.replace('[', '').replace(']', '')
        split = feature_str.split(',')
        feature_arr = []
        for item in split:
            feature_arr.append(int(item))
        sequence.append(feature_arr)

    return sequence


def print_data_to_file(dttm, ga_data, servo_data, path, specie):
    file = os.path.join(path, 'data_{0}.csv'.format(specie))
    with open(file, 'a') as csv_file:
        csv_file.write('{0}|{1}|{2}\n'.format(dttm, array_to_string(servo_data), array_to_string(ga_data)))


#execute_sequence('specie_20181028224456')