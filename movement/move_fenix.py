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

    for item in sequence:
        #fnx.set_servo_values(item)
        time.sleep(0.1)

    time.sleep(10)
