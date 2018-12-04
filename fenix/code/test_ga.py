import sys
sys.path.append('/nexus/fenix/')
from fenix.code.gyro_accel import get_ga_value
import time

for i in range(100):
    #print(get_ga_value())
    get_ga_value()
    time.sleep(0.1)