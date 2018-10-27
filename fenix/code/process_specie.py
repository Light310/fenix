from datetime import datetime
import os
from common.BasicConfig import BasicConfig

cfg = BasicConfig()
start_position = cfg.start_position
path = cfg.workdir


class SpeciesDir:
    def __init__(self):
        # make a dir, chmod and so on
        self.path = ''
        dttm = datetime.now().strftime("%Y%m%d%H%M%S")
        os.mkdir(path+dttm)

    def archive(self):
        # archive self
        pass

    def send_to_nexus(self):
        # send self to nexus
        self.archive()
        pass


# connects to gyro accel and returns its data
# mb later it will be done not so often
def get_gyro_accel_data():
    gyro_accel_data = 0
    return gyro_accel_data


# move to position
# reads current position and starts moving from one position to another, until last one is reached
# if logging = 1, stores data in a log after each move
def execute_sequence(sequence, logging = 0):
    if logging == 1:
        gyro_accel_data = get_gyro_accel_data()
        # write down servos and gyro accel data
    pass


# reads the next specie for processing
# returns a 2d-array
def read_next_specie():
    specie = [[0,0], [0,0]]
    return specie


# makes a camera shot
def camera_shot(name):
    pass


def process_specie():
    execute_sequence(start_position)
    specie = read_next_specie()
    specie_dir = SpeciesDir()

    camera_shot(specie_dir.path)
    execute_sequence(specie, logging=1)
    camera_shot(specie_dir.path)

    specie_dir.send_to_nexus()


def __main__():
    process_specie()