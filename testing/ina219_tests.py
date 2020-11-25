from ina219 import INA219
from ina219 import DeviceRangeError
import time

SHUNT_OHMS = 0.1


def read():
    ina1 = INA219(SHUNT_OHMS, address=0x40)
    ina1.configure()
    ina2 = INA219(SHUNT_OHMS, address=0x41)
    ina2.configure()
    ina3 = INA219(SHUNT_OHMS, address=0x44)
    ina3.configure()
    ina4 = INA219(SHUNT_OHMS, address=0x45)
    ina4.configure()

    #print("Bus Voltage: %.3f V" % ina.voltage())
    try:
        print("Current: %.3f , %.3f , %.3f, %.3f mA" % (ina1.current(), ina2.current(), ina3.current(), ina4.current()))
        #print("Current: %.3f mA" % (ina3.current()))
        #print("Power: %.3f mW" % ina.power())
        #print("Shunt voltage: %.3f mV" % ina3.shunt_voltage())        
        print("------------")
    except DeviceRangeError as e:
        # Current out of device range with specified shunt resistor
        print(e)

try:
    while True:    
        read()
        time.sleep(0.1)
except KeyboardInterrupt:
    print('Exit')