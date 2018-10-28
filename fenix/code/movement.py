import time
import os
import math
from common.BasicConfig import BasicConfig
from common.MyTime import now_str
from datetime import datetime
import csv

sleep_time = 0.05
step_divider = 1

#control_file = '/nexus/files/servos.txt'

cfg = BasicConfig()
servos_file = cfg.servos_file


def isclose(x, y):
    if abs(float(x) - float(y)) < 0.01:
        return True
    else:
        return False


class Move:
    def __init__(self, name, start_seq, main_seq, finish_seq, cmd):
        self.name = name
        self.start_seq = start_seq
        self.main_seq = main_seq
        self.finish_seq = finish_seq
        self.cmd = cmd

    def __str__(self):
        return self.name


def close_values(array1, array2, delta):
    cnt = 0
    ln = len(array1)
    for i in range(0, ln):
        if abs(array1[i] - array2[i]) < delta:
            cnt += 1

    if cnt == ln:
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


def execute_sequence(specie):
    sequence = read_specie(specie)
    data = {}
    current_position = read_servos()[:]
    delta = 1
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
        #print('-----------')
        #print('Initial position : {0}'.format(initial_position))
        #print('Current position : {0}'.format(current_position))
        #print('Target  position : {0}'.format(target_position))
        # if target_position == current_position:
        steps_performed += 1
        # if close_values(target_position, current_position, delta) or steps_performed > 200:
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
            # print('-----------')
            # print('Initial position : {0}'.format(initial_position))
            # print('Current position : {0}'.format(current_position))
            # print('Target  position : {0}'.format(target_position))

        for m in range(0, len(target_position)):
            # if abs(target_position[m] - current_position[m]) < delta:
            # if abs(float(target_position[m]) - float(current_position[m])) < 0.01:
            if isclose(target_position[m], current_position[m]):
                # print ("Position {0} equal".format(m))
                pass
            else:
                cur_step = round(float(abs(initial_position[m] - target_position[m]) * 1.0 / step_amt), 2)
                # print('M : {0}. Initial : {1}, target : {2}. Cur_Step = {3}, step_amt = {4}'
                #      .format(m, initial_position[m], target_position[m], cur_step, step_amt))
                if current_position[m] > target_position[m]:
                    current_position[m] = round(current_position[m] - cur_step, 2)
                    if current_position[m] < target_position[m]:
                        current_position[m] = int(math.ceil(current_position[m]))
                if current_position[m] < target_position[m]:
                    current_position[m] = round(current_position[m] + cur_step, 2)
                    if current_position[m] > target_position[m]:
                        current_position[m] = int(math.floor(current_position[m]))

        write_servos(current_position)
        dttm = now_str()
        data[dttm] = current_position[:]
        time.sleep(sleep_time)

    print_data_to_file(data, specie)



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
    with open(os.path.join(cfg.species_dir, specie), 'r') as f:
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


def print_data_to_file(data, specie):
    file = os.path.join(cfg.data_dir, 'data_{0}.csv'.format(specie))
    with open(file, 'w') as csv_file:
        for key, value in data.items():
            value_txt = ','.join(str(int(e)) for e in value)
            csv_file.write('{0}:{1}\n'.format(key, value_txt))


execute_sequence('specie_20181028224456')
