import math
import sys
import math
from math import pi, sin, cos
import random
import os

import copy

from cyber_core.animation import animate
from cyber_core.dark_angles_processing_dashed import get_leg_angles, angles_str, target_alpha, target_beta, target_gamma

mode = 90
margin = 4
z_up = 5
#k = 14

turn_angle = pi / 96
# phi_angle = 15
phi_angle = 0
phi = math.radians(phi_angle)

#angles_prev = [target_alpha, target_beta, target_gamma]


def create_new_ms(ground_z, k):
    d = 5.3
    a = 8.7
    b = 6.9
    c = 13.2

    leg_distance = 3.8 
    O1 = Point(leg_distance, leg_distance, 0)
    D1 = Point(k, k, ground_z)
    Leg1 = Leg(1, "Leg1", O1, D1, 
               math.radians(target_alpha), math.radians(target_beta), math.radians(target_gamma),
               a, b, c, d)

    O2 = Point(leg_distance, -leg_distance, 0)
    D2 = Point(k, -k, ground_z)
    Leg2 = Leg(2, "Leg2", O2, D2, 
               math.radians(target_alpha), math.radians(target_beta), math.radians(target_gamma),
               a, b, c, d)

    O4 = Point(-leg_distance, leg_distance, 0)
    D4 = Point(-k, k, ground_z)
    Leg4 = Leg(4, "Leg4", O4, D4, 
               math.radians(target_alpha), math.radians(target_beta), math.radians(target_gamma),
               a, b, c, d)


    O3 = Point(-leg_distance, -leg_distance, 0)
    D3 = Point(-k, -k, ground_z)
    Leg3 = Leg(3, "Leg3", O3, D3, 
               math.radians(target_alpha), math.radians(target_beta), math.radians(target_gamma),
               a, b, c, d)
   

    return MovementSequence(Leg1, Leg2, Leg3, Leg4, ground_z)

def get_angle_by_coords(x1, y1):
    l = math.sqrt(x1 ** 2 + y1 ** 2)
    initial_angle = math.asin(abs(y1) / l)
    if x1 >= 0 and y1 >= 0:
        return initial_angle
    if x1 >= 0 and y1 < 0:
        return 2*pi - initial_angle
    if x1 < 0 and y1 >= 0:
        return pi - initial_angle
    if x1 < 0 and y1 < 0:
        return initial_angle + pi


def turn_on_angle(x1, y1, angle):

    if angle >= pi/2:
        raise Exception('Too big angle : {0}'.format(angle))
    l = math.sqrt(x1 ** 2 + y1 ** 2)
    initial_angle = get_angle_by_coords(x1, y1)
    result_angle = angle + initial_angle
    """
    print('In : ({0},{1}, {2}). Out : ({3},{4}, {5})'
          .format(x1,
                  y1,
                  angle,
                  round(cos(result_angle) * l, 2),
                  round(sin(result_angle) * l, 2),
                  result_angle))
    """
    return round(cos(result_angle) * l, 2), round(sin(result_angle) * l, 2)


class Point:
    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z

    def __str__(self):
        return '({0},{1},{2})'.format(round(self.x, 3), round(self.y, 3), round(self.z, 3))


class Line:
    def __init__(self, Point1, Point2):
        self.Point1 = Point1
        self.Point2 = Point2

    def convert_to_arr(self):
        return [[self.Point1.x, self.Point2.x],
                [self.Point1.y, self.Point2.y],
                [self.Point1.z, self.Point2.z]]



class LinearFunc:
    def __init__(self, point1=None, point2=None, k=None, b=None):
        if point1 is None:
            if k == 0:
                k = 0.00001
            self.k = k
            self.b = b
        else:
            delta_x = (point2.x - point1.x)
            if delta_x == 0:
                delta_x = 0.00001
            self.k = (point2.y - point1.y) / delta_x
            self.b = (point2.x * point1.y - point1.x * point2.y) / delta_x
            self.angle = math.atan2(point2.y - point1.y, point2.x - point1.x)

    def get_y(self, x):
        return self.k * x + self.b

    def get_x(self, y):
        return (y - self.b) / self.k

    def __str__(self):
        return 'y = ({0}) * x + ({1})'.format(round(self.k, 4), round(self.b, 4))


def calculate_intersection(func1, func2):
    x = (func1.b - func2.b) / (func2.k - func1.k)
    y = func1.k * x + func1.b
    return x, y

# function, that moves on a line from a given point to a target point for a margin distance
def move_on_a_line(intersection_point, target_point, margin):
    function = LinearFunc(intersection_point, target_point)
    new_point_x = round(intersection_point.x + math.cos(function.angle) * margin, 2)
    new_point_y = round(intersection_point.y + math.sin(function.angle) * margin, 2)
    return [new_point_x, new_point_y]



def target_body_position(target_leg_positions, unsupporting_leg_number):
    """
    take 4 legs basement points and the unsupporting leg
    return target position of body
    :param target_leg_positions: array: [[leg1_x, leg1_y], [leg2_x, leg2_y], [leg3_x, leg3_y], [leg4_x, leg4_y]]
    :param unsupporting_leg_number: 1 or 2 or 3 or 4
    :return: [body_x, body_y]
    """
    leg1_point = Point(target_leg_positions[0][0], target_leg_positions[0][1], 0)
    leg2_point = Point(target_leg_positions[1][0], target_leg_positions[1][1], 0)
    leg3_point = Point(target_leg_positions[2][0], target_leg_positions[2][1], 0)
    leg4_point = Point(target_leg_positions[3][0], target_leg_positions[3][1], 0)

    # find intersection point
    func1 = LinearFunc(leg1_point, leg3_point)
    func2 = LinearFunc(leg2_point, leg4_point)
    intersection = Point(*calculate_intersection(func1, func2), 0)

    # find a point on targeted line, at a margin distance from intersection point
    if unsupporting_leg_number == 1:
        target_leg = leg3_point
    elif unsupporting_leg_number == 2:
        target_leg = leg4_point
    elif unsupporting_leg_number == 3:
        target_leg = leg1_point
    elif unsupporting_leg_number == 4:
        target_leg = leg2_point
    else:
        raise ValueError('Bad leg number : {0}. Should be 1, 2, 3 or 4'.format(unsupporting_leg_number))

    body_target_point = move_on_a_line(intersection, target_leg, margin)

    return body_target_point


class MovementHistory:
    def __init__(self):
        self.angles_history = []

    def add_angles_snapshot(self, leg1, leg2, leg3, leg4):
        # angles are : gamma1, beta1, alpha1, tetta1, gamma2, beta2, alpha2, tetta2 ...
        # for leg1 tetta = 45 means 0 for servo
        # leg2 tetta = -45, leg3 tetta = -135, leg4 tetta = 135

        position = []
        for leg in [leg1, leg2, leg3, leg4]:
            position.append(round(math.degrees(leg.gamma), 2))
            position.append(round(math.degrees(leg.beta), 2))
            position.append(round(math.degrees(leg.alpha), 2))
            tetta = math.degrees(leg.tetta)
            if leg == leg1:
                #tetta -= 45
                tetta -= 90
            if leg == leg2:
                #tetta += 45
                tetta += 90
            if leg == leg3:
                #tetta += 135
                tetta += 90
            if leg == leg4:
                #tetta -= 135
                tetta -= 90
            tetta = round(tetta, 2)
            #print('tetta after : {0}'.format(tetta))
            position.append(tetta)
        self.angles_history.append(self.convert_angles(position))

    @staticmethod
    def convert_angles(angles):
        out_angles = []
        for i in range(4):
            for j in range(4):
                cur_value = angles[4*i + 3 - j]
                if j == 2:
                    out_angles.append(cur_value * -1)
                elif j == 0:
                    if i in [0, 2]:
                        out_angles.append(round(cur_value + 45, 2))
                    else:
                        out_angles.append(round(cur_value - 45, 2))
                else:
                    out_angles.append(cur_value)
        
        return out_angles


#################################################################


class Leg:
    def __init__(self, number, name, O, D, alpha, beta, gamma, len_a, len_b, len_c, len_d):
        self.number = number
        self.name = name
        self.O = O
        self.A = None
        self.B = None
        self.C = None
        self.D = D
        self.tetta = None
        self.alpha = alpha
        self.beta = beta
        self.gamma = gamma
        self.len_a = len_a
        self.len_b = len_b
        self.len_c = len_c
        self.len_d = len_d
        self.calculate_angles()

    def __str__(self):
        return '{0}. O: {1} -> A: {2} -> B: {3} -> C: {4} -> D: {5}. Angles : {6}' \
            .format(self.name,
                    self.O,
                    self.A,
                    self.B,
                    self.C,
                    self.D,
                    angles_str([self.tetta,
                                self.alpha,
                                self.beta,
                                self.gamma]))

    @staticmethod
    def move_point(point, delta_x, delta_y, delta_z):
        point.x += delta_x
        point.y += delta_y
        point.z += delta_z

    def move_mount_point(self, delta_x, delta_y, delta_z):
        #)
        #print('Got command to move point O for ({0},{1},{2})'.format(delta_x, delta_y, delta_z))
        self.move_point(self.O, delta_x, delta_y, delta_z)
        self.calculate_angles()

    def move_end_point(self, delta_x, delta_y, delta_z):
        #print(self)
        #print('Got command to move point D for ({0},{1},{2})'.format(delta_x, delta_y, delta_z))
        self.move_point(self.D, delta_x, delta_y, delta_z)
        self.calculate_angles()

    # means one leg is raised and moves with the body
    # end_delta = 0 means that leg is not moving, else it is also moving somehow
    def move_both_points(self, delta_x, delta_y, delta_z, end_delta_x, end_delta_y, end_delta_z):
        self.move_point(self.O, delta_x, delta_y, delta_z)
        self.move_point(self.D,
                        delta_x + end_delta_x,
                        delta_y + end_delta_y,
                        delta_z + end_delta_z)
        self.calculate_angles()

    def calculate_angles(self):
        try:
            #print('Before angles : {0}'.format(self))
            pass
        except:
            pass
        O = self.O
        D = self.D

        tetta = math.atan2(D.y - O.y, D.x - O.x)
        A = Point(O.x + self.len_d * cos(tetta), O.y + self.len_d * sin(tetta), O.z)
        l = round(math.sqrt((D.x - A.x) ** 2 + (D.y - A.y) ** 2), 2)
        delta_z = round(D.z - O.z, 2)

        global mode
        #alpha, beta, gamma = get_leg_angles(l, delta_z, [self.alpha, self.beta, self.gamma], mode=mode)
        alpha, beta, gamma = get_leg_angles(l, 
                                            delta_z, 
                                            mode, 
                                            [self.len_a, self.len_b, self.len_c, self.len_d])

        Bx = self.len_a * cos(alpha)
        By = self.len_a * sin(alpha)
        Cx = Bx + self.len_b * cos(alpha + beta)
        Cy = By + self.len_b * sin(alpha + beta)
        Dx = Cx + self.len_c * cos(alpha + beta + gamma)
        Dy = Cy + self.len_c * sin(alpha + beta + gamma)
        if abs(Dx - l) > 0.01 or abs(Dy - delta_z) > 0.01:
            print('WTF')

        B_xz = [self.len_a * cos(alpha), self.len_a * sin(alpha)]
        C_xz = [B_xz[0] + self.len_b * cos(alpha + beta), B_xz[1] + self.len_b * sin(alpha + beta)]
        D_xz = [C_xz[0] + self.len_c * cos(alpha + beta + gamma), C_xz[1] + self.len_c * sin(alpha + beta + gamma)]

        # print('XZ-projection. B : {0}. C : {1}. D : {2}.'.format(B_xz, C_xz, D_xz))
        D_prev = D
        self.A = A
        self.B = Point(A.x + B_xz[0] * cos(tetta), A.y + B_xz[0] * sin(tetta), A.z + B_xz[1])
        self.C = Point(A.x + C_xz[0] * cos(tetta), A.y + C_xz[0] * sin(tetta), A.z + C_xz[1])
        self.D = Point(A.x + D_xz[0] * cos(tetta), A.y + D_xz[0] * sin(tetta), A.z + D_xz[1])
        if abs(D_prev.x - self.D.x) > 0.01 or abs(D_prev.y - self.D.y) > 0.01 or abs(D_prev.z - self.D.z) > 0.01:
            #print('wtf')
            raise Exception('D_prev far from D. Angles : {0}'.format(angles_str([tetta, alpha, beta, gamma])))
        # print('XYZ-projection. B : {0}. C : {1}. D : {2}.'.format(self.B, self.C, self.D))

        self.tetta, self.alpha, self.beta, self.gamma = tetta, alpha, beta, gamma
        #print('After angles : {0}'.format(self))



###########################################################################


class MovementSequence:
    def __init__(self, Leg1, Leg2, Leg3, Leg4, ground_z):
        self.ground_z = ground_z
        self.mass_center_distance = 0
        self.mass_center_distance_gen2 = None
        self.mass_center = None
        self.unsupporting_leg = None
        self.target_unsupporting_leg = None
        self.mh = MovementHistory()

        self.Leg1 = Leg1
        self.Leg2 = Leg2
        self.Leg3 = Leg3
        self.Leg4 = Leg4
        self.Legs = [self.Leg1, self.Leg2, self.Leg3, self.Leg4]
        self.post_movement_actions()

    def __str__(self):
        result = '-------------------------------------- MS -------------------------------------\n'
        result += '\n'.join('{0}'.format(x) for x in self.Legs)
        return result

    def save_angles(self):
        self.mh.add_angles_snapshot(self.Leg1, self.Leg2, self.Leg3, self.Leg4)

    def post_movement_actions(self):
        # self.calculate_unsupporting_leg()
        print('Saving angles')
        self.save_angles()
   
    def body_movement(self, delta_x, delta_y, delta_z, leg_up=None, leg_up_delta=[0, 0, 0]):
        if delta_x == delta_y == delta_z == 0:
            #print('No movement required')
            return
               
        if leg_up == self.Leg1:
            self.Leg1.move_both_points(delta_x, delta_y, delta_z,
                                        leg_up_delta[0], leg_up_delta[1], leg_up_delta[2])
        else:
            self.Leg1.move_mount_point(delta_x, delta_y, delta_z)

        if leg_up == self.Leg2:
            self.Leg2.move_both_points(delta_x, delta_y, delta_z,
                                        leg_up_delta[0], leg_up_delta[1], leg_up_delta[2])
        else:
            self.Leg2.move_mount_point(delta_x, delta_y, delta_z)

        if leg_up == self.Leg3:
            self.Leg3.move_both_points(delta_x, delta_y, delta_z,
                                        leg_up_delta[0], leg_up_delta[1], leg_up_delta[2])
        else:
            self.Leg3.move_mount_point(delta_x, delta_y, delta_z)

        if leg_up == self.Leg4:
            self.Leg4.move_both_points(delta_x, delta_y, delta_z,
                                        leg_up_delta[0], leg_up_delta[1], leg_up_delta[2])
        else:
            self.Leg4.move_mount_point(delta_x, delta_y, delta_z)

        self.post_movement_actions()

    def body_to_center(self, delta_y=0, delta_x=0):
        # move body to center
        avg_o_x, avg_o_y, avg_d_x, avg_d_y = 0, 0, 0, 0
        for leg in self.Legs:
            avg_o_x += leg.O.x
            avg_o_y += leg.O.y
            avg_d_x += leg.D.x
            avg_d_y += leg.D.y

        avg_o_x /= 4
        avg_o_y /= 4
        avg_d_x /= 4
        avg_d_y /= 4

        self.body_movement(avg_d_x - avg_o_x + delta_x, avg_d_y - avg_o_y + delta_y, 0)

    def turn_body(self, angle):
        #num_steps = int(abs(angle / turn_angle))
        #step_angle = round(angle / num_steps, 4)

        #for m in range(num_steps):
        for leg in self.Legs:
            x_new, y_new = turn_on_angle(leg.O.x, leg.O.y, angle)
            delta_x = x_new - leg.O.x
            delta_y = y_new - leg.O.y
            leg.move_mount_point(delta_x, delta_y, 0)
        self.post_movement_actions()

    """
    # LM - legs middle point, LM12 - middle point between legs 1 and 2, and so on
    def calculate_basement_points(self):
        LF_13 = LinearFunc(point1=self.Leg1.D, point2=self.Leg3.D)
        LF_24 = LinearFunc(point1=self.Leg2.D, point2=self.Leg4.D)

        intersection = calculate_intersection(LF_13, LF_24)
        LM = Point(intersection[0], intersection[1], self.ground_z)
        return LM

    def calculate_mass_center(self):
        weight_points = []
        for leg in [self.Leg1, self.Leg2, self.Leg3, self.Leg4]:
            weight_points.append([(leg.O.x + leg.A.x) / 2, (leg.O.y + leg.A.y) / 2, leg_OA_weight])
            weight_points.append([(leg.A.x + leg.B.x) / 2, (leg.A.y + leg.B.y) / 2, leg_AB_weight])
            weight_points.append([(leg.B.x + leg.C.x) / 2, (leg.B.y + leg.C.y) / 2, leg_BC_weight])
            weight_points.append([(leg.C.x + leg.D.x) / 2, (leg.C.y + leg.D.y) / 2, leg_CD_weight])
        weight_points.append([(self.Leg1.O.x + self.Leg2.O.x + self.Leg3.O.x + self.Leg4.O.x) / 4,
                              (self.Leg1.O.y + self.Leg2.O.y + self.Leg3.O.y + self.Leg4.O.y) / 4,
                              body_weight])

        weight_sum = 0
        mass_center_x = 0
        mass_center_y = 0
        for item in weight_points:
            mass_center_x += item[0] * item[2]
            mass_center_y += item[1] * item[2]
            weight_sum += item[2]

        return [round(mass_center_x / weight_sum, 2), round(mass_center_y / weight_sum, 2)]
    """
    def leg_movement(self, leg_num, leg_delta):
        if leg_num == 1:
            leg = self.Leg1
        elif leg_num == 2:
            leg = self.Leg2
        elif leg_num == 3:
            leg = self.Leg3
        elif leg_num == 4:
            leg = self.Leg4
       
        for my_leg in [self.Leg1, self.Leg2, self.Leg3, self.Leg4]:
            if my_leg == leg:
                my_leg.move_end_point(leg_delta[0], leg_delta[1], leg_delta[2])
        self.post_movement_actions()

    @staticmethod
    def _leg_move(Leg, delta=None):
        if delta is None:
            Leg.move_end_point(0, 0, 0)
        else:
            #Leg.move_end_point(delta[0], delta[1], delta[2])
            Leg.move_end_point(*delta)
    
    @property
    def sequence(self):
        return self.mh.angles_history

    def sleep(self, iterations):
        for _ in range(iterations):
            self.post_movement_actions()


def ms_to_array(ms):
    ms_array = []
    for leg in [ms.Leg1, ms.Leg2, ms.Leg3, ms.Leg4]:
        ms_array.append([round(leg.O.x, 2),
                         round(leg.O.y, 2),
                         round(leg.O.z, 2),
                         round(leg.D.x, 2),
                         round(leg.D.y, 2),
                         round(leg.D.z, 2),
                         round(leg.alpha, 5),
                         round(leg.beta, 5),
                         round(leg.gamma, 5),
                         round(leg.tetta, 5)])
    return ms_array


def body_compensation_for_leg_delta(ms, leg_num, leg_delta):

    legs_coords_array = [[ms.Leg1.D.x + leg_delta[0][0], ms.Leg1.D.y  + leg_delta[0][1]],
                   [ms.Leg2.D.x + leg_delta[1][0], ms.Leg2.D.y + leg_delta[1][1]],
                   [ms.Leg3.D.x + leg_delta[2][0], ms.Leg3.D.y + leg_delta[2][1]],
                   [ms.Leg4.D.x + leg_delta[3][0], ms.Leg4.D.y + leg_delta[3][1]]]

    target = target_body_position(legs_coords_array, leg_num)

    current_body = [(ms.Leg1.O.x + ms.Leg2.O.x + ms.Leg3.O.x + ms.Leg4.O.x)/4,
                    (ms.Leg1.O.y + ms.Leg2.O.y + ms.Leg3.O.y + ms.Leg4.O.y)/4]

    ms.body_movement(target[0] - current_body[0], target[1] - current_body[1], 0)


def compensated_leg_movement(ms, leg_num, leg_delta):
    full_leg_delta = [[0, 0], [0, 0], [0, 0], [0, 0]]
    if leg_num == 1:
        leg = ms.Leg1
        full_leg_delta[0] = [leg_delta[0], leg_delta[1]]
    elif leg_num == 2:
        leg = ms.Leg2
        full_leg_delta[1] = [leg_delta[0], leg_delta[1]]
    elif leg_num == 3:
        leg = ms.Leg3
        full_leg_delta[2] = [leg_delta[0], leg_delta[1]]
    elif leg_num == 4:
        leg = ms.Leg4
        full_leg_delta[3] = [leg_delta[0], leg_delta[1]]

    # moving body to compensate future movement
    body_compensation_for_leg_delta(ms, leg_num, full_leg_delta)

    #max_delta = max(abs(x) for x in leg_delta)
    #num_steps = int(max_delta / ms.step)
    #leg_delta = [round(x / num_steps, 4) for x in leg_delta]
    #for m in range(num_steps):
    #leg.move_end_point(leg_delta[0], leg_delta[1], leg_delta[2])
    leg.move_end_point(*leg_delta)
    ms.post_movement_actions()


def move_legs_z(ms, legs_delta_z, leg_seq):
    """
    max_delta = max(abs(x) for x in legs_delta_z)
    num_steps = int(max_delta / ms.step)
    leg_delta_step = [round(x / num_steps, 4) for x in legs_delta_z]

    for m in range(num_steps):
    """
    for i in range(len(leg_seq)):
        leg_seq[i].move_end_point(0, 0, legs_delta_z[i])
    ms.post_movement_actions()


def leg_move_with_compensation(ms, leg_num, delta_x, delta_y):
    #compensated_leg_movement(ms, leg_num, [0, 0, z_up])
    #compensated_leg_movement(ms, leg_num, [delta_x, delta_y, 0])
    compensated_leg_movement(ms, leg_num, [delta_x, delta_y, z_up])
    compensated_leg_movement(ms, leg_num, [0, 0, -z_up])


def turn_body(ms, angle_deg):
    angle = math.radians(angle_deg)
    # move leg one by one
    for leg in [ms.Leg1, ms.Leg3, ms.Leg2, ms.Leg4]:
        x_new, y_new = turn_on_angle(leg.D.x, leg.D.y, angle)
        delta_x = x_new - leg.D.x
        delta_y = y_new - leg.D.y
        leg_move_with_compensation(ms, leg.number, delta_x, delta_y)

    ms.body_to_center()

    ms.turn_body(angle)


def move_body_straight(ms, delta_x, delta_y, leg_seq=[1, 2, 3, 4], body_to_center=False):
    #print(f'(x, y) = ({delta_x}, {delta_y}). margin = {margin}, k = {k}, ground_z = {ground_z}, mode = {mode}')

    for leg in leg_seq:
        leg_move_with_compensation(ms, leg, delta_x, delta_y)
    if body_to_center:
        ms.body_to_center()

def reposition_legs(ms, delta_xy):
    leg_move_with_compensation(ms, 1, delta_xy, delta_xy)
    leg_move_with_compensation(ms, 2, delta_xy, -delta_xy)
    leg_move_with_compensation(ms, 3, -delta_xy, -delta_xy)
    leg_move_with_compensation(ms, 4, -delta_xy, delta_xy)

    ms.body_to_center()

def move_2_legs(ms, delta_y, sync_body=True):
    z = 6
    full_leg_delta_1 = [0, delta_y, z]
    full_leg_delta_2 = [0, 0, -z]
    quarter_step = round(delta_y/4, 1)
    three_quarter_step = round(3*delta_y/4, 1)

    #ms.body_movement(0, quarter_step, 0)

    for leg in [ms.Leg2, ms.Leg4]:
        leg.move_end_point(*full_leg_delta_1)
    ms.post_movement_actions()

    for leg in [ms.Leg2, ms.Leg4]:
        leg.move_end_point(*full_leg_delta_2)
    ms.post_movement_actions()

    #ms.body_movement(0, three_quarter_step, 0)
    ms.body_movement(0, delta_y, 0)

    for leg in [ms.Leg1, ms.Leg3]:
        leg.move_end_point(*full_leg_delta_1)
    ms.post_movement_actions()

    for leg in [ms.Leg1, ms.Leg3]:
        leg.move_end_point(*full_leg_delta_2)
    ms.post_movement_actions()

    """
    print('Leg 2 and 4 up')
    for leg in [ms.Leg2, ms.Leg4]:
        leg.move_end_point(*full_leg_delta_1)
    ms.post_movement_actions()
    if sync_body:
        print('Sync body 1')
        ms.body_to_center()
    
    print('Leg 2 and 4 down')
    for leg in [ms.Leg2, ms.Leg4]:
        leg.move_end_point(*full_leg_delta_2)
    ms.post_movement_actions()
    if sync_body:
        print('Sync body 2')
        ms.body_to_center()
        
    if not sync_body:
        print('Sync body 3')
        ms.body_to_center()
        #ms.body_movement(0, 5, 0)

    print('Leg 1 and 3 up')
    for leg in [ms.Leg1, ms.Leg3]:
        leg.move_end_point(*full_leg_delta_1)
    ms.post_movement_actions()
    if sync_body:
        print('Sync body 4')
        ms.body_to_center()
    
    print('Leg 1 and 3 down')
    for leg in [ms.Leg1, ms.Leg3]:
        leg.move_end_point(*full_leg_delta_2)
    ms.post_movement_actions()
    if sync_body:
        print('Sync body 5')
        ms.body_to_center()
        
    if not sync_body:
        print('Sync body 6')
        ms.body_to_center()
    """

def move_2_legs_x3(ms, delta_y):
    z = 5
    full_leg_delta_1 = [0, delta_y, z]
    full_leg_delta_2 = [0, 0, -z]
    full_leg_delta_3 = [0, 2*delta_y, z]

    for leg in [ms.Leg2, ms.Leg4]:
        leg.move_end_point(*full_leg_delta_1)
    ms.post_movement_actions()

    for leg in [ms.Leg2, ms.Leg4]:
        leg.move_end_point(*full_leg_delta_2)
    ms.post_movement_actions()

    #ms.body_movement(0, three_quarter_step, 0)
    ms.body_movement(0, delta_y, 0)

    for leg in [ms.Leg1, ms.Leg3]:
        leg.move_end_point(*full_leg_delta_3)
    ms.post_movement_actions()

    for leg in [ms.Leg1, ms.Leg3]:
        leg.move_end_point(*full_leg_delta_2)
    ms.post_movement_actions()

    ms.body_movement(0, delta_y, 0)

    for leg in [ms.Leg2, ms.Leg4]:
        leg.move_end_point(*full_leg_delta_3)
    ms.post_movement_actions()

    for leg in [ms.Leg2, ms.Leg4]:
        leg.move_end_point(*full_leg_delta_2)
    ms.post_movement_actions()

    ms.body_movement(0, delta_y, 0)

    for leg in [ms.Leg1, ms.Leg3]:
        leg.move_end_point(*full_leg_delta_1)
    ms.post_movement_actions()

    for leg in [ms.Leg1, ms.Leg3]:
        leg.move_end_point(*full_leg_delta_2)
    ms.post_movement_actions()

    """
    # first pair up-forward for X
    for leg in [ms.Leg2, ms.Leg4]:
        leg.move_end_point(*full_leg_delta_1)
    ms.post_movement_actions()
    ms.body_to_center(delta_y=-1)
    # first pair down
    for leg in [ms.Leg2, ms.Leg4]:
        leg.move_end_point(*full_leg_delta_2)
    ms.post_movement_actions()
    ms.body_to_center()

    # second pair up-forward for 2X
    for leg in [ms.Leg1, ms.Leg3]:
        leg.move_end_point(*full_leg_delta_3)
    ms.post_movement_actions()
    ms.body_to_center(delta_y=-1)
    # second pair down
    for leg in [ms.Leg1, ms.Leg3]:
        leg.move_end_point(*full_leg_delta_2)
    ms.post_movement_actions()
    ms.body_to_center()    
    
    # first pair up-forward again for 2X
    for m in range(num_steps_3):
        for leg in [ms.Leg2, ms.Leg4]:
            leg.move_end_point(*leg_delta_3)
        ms.post_movement_actions()
        ms.body_to_center(delta_y=-1)
    # first pair down
    for m in range(num_steps_2):
        for leg in [ms.Leg2, ms.Leg4]:
            leg.move_end_point(*leg_delta_2)
        ms.post_movement_actions()
        ms.body_to_center()
    
    # second pair up-forward for 2X
    for m in range(num_steps_3):
        for leg in [ms.Leg1, ms.Leg3]:
            leg.move_end_point(*leg_delta_3)
        ms.post_movement_actions()
        ms.body_to_center(delta_y=-1)
    # second pair down
    for m in range(num_steps_2):
        for leg in [ms.Leg1, ms.Leg3]:
            leg.move_end_point(*leg_delta_2)
        ms.post_movement_actions()
        ms.body_to_center()    
        
    # first pair up-forward again for 2X
    for leg in [ms.Leg2, ms.Leg4]:
        leg.move_end_point(*full_leg_delta_3)
    ms.post_movement_actions()
    ms.body_to_center(delta_y=-1)
    # first pair down
    for leg in [ms.Leg2, ms.Leg4]:
        leg.move_end_point(*full_leg_delta_2)
    ms.post_movement_actions()
    ms.body_to_center()
    
    # second pair up-forward for X
    for leg in [ms.Leg1, ms.Leg3]:
        leg.move_end_point(*full_leg_delta_1)
    ms.post_movement_actions()
    ms.body_to_center(delta_y=-1)
    # second pair down
    for leg in [ms.Leg1, ms.Leg3]:
        leg.move_end_point(*full_leg_delta_2)
    ms.post_movement_actions()
    ms.body_to_center()
    """
    