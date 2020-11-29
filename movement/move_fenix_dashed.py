import time
#import datetime

from commands import get_command

#from sequences import get_values_for_servos
from cyber_core.create_sequence import calculate_sequence
from cyber_core.dark_kinematics_dashed import create_new_ms
from servos import Fenix


#start = datetime.datetime.now()
ms = create_new_ms(ground_z=-17, k=14)

#calculate_sequence(ms, 'forward')
#print('Time taken : {0}'.format(datetime.datetime.now() - start))
fnx = Fenix()
fnx.set_speed(2000)

start = True
while True:
    command = get_command()
    
    if command == 'exit':
        break

    #sequence = get_values_for_servos(command)
    if command != 'none':
        sequence = calculate_sequence(ms, command)
        
        for angles in sequence:
            print('Going for {0}'.format(angles))
            fnx.set_servo_values_paced(angles)
            fnx.print_status()     
            #time.sleep(1)

    time.sleep(3)
