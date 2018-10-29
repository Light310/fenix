from datetime import datetime
import os
from common.BasicConfig import BasicConfig
from fenix.code.movement import execute_sequence

cfg = BasicConfig()
start_position = cfg.start_position[:]
path = cfg.workdir


class SpeciesDir:
    def __init__(self, specie):
        # make a dir, chmod and so on
        # dttm = datetime.now().strftime("%Y%m%d%H%M%S")
        self.specie_path = os.path.join(path, 'result_{0}'.format(specie))
        os.mkdir(self.specie_path)

    def archive(self):
        # archive self
        pass

    def send_to_nexus(self):
        # send self to nexus
        self.archive()
        pass


# reads the next specie for processing
# returns a 2d-array
def read_next_specie():
    specie = [[0,0], [0,0]]
    return specie


# makes a camera shot
def camera_shot(name):
    pass


def process_specie(specie):
    execute_sequence(start_position)
    #specie = read_next_specie()
    specie_dir = SpeciesDir()

    camera_shot(specie_dir.path)
    execute_sequence(specie, logging=1)
    camera_shot(specie_dir.path)

    specie_dir.send_to_nexus()


process_specie()

"""
'specie_20181028224456'
'specie_20181028224457'
'specie_20181028224458'
'specie_20181028224459'
"""