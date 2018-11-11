from datetime import datetime
import os
import sys
import time

sys.path.append('/nexus/fenix/')
#sys.path.append('/nexus/fenix/fenix/code/')
from common.BasicConfig import BasicConfig
from fenix.code.movement import execute_sequence
from fenix.code.pi_camera import camera_shot
from fenix.code.process_dirs import get_next_specie
#from fenix.code.pi_cam_dummy import camera_shot

cfg = BasicConfig()
start_position = cfg.start_position[:]
#basic_path = cfg.workdir
results_path = cfg.results_dir
species_path = cfg.species_dir


class SpeciesDir:
    def __init__(self, specie):
        # make a dir, chmod and so on
        # dttm = datetime.now().strftime("%Y%m%d%H%M%S")
        self.specie_path = os.path.join(results_path, 'result_{0}'.format(specie))
        os.mkdir(self.specie_path)

    def archive(self):
        # archive self
        pass

    def send_to_nexus(self):
        # send self to nexus
        self.archive()
        pass


def process_specie(specie):
    execute_sequence()
    #specie = read_next_specie()
    specie_dir = SpeciesDir(specie)

    camera_shot(os.path.join(specie_dir.specie_path, 'before_image.jpg'))
    execute_sequence(specie=specie, path=specie_dir.specie_path, logging=1)
    camera_shot(os.path.join(specie_dir.specie_path, 'after_image.jpg'))
    execute_sequence()


for i in range(5):
    process_specie(get_next_specie())
    time.sleep(3)
