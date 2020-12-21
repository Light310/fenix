from cyber_core.kinematics_refactored import MovementSequence

# Here we get the command, like "up" or "forward"
# also the ground_z
def calculate_sequence(ms, command):

    command_text = command.split(' ')[0]
    command_value = int(command.split(' ')[1])

    if ms is None:
        ms = MovementSequence(legs_offset_v=-10, legs_offset_h=14)

    ms.reset_history()

    if command_text == 'forward2leg' or command_text == 'f2l':
        ms.move_2_legs(command_value)
    elif command_text == 'backward2leg' or command_text == 'b2l':
        ms.move_2_legs(-command_value)
    elif command_text == 'forward' or command_text == 'f':
        ms.move_body_straight(0, command_value, leg_seq=[1, 4, 3, 2])
    elif command_text == 'backward' or command_text == 'b':
        ms.move_body_straight(0, -command_value, leg_seq=[2, 3, 4, 1])
    elif command_text == 'up' or command_text == 'u':
        ms.body_movement(0, 0, command_value)
    elif command_text == 'down' or command_text == 'd':
        ms.body_movement(0, 0, -command_value)
    elif command_text == 'rep' or command_text == 'r':
        ms.reposition_legs(command_value, command_value)
    elif command_text == 'lookvert' or command_text == 'lv':
        if ms.current_angle * command_value > 0:
            ms.look_on_angle(0)
        ms.look_on_angle(-command_value)
    elif command_text == 'lookhor' or command_text == 'lh':
        ms.turn_only_body(command_value)
    elif command_text == 'comp':
        ms.body_compensation_for_a_leg(command_value)
    elif command_text == 'legup' or command_text == 'lu':
        command_value_2 = int(command.split(' ')[2])
        ms.move_leg_endpoint(command_value, [0, 0, command_value_2])
    elif command_text == 'legforw' or command_text == 'lf':
        command_value_2 = int(command.split(' ')[2])
        ms.move_leg_endpoint(command_value, [0, command_value_2, 0])
    elif command == 'center' or command_text == 'c':
        ms.body_to_center()
    #elif command_text == 'forward2legx3' or command_text == 'f2l3':
    #    move_2_legs_x3(ms, command_value)
    else:
        return None

    
    return ms.sequence
