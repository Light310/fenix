import time
import os
import math
from common.BasicConfig import BasicConfig


sleep_time = 0.2
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
    for i in range(len(array1)):
        md = max(md, abs(array1[i] - array2[i]))

    return md


def execute_sequence(sequence):
    for item in sequence:
        write_servos(item)
        time.sleep(sleep_time)


def write_servos(array):
    with open(servos_file, 'w') as f:
        servos_txt = ','.join(str(float(round(e, 3))) for e in array)
        print('Writing position : {0}'.format(servos_txt))
        f.write(servos_txt)


def read_servos():
    if not os.path.isfile(servos_file):
        write_servos(cfg.start_position)

    with open(servos_file, 'r') as f:
        line = f.readline()

    split = line.split(',')
    result = []
    for item in split:
        result.append(float(item))
    return result



#execute_sequence('specie_20181028224456')