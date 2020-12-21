import time
import copy

from commands import get_command

#from sequences import get_values_for_servos
from cyber_core.get_sequence_refactored import calculate_sequence
from cyber_core.kinematics_refactored import MovementSequence
from servos import Fenix


#start = datetime.datetime.now()
#ms = create_new_ms(ground_z=-17, k=14)
ms = MovementSequence(legs_offset_v=-5, legs_offset_h=14)

#calculate_sequence(ms, 'forward')
#print('Time taken : {0}'.format(datetime.datetime.now() - start))
fnx = Fenix()
fnx.set_speed(1000)

start = True
while True:
    command = get_command()
    
    if command == 'exit':
        break

    #sequence = get_values_for_servos(command)
    if command != 'none':
        # may be I should make a deep copy of ms, if some moves had been recorder into it
        try:
            ms_cp = copy.deepcopy(ms)
            sequence = calculate_sequence(ms, command)
        except Exception as e:
            print(f'Could not process command - {str(e)}')
            ms = copy.deepcopy(ms_cp)
            time.sleep(3.0)
            continue

        if sequence is None:
            time.sleep(0.5)
            continue
        
        for angles in sequence:
            print('Going for {0}'.format(angles))
            fnx.set_servo_values_paced(angles)
            fnx.print_status()

    else:
        time.sleep(0.25)
