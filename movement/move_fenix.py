import time

from commands import get_command
#from sequences import get_values_for_servos
from cyber_core.create_sequence import calculate_sequence
#from servos import Fenix
from adj_servos import Fenix


fnx = Fenix()

start = True
while True:
    command = get_command()

    if command == 'exit':
        fnx.stop()
        break

    #sequence = get_values_for_servos(command)
    if command != 'none':
        sequence = calculate_sequence(command)    

        # if current values too far from 1st item, we send values with low speed
        if start:
            print('We are at start')
            if fnx.angles_are_close(sequence[0]) is False:
                fnx.set_servo_values(sequence[0], 3000)
                for i in range(20):
                    print('Sleeping {0} sec'.format(i))
                    time.sleep(1)
                    if fnx.angles_are_close(sequence[0]):
                        break
            start = False

        for item in sequence:
            #fnx.set_servo_values(item)
            fnx.set_servo_values_adj(item)
            time.sleep(0.02)

    time.sleep(10)
