import random
import sys
sys.path.append('/nexus/fenix/')
from common.BasicConfig import BasicConfig
from datetime import datetime
import os
import time


class Specie:
    def __init__(self):
        cfg = BasicConfig()
        self.basic_position = cfg.start_position
        dttm = datetime.now().strftime("%Y%m%d%H%M%S")
        self.specie_file = os.path.join(cfg.species_dir, 'specie_{0}'.format(dttm))
        self.features_cnt = cfg.features_cnt

    def generate_feature(self):
        mutation = [0 for i in range(16)]
        mutated_position = [0 for i in range(16)]

        for i in range(16):
            rnd = random.randint(1, 100)
            if rnd > 85:
                mutation[i] = -1
            elif rnd > 70:
                mutation[i] = 1

        for i in range(len(self.basic_position)):
            mutated_position[i] = self.basic_position[i] + 30*mutation[i]

        return mutated_position

    def generate_specie(self):
        for i in range(self.features_cnt):
            feature = self.generate_feature()
            with open(self.specie_file, 'a') as f:
                f.write('{0}\n'.format(feature))


for i in range(5):
    Specie().generate_specie()
    time.sleep(1)
