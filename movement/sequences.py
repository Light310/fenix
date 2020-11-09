from cyber_core.create_sequence import calculate_sequence


def get_values_for_servos(command):
    if command == 'none':
        return []
    return calculate_sequence(command)
