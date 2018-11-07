from nexus.code.process_image import compare_objects
from common.BasicConfig import BasicConfig
import os


def analyze_specie(specie):
    cfg = BasicConfig()
    work_dir = cfg.workdir
    specie_dir = os.path.join(work_dir, 'result_{0}'.format(specie))
    image_before = os.path.join(specie_dir, 'before_image.jpg')
    image_after = os.path.join(specie_dir, 'after_image.jpg')
    image_compare_result = compare_objects(image_before, image_after)
    print('Specie : {0}. Result : {1}'.format(specie, image_compare_result))


analyze_specie('specie_20181030191641')
analyze_specie('specie_20181030191642')
analyze_specie('specie_20181030191643')
analyze_specie('specie_20181030191644')
analyze_specie('specie_20181030191645')

