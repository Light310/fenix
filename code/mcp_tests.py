import smbus
from modules.mcp23017 import MCP23017
import subprocess

def check_i2c():
    p = subprocess.Popen(['i2cdetect', '-y','1'],stdout=subprocess.PIPE,)
    i2c = p.stdout.readlines()
    return str(i2c[7])

bus = smbus.SMBus(1)
mcp = MCP23017(bus)

#mcp.set_a_values(0b11111111)
#mcp.set_b_values(0b11111111)
for i in range(13):
    print('i : {0}'.format(i))
    mcp.set_pin(i, 1)
    #print(check_i2c())
    if '69' in check_i2c():
        print('Switch happened')
    mcp.set_pin(i, 0)
    #print(check_i2c())
