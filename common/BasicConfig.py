import configparser
import os
from definitions import ROOT_DIR

class BasicConfig:
    def __init__(self):
        self.config = configparser.ConfigParser()
        self.config.read(os.path.join(ROOT_DIR, 'main.cfg'))
        #print(os.path.join(ROOT_DIR, 'main.cfg'))
        #print(config['Dir']['work_dir'])
        #config.read()

    @property
    def workdir(self):
        return (os.path.join(ROOT_DIR, self.config['Dir']['work_dir']))

    @property
    def start_position(self):
        return self.config['Position']['start_position']