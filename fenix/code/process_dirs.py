from datetime import datetime
import os
import sys
sys.path.append('/nexus/fenix/')
#sys.path.append('/nexus/fenix/fenix/code/')
from common.BasicConfig import BasicConfig

from os import walk
                                                  

def get_next_specie():
    cfg = BasicConfig()
    #print('species_dir :  {0}'.format(cfg.species_dir))
    print('results_dir :  {0}'.format(cfg.results_dir))

    species = []
    results = []
    for (filenames) in walk(cfg.species_dir):    
        for item in filenames[2]:
            print('Item : {0}'.format(item))
            if 'specie_20' in item:
                species.append(item.replace('specie_',''))
        break

    for (dirpath, dirnames, filenames) in walk(cfg.results_dir):
        #print(dirpath)
        #print(dirnames)
        #print(filenames)
        for item in dirnames:
            print('Dir : {0}'.format(item))
            if 'result_specie_20' in item:
                results.append(item.replace('result_specie_',''))
        break

    unprocessed = []
    for specie in species:
        if specie not in results:
            unprocessed.append(specie)

    #print (species)
    #print (results)
    print ('Unprocessed : {0}'.format(unprocessed))

    return ('specie_{0}'.format(unprocessed[0]))

#get_next_specie()