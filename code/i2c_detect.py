import os
import subprocess
import re

p = subprocess.Popen(['i2cdetect', '-y','1'],stdout=subprocess.PIPE,)
i2c = p.stdout.readlines()
print(i2c[3], i2c[7])
"""
for i in range(0, 9):
    line = str(p.stdout.readline())
    print(line)
"""