import time

from commands import get_command
from sequences import get_values_for_servos
from servos import Fenix


fnx = Fenix()

while True:
    command = get_command()

    if command == 'exit':
        break

    sequence = get_values_for_servos(command)

    # if current values too far from 1st item, we send values with low speed
    if fnx.angles_are_close(sequence[0]) is False:
        fnx.set_servo_values(sequence[0], 3000)
        for i in range(20):
            print('Sleeping {0} sec'.format(i))
            time.sleep(1)
            if fnx.angles_are_close(sequence[0]):
                break

    for item in sequence:
        fnx.set_servo_values(item)
        time.sleep(0.01)

    time.sleep(10)
