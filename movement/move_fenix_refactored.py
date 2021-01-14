import time
import copy

from commands import get_command

#from sequences import get_values_for_servos
from cyber_core.get_sequence_refactored import calculate_sequence
from cyber_core.kinematics_refactored import MovementSequence
from servos import Fenix
from modules.fnx_ina219 import FNX_INA219

inas = FNX_INA219()


#start = datetime.datetime.now()
#ms = create_new_ms(ground_z=-17, k=14)
ms = MovementSequence(legs_offset_v=-3, legs_offset_h=18)

#calculate_sequence(ms, 'forward')
#print('Time taken : {0}'.format(datetime.datetime.now() - start))
fnx = Fenix()
#fnx.set_speed(500)
movement_speed = 50

start = True
while True:
    command = get_command()
    
    if command == 'exit':
        break

    if command != 'none' and bool(command.strip()):
        try:
            ms_cp = copy.deepcopy(ms)
            sequence = calculate_sequence(ms, command)
        except Exception as e:
            print(f'Could not process command - {str(e)}')
            ms = copy.deepcopy(ms_cp)
            time.sleep(3.0)
            continue

        if sequence is None:
            print('Sequence is None')
            time.sleep(0.5)
        else:
        
            if 'start' in command or 'end' in command:
                fnx.set_speed(800)
            else:
                fnx.set_speed(movement_speed)

            for angles in sequence:
                #print('Going for {0}'.format(angles))
                print(f'Before : {inas.read()}')
                fnx.set_servo_values_paced(angles)
                print(f'After  : {inas.read()}')
                #fnx.print_status()

    else:
        time.sleep(0.25)
