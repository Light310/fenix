import time


command_file = '/fenix/movement/command.txt'


def write_command_file(command):
    print('writing {0} to command file'.format(command))
    with open(command_file, 'w') as f:
        f.write(command)


symbols = {
    'w': 'forward',
    's': 'backward',
    'r': 'up',
    't': 'down',
    'z': 'exit'
}

try:
    write_command_file('none')

    while True:
        command = input('Enter command:\n')
        #print('Got symbol : {0}'.format(symbol))
        #command = symbols.get(symbol, 'none')
        write_command_file(command)
        if command == 'exit':
            break
        time.sleep(0.3)
        write_command_file('none')

except KeyboardInterrupt:
    write_command_file('exit')
