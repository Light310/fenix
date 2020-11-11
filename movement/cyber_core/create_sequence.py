from cyber_core.dark_kinematics import create_new_ms, move_body_straight, compensated_leg_movement


def calculate_sequence(movement):
    step_len = 6
    ground_z = -7
    k = 16

    if movement == 'up':
        ground_z = -5
    ms = create_new_ms(ground_z, k, step=0.2)

    if movement == 'forward':
        #move_body_straight(ms, 0, step_len, leg_seq=[1, 4, 3, 2], body_to_center=True)
        #compensated_leg_movement(ms, 3, [0, 0, 5])
        #compensated_leg_movement(ms, 3, [0, 0, -5])
        ms.body_movement(3, 0, 0)
        ms.body_movement(-3, 0, 0)
    elif movement == 'backward':
        move_body_straight(ms, 0, -step_len, leg_seq=[2, 3, 4, 1], body_to_center=True)
    elif movement == 'up':
        activation_move = 4
        ms.body_movement(0, 0, activation_move)
    elif movement == 'down':
        deactivation_move = -4
        ms.body_movement(0, 0, deactivation_move)
    #ms.run_animation(delay=50)
    print(ms.sequence)
    return ms.sequence

    
#grounds_z = [3, 6]

"""
for i in range(len(grounds_z) - 1):
    ground_z = -grounds_z[i+1]
    
    
    sq_file = f'{sq_file_prefix}body_backwards_{-ground_z}.txt'
    print(sq_file)
    ms = create_new_ms(ground_z, k, step=0.2)
    ms.body_movement(5, -5, 0) 
    ms.print_to_sequence_file(sq_file)
    

    # move forward    
    try:
        sq_file = f'{sq_file_prefix}forward_{-ground_z}.txt'
        print(sq_file)
        ms = create_new_ms(ground_z, k, step=0.2)
        move_body_straight(ms, 0, step_len, leg_seq=[1, 4, 3, 2], body_to_center=True)    
        ms.print_to_sequence_file(sq_file)
    except:
        print('Lowering step')
        sq_file = f'{sq_file_prefix}forward_{-ground_z}.txt'
        print(sq_file)
        ms = create_new_ms(ground_z, k, step=0.2)
        move_body_straight(ms, 0, step_len - 2, leg_seq=[1, 4, 3, 2], body_to_center=True)    
        ms.print_to_sequence_file(sq_file)
    
    # move backwards
    try:
        sq_file = f'{sq_file_prefix}backwards_{-ground_z}.txt'
        print(sq_file)
        ms = create_new_ms(ground_z, k, step=0.2)
        move_body_straight(ms, 0, -step_len, leg_seq=[2, 3, 4, 1], body_to_center=True)    
        ms.print_to_sequence_file(sq_file)
    except:
        print('Lowering step')
        sq_file = f'{sq_file_prefix}backwards_{-ground_z}.txt'
        print(sq_file)
        ms = create_new_ms(ground_z, k, step=0.2)
        move_body_straight(ms, 0, -step_len + 2, leg_seq=[2, 3, 4, 1], body_to_center=True)    
        ms.print_to_sequence_file(sq_file)

    # straferight    
    try:
        sq_file = f'{sq_file_prefix}straferight_{-ground_z}.txt'
        print(sq_file)
        ms = create_new_ms(ground_z, k, step=0.2)
        move_body_straight(ms, step_len, 0, leg_seq=[2, 1, 3, 4], body_to_center=True)    
        ms.print_to_sequence_file(sq_file)
    except:
        print('Lowering step')
        sq_file = f'{sq_file_prefix}straferight_{-ground_z}.txt'
        print(sq_file)
        ms = create_new_ms(ground_z, k, step=0.2)
        move_body_straight(ms, step_len - 2, 0, leg_seq=[2, 1, 3, 4], body_to_center=True)    
        ms.print_to_sequence_file(sq_file)
    
    # strafeleft
    try:
        sq_file = f'{sq_file_prefix}strafeleft_{-ground_z}.txt'
        print(sq_file)
        ms = create_new_ms(ground_z, k, step=0.2)
        move_body_straight(ms, -step_len, 0, leg_seq=[4, 3, 1, 2], body_to_center=True)    
        ms.print_to_sequence_file(sq_file)
    except:
        sq_file = f'{sq_file_prefix}strafeleft_{-ground_z}.txt'
        print(sq_file)
        ms = create_new_ms(ground_z, k, step=0.2)
        move_body_straight(ms, -step_len + 2, 0, leg_seq=[4, 3, 1, 2], body_to_center=True)    
        ms.print_to_sequence_file(sq_file)
    
    # up
    sq_file = f'{sq_file_prefix}up_{grounds_z[i]}_{grounds_z[i+1]}.txt'
    print(sq_file)
    ms = create_new_ms(-grounds_z[i], k, step=0.1)
    activation_move = grounds_z[i+1] - grounds_z[i]
    ms.body_movement(0, 0, activation_move)
    #ms.print_to_sequence_file(sq_file)
    print(ms.sequence)
    
    # down
    for j in range(i+1):
        sq_file = f'{sq_file_prefix}down_{grounds_z[i+1]}_{grounds_z[j]}.txt'
        print(sq_file)
        ms = create_new_ms(-grounds_z[i+1], k, step=0.1)
        deactivation_move = grounds_z[j] - grounds_z[i+1]
        ms.body_movement(0, 0, deactivation_move)
        ms.print_to_sequence_file(sq_file)

"""

#ms.run_animation(delay=50)
