from nexus.code.process_image import compare_objects
from common.BasicConfig import BasicConfig
import os


def process_specie():
    cfg = BasicConfig()
    work_dir = cfg.workdir
    image_before = os.path.join(work_dir, 'image_test.jpg')
    image_after = os.path.join(work_dir, 'image_test_2.jpg')
    image_compare_result = compare_objects(image_before, image_after)
    print(image_compare_result)


process_specie()