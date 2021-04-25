import time
import datetime
import copy

from commands import get_command

#from sequences import get_values_for_servos
from cyber_core.get_sequence_refactored import calculate_sequence
from cyber_core.kinematics_refactored import MovementSequence
from servos import Fenix
from modules.fnx_ina219 import FNX_INA219
from modules.utils import write_legs_file


#inas = FNX_INA219()

ms = MovementSequence(legs_offset_v=-10, legs_offset_h=16)
#ms = MovementSequence(legs_offset_v=-10, legs_offset_h=18)

fnx = Fenix()
#fnx.set_speed(500)
movement_speed = 500
run_up_speed = 250 # 130
run_down_speed = 250 # 130 # 200

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
            time.sleep(2.0)
            continue

        if sequence is None:
            print('Sequence is None')
            time.sleep(0.5)
        else:
        
            if 'start' in command or 'end' in command:
                fnx.set_speed(800)
            else:
                fnx.set_speed(movement_speed)

            start_time = datetime.datetime.now()
            if 'r2l' in command:
                for index, angles in enumerate(sequence):
                    if index % 2 == 1:
                        fnx.set_speed(run_down_speed)
                    else:
                        fnx.set_speed(run_up_speed)
                    #print(f'\nStarting movement : {datetime.datetime.now()}')
                    #print('Going for {0}'.format(angles))
                    #print(f'Before : {inas.read()}')
                    fnx.set_servo_values_paced(angles)
                    #print(f'After  : {inas.read()}')
                    #fnx.print_status()
                    #rint(f'Finished movement : {datetime.datetime.now()}')
            elif 'forward' in command:
                write_legs_file(0)
                fnx.set_servo_values_paced(sequence[0])
                write_legs_file(1)
                fnx.set_servo_values_paced(sequence[1])
                fnx.set_servo_values_paced(sequence[2])
                write_legs_file(0)
                fnx.set_servo_values_paced(sequence[3])
                write_legs_file(4)
                fnx.set_servo_values_paced(sequence[4])
                fnx.set_servo_values_paced(sequence[5])
                write_legs_file(0)
                fnx.set_servo_values_paced(sequence[6])
                write_legs_file(3)
                fnx.set_servo_values_paced(sequence[7])
                fnx.set_servo_values_paced(sequence[8])
                write_legs_file(0)
                fnx.set_servo_values_paced(sequence[9])
                write_legs_file(2)
                fnx.set_servo_values_paced(sequence[10])
                fnx.set_servo_values_paced(sequence[11])
                write_legs_file(0)
                fnx.set_servo_values_paced(sequence[12])
                write_legs_file(0)
                # 1 4 3 2
            else:
                for angles in sequence:
                    #print(f'Starting movement : {datetime.datetime.now()}')
                    #print('Going for {0}'.format(angles))
                    #print(f'Before : {inas.read()}')
                    fnx.set_servo_values_paced(angles)
                    #print(f'After  : {inas.read()}')
                    #fnx.print_status()
                    #print(f'Finished movement : {datetime.datetime.now()}')
            print(f'Step took : {datetime.datetime.now() - start_time}')

    else:
        time.sleep(0.25)
