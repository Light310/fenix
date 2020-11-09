def get_command():
    remote_command = get_remote_command()
    if remote_command:
        return remote_command
    
    local_command = get_local_command()
    if local_command:
        return local_command

    return 'exit'


def get_local_command():
    command_file = '/fenix/movement/command.txt'
    with open(command_file, 'r') as f:
        command = f.readline()
    print('Processing local command {0}'.format(command))
    return command


def get_remote_command():
    return None
