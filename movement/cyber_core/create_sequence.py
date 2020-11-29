#from cyber_core.dark_kinematics import create_new_ms, move_body_straight, move_2_legs, move_2_legs_x3
from cyber_core.dark_kinematics_dashed import create_new_ms, move_body_straight, compensated_leg_movement, move_2_legs, move_2_legs_x3

# Here we get the command, like "up" or "forward"
# also the ground_z
def calculate_sequence(movement, ground_z = -17):    

    step_len = 8
    k = 14

    if movement == 'up':
        ground_z = -9
    ms = create_new_ms(ground_z, k)


    if movement == 'forward':
        #move_body_straight(ms, 0, step_len, leg_seq=[1, 4, 3, 2], body_to_center=True)
        #compensated_leg_movement(ms, 3, [0, 0, 5])
        #compensated_leg_movement(ms, 3, [0, 0, -5])
        #ms.body_movement(3, 0, 0)
        #ms.body_movement(-3, 0, 0)
        #move_2_legs(ms, 12, sync_body=False)
        move_2_legs_x3(ms, 10)
        #ms.body_movement(5, 5, 0)
    elif movement == 'backward':
        move_body_straight(ms, 0, -step_len, leg_seq=[2, 3, 4, 1], body_to_center=True)
    elif movement == 'up':
        activation_move = 4
        ms.body_movement(0, 0, activation_move)
    elif movement == 'down':
        deactivation_move = -4
        ms.body_movement(0, 0, deactivation_move)
    #ms.run_animation(delay=50)
    for item in ms.sequence:
        print(item)
    return ms.sequence
