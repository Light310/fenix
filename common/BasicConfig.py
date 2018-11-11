import configparser
import os
from definitions import ROOT_DIR

class BasicConfig:
    def __init__(self):
        self.config = configparser.ConfigParser()
        self.config.read(os.path.join(ROOT_DIR, 'main.cfg'))

    @property
    def workdir(self):
        return os.path.join(ROOT_DIR, self.config['Dir']['work_dir'])

    @property
    def species_dir(self):
        return os.path.join(self.workdir, 'species')

    @property
    def results_dir(self):
        return os.path.join(self.workdir, 'results')

    @property
    def data_dir(self):
        return os.path.join(self.workdir, self.config['Dir']['data_dir'])

    @property
    def start_position(self):
        position_str = self.config['Position']['start_position']
        split = position_str.split(',')
        result = []
        for item in split:
            result.append(int(item))
        return result

    @property
    def features_cnt(self):
        return int(self.config['Mutation']['features_cnt'])

    @property
    def servos_file(self):
        return os.path.join(self.workdir, self.config['Files']['servos_file'])
