#!/usr/bin/python

from time import sleep
import math

from lis3mdl import LIS3MDL

magnet = LIS3MDL()
magnet.enableLIS()

while True:
    mgnt = magnet.getMagnetometerRaw()
    str = 'Magnet: {0}. '.format(mgnt)
    heading = math.atan2(mgnt[1], mgnt[0]);

    if heading < 0:
        heading += math.pi*2
    elif heading > math.pi*2:
        heading -= math.pi*2
    headingDegrees = math.degrees(heading)
    str += 'Angle : {0}. '.format(headingDegrees)

    #print "Magnet:", magnet.getMagnetometerRaw()
    sleep(0.2)
    str += 'Magnet Temperature: {0}'.format(magnet.getLISTemperatureCelsius())
    #print "Magnet Temperature:", magnet.getLISTemperatureCelsius()    
    print (str)
    sleep(0.1)