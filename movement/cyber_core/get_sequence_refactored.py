from cyber_core.kinematics_refactored import MovementSequence

# Here we get the command, like "up" or "forward"
# also the ground_z
def calculate_sequence(ms, command):

    command_text = command.split(' ')[0]
    command_value = int(command.split(' ')[1])
    try:
        command_value_2 = int(command.split(' ')[2])
    except:
        command_value_2 = None

    if ms is None:
        ms = MovementSequence(legs_offset_v=-10, legs_offset_h=15)

    ms.reset_history()
    print(f'Offset V : {ms.current_legs_offset_v}. Offset H : {ms.current_legs_offset_h}')

    if command_text == 'forward2leg' or command_text == 'f2l':
        if command_value_2 is None:
            ms.move_2_legs(command_value)
        else:
            ms.move_2_legs(command_value, command_value_2)
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
        #if ms.current_angle * command_value > 0:
        #    ms.look_on_angle(0)
        ms.look_on_angle(-command_value)
    elif command_text == 'lookhor' or command_text == 'lh':
        ms.turn(command_value, only_body=True)
    elif command_text == 'turn' or command_text == 't':
        turn = command_value
        current_turn = 0
        if turn > 0:
            while turn - current_turn > 30:
                print('Turning on 30')
                ms.turn_move(30)
                current_turn += 30

            print(f'Turning on {turn - current_turn}')
            ms.turn_move(turn - current_turn)
        else:
            while turn - current_turn < -30:
                print('Turning on -30')
                ms.turn_move(-30)
                current_turn -= 30

            print(f'Turning on {turn - current_turn}')
            ms.turn_move(turn - current_turn)

    elif command_text == 'comp':
        ms.body_compensation_for_a_leg(command_value)
    elif command_text == 'legup' or command_text == 'lu':
        ms.move_leg_endpoint(command_value, [0, 0, command_value_2])
    elif command_text == 'legforw' or command_text == 'lf':
        ms.move_leg_endpoint(command_value, [0, command_value_2, 0])
    elif command_text == 'legside' or command_text == 'ls':
        ms.move_leg_endpoint(command_value, [command_value_2, 0, 0])
    elif command_text == 'center' or command_text == 'c':
        ms.body_to_center()
    elif command_text == 'start':
        target_height = 14
        target_width = 14
        # current_legs_offset_v is below zero
        ms.body_movement(0, 0, ms.current_legs_offset_v + target_height)
        ms.reposition_legs(target_width - ms.current_legs_offset_h, target_width - ms.current_legs_offset_h)
    elif command_text == 'end':
        target_height = 3
        target_width = 18
        # current_legs_offset_v is below zero
        ms.reposition_legs(target_width - ms.current_legs_offset_h, target_width - ms.current_legs_offset_h)
        ms.body_movement(0, 0, ms.current_legs_offset_v + target_height)
    elif command_text == 'dance':
        ms.opposite_legs_up(command_value, command_value_2)
    elif command_text == 'hit':
        ms.hit(command_value)
    else:
        return None
    
    #ms.print_legs_diff()
    return ms.sequence
