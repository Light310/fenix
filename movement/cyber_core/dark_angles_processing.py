import math
from math import pi, sin, cos
import numpy as np

target_alpha = 0
target_beta = 0
target_gamma = 0

def get_leg_angles(delta_x, delta_z, prev_angles, mode, lengths):
    #print(f'Looking for angles for ({delta_x}, {delta_z}, {prev_angles}, {mode})')
    if sum(prev_angles) != 0:
        prev_ksi = math.degrees(sum(prev_angles)) + 90
    else:
        prev_ksi = None

    possible_angles = find_angles(delta_x, delta_z, lengths, prev_ksi)

    # recalculating to check for some error
    """
    for item in possible_angles:
        alpha = item[0]
        beta = item[1]
        gamma = item[2]
        Bx = a * cos(alpha)
        By = a * sin(alpha)
        Cx = Bx + b * cos(alpha + beta)
        Cy = By + b * sin(alpha + beta)
        Dx = Cx + c * cos(alpha + beta + gamma)
        Dy = Cy + c * sin(alpha + beta + gamma)
        if abs(Dx - delta_x) > 0.01 or abs(Dy - delta_z) > 0.01:
            raise Exception('Recalculating error')
    """

    return get_best_angles(possible_angles, prev_angles, mode)

def get_best_angles(all_angles, prev_angles, mode):
    min_distance = 100000000
    best_angles = None
    min_distance_num = 0
    
    for item in all_angles:
        if not check_angles(item, mode)[0]:
            continue        
        cur_distance = get_angles_distance(item, prev_angles)
        #print(angles_str(item), cur_distance)
        #print(cur_distance)
        
        if cur_distance <= min_distance:
            min_distance = cur_distance
            best_angles = item[:]

    if min_distance > 0.1:
        min_distance_num += 1        
        if min_distance_num > 1:            
            print('best_angles : {0}'.format([math.degrees(x) for x in best_angles]))
            raise Exception('Min distance found : {0}'.format(min_distance))

    #print(f'Diff: {angles_diff(prev_angles, best_angles)}. Prev angles: {angles_str(prev_angles)}, best_angles: {angles_str(best_angles)}')
    #print(min_distance)
    if best_angles is None:
        #print('No suitable angles found. Halt')
        #for angle in all_angles:
        #    print(check_angles(angle, mode)[1])
        raise Exception('No angles\n')
        # sys.exit(1)
    return best_angles

def check_angles(angles, mode):
    # mode means range plus and minus from vertical. Mode 10 means 80 - 100 degrees
    alpha = math.degrees(angles[0])
    beta = math.degrees(angles[1])
    gamma = math.degrees(angles[2])
    angles_converted = str([round(x, 2) for x in [alpha, beta, gamma]])
    if alpha < -40 or alpha > 40:
        return False, angles_converted + ' alpha={0}'.format(alpha)
    if beta < -110 or beta > -15:
        return False,  angles_converted + '. beta={0}'.format(beta)
    if gamma < -110 or gamma > 0: # 15 is cuz of construction of last joint
        return False, angles_converted + '. gamma={0}'.format(gamma)
    #if alpha + beta < -110 or alpha + beta > 80:
    #    return False, angles_converted + '. alpha + beta = {0}'.format(alpha + beta)
    
    if mode is None:
        mode = 40

    if alpha + beta + gamma < -90 - mode or alpha + beta + gamma > -90 + mode:
        return False, f'{angles_converted}. mode {mode}. alpha + beta + gamma = {alpha + beta + gamma}'
        
    return True, 'All ok'


def find_angles(Dx, Dy, lengths, prev_ksi=None):
    a, b, c, d = lengths
    #print(f'Dx, Dy : ({Dx}, {Dy})')
    results = []
    full_dist = math.sqrt(Dx ** 2 + Dy ** 2)
    if full_dist > a + b + c:
        #print('No decisions. Full distance : {0}'.format(full_dist))
        raise Exception('No decisions. Full distance : {0}'.format(full_dist))
        #sys.exit(1)

    #for k in np.arange(-35.0, 35.0, 0.1):
    from_angle = -90.0
    to_angle = 90.0
    angle_step = 1.0
    if prev_ksi:
        from_angle = max(from_angle, prev_ksi - 3.0)
        to_angle = min(to_angle, prev_ksi + 3.0)
        angle_step = 0.01
        #print(f'Trying angles : {from_angle}, {to_angle}')

    for k in np.arange(from_angle, to_angle, angle_step):

        ksi = math.radians(k)

        Cx = Dx + c * math.cos(math.pi / 2 + ksi)
        Cy = Dy + c * math.sin(math.pi / 2 + ksi)
        dist = math.sqrt(Cx ** 2 + Cy ** 2)

        if dist > a + b or dist < abs(a - b):
            pass
        else:
            # print('Ksi : {0}'.format(k))
            alpha1 = math.acos((a ** 2 + dist ** 2 - b ** 2) / (2 * a * dist))
            beta1 = math.acos((a ** 2 + b ** 2 - dist ** 2) / (2 * a * b))
            beta = -1 * (pi - beta1)

            alpha2 = math.atan2(Cy, Cx)
            alpha = alpha1 + alpha2

            Bx = a * cos(alpha)
            By = a * sin(alpha)

            BD = math.sqrt((Dx - Bx) ** 2 + (Dy - By) ** 2)
            angle_C = math.acos((b ** 2 + c ** 2 - BD ** 2) / (2 * b * c))

            for coef in [-1, 1]:
                gamma = coef * (pi - angle_C)

                Cx = Bx + b * cos(alpha + beta)
                Cy = By + b * sin(alpha + beta)
                new_Dx = Cx + c * cos(alpha + beta + gamma)
                new_Dy = Cy + c * sin(alpha + beta + gamma)
                if abs(new_Dx - Dx) > 0.01 or abs(new_Dy - Dy) > 0.01:
                    continue

                results.append([alpha, beta, gamma])
                #if abs(math.degrees(alpha+beta+gamma) - k + 90) > 0.1:
                #    print(f'wtf {math.degrees(alpha+beta+gamma)}. {k}. {abs(math.degrees(alpha+beta+gamma) - k + 90)}')

    return results

def get_angles_distance(angles1, angles2):
    # angles sent in radians
    # adding difference of last join from perpendicular as a critical value
    # do I need SQRT? WTF?
    return math.sqrt((angles1[0] - angles2[0]) ** 2 + \
           (angles1[1] - angles2[1]) ** 2 + \
           (angles1[2] - angles2[2]) ** 2 + \
           3 * abs(math.degrees(angles1[0] + angles1[1] + angles1[2]) + 90) ** 2)


def angles_str(angles):
    result = ''
    for item in angles:
        result += '{0} '.format(round(math.degrees(item), 2))
    return result

def angles_diff(angles1, angles2):
    summ_diff = 0
    result = []
    for angle1, angle2 in zip(angles1, angles2):
        item = round(math.degrees(angle1 - angle2), 2)
        result.append(item)
        summ_diff += abs(item)
    
    return result, round(summ_diff, 2)
