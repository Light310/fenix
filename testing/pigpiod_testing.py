import os
import time
import pigpio

#os.system("sudo pigpiod")
#time.sleep(1.0)

pi = pigpio.pi()
pi.set_servo_pulsewidth(4, 0)
pi.stop()
#os.system("sudo killall pigpiod")
