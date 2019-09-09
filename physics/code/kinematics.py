import math
import sys
from math import pi, sin, cos
import random
#sys.path.append('/nexus/fenix/')
import numpy as np
import copy


from common.BasicConfig import BasicConfig


from physics.code.animation import animate
#from fnx.animate import animate
#from common.utils import angle_to_rad, rad_to_angle
#from fenix.code.kinetic_movement import execute_sequence


cfg = BasicConfig()
tmp_file = cfg.tmp_file
sequence_file = cfg.sequence_file


def angle_to_rad(angle):
    return angle * pi / 180


def rad_to_angle(rad):
    return rad * 180 / pi


"""
a = 10.5
b = 5.5
c = 14.5
d = 5.5

a = 10.5
b = 5.5
c = 21.0
d = 5.5


a = 10.5
a2 = 13.6
b = 5.5
c = 9.3
d = 5.5
"""
ground_z = -9
k = 14
turn_angle = pi / 96

z_up = 4

mc_magrin = 1


#phi_angle = 7.5
phi_angle = 0.0
phi = angle_to_rad(phi_angle)

#body_weight = 300
#leg_CD_weight = 500
body_weight = 300
leg_CD_weight = 30
leg_BC_weight = 30
leg_AB_weight = 50
leg_OA_weight = 30


"""
start_gamma = -55
start_beta = -60
start_alpha = 25
"""
"""
start_gamma = -20
start_beta = -100
start_alpha = 35
"""
start_gamma = -90
start_beta = -60
start_alpha = -60

target_1 = 60
target_2 = -60
target_3 = -90


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

    def get_y(self, x):
        return self.k * x + self.b

    def get_x(self, y):
        return (y - self.b) / self.k

    def __str__(self):
        return 'y = ({0}) * x + ({1})'.format(round(self.k, 4), round(self.b, 4))


def calculate_intersection(func1, func2):
    x = (func1.b - func2.b) / (func2.k - func1.k)
    y = func1.k * x + func1.b
    return [x, y]


def distance_to_line(x, y, LF, target_sector, vertical):
    if LF.k == 0:
        k = 0.00001
    else:
        k = LF.k
    normal_line_k = -1 / k

    normal_line_b = y - normal_line_k * x
    normal_func = LinearFunc(k=normal_line_k, b=normal_line_b)
    intersection = calculate_intersection(LF, normal_func)
    d = math.sqrt((intersection[0] - x) ** 2 + (intersection[1] - y) ** 2)

    if vertical == 1:
        if target_sector in [1, 2]:
            if x < LF.get_x(y):
                d = -1 * d
        else:
            if x > LF.get_x(y):
                d = -1 * d
    else:
        if target_sector in [2, 3]:
            if y > LF.get_y(x):
                d = -1 * d
        else:
            if y < LF.get_y(x):
                d = -1 * d

    return round(d, 3)


def angle_between_lines(f1, f2):
    angle = math.atan2(abs(f1.k - f2.k), 1 + f1.k * f2.k)
    return angle


def define_sector(LF_12, LF_23, LF_34, LF_14, x, y):
    if LF_14.get_x(y) <= x and LF_12.get_y(x) <= y:
        return 1
    if LF_23.get_x(y) <= x and LF_12.get_y(x) > y:
        return 2
    if LF_23.get_x(y) > x and LF_34.get_y(x) > y:
        return 3
    if LF_14.get_x(y) > x and LF_34.get_y(x) <= y:
        return 4


class MovementHistory:
    def __init__(self):
        self.body_lines_history = [[], [], [], []]
        self.line_mass_weight_history = [[]]
        self.basement_lines_history = [[], [], [], [], [], [], [], []]
        self.leg_lines_history = [[], [], [], [], [], [], [], [], [], [], [], [], [], [], [], []]
        self.unsupporting_leg_lines_history = [[]]
        self._lines_history = []
        self.angles_history = []

    # o1 - o4 = leg1.O - leg4.O
    def add_body_lines(self, o1, o2, o3, o4):
        self.body_lines_history[0].append(Line(o1, o2).convert_to_arr())
        self.body_lines_history[1].append(Line(o2, o3).convert_to_arr())
        self.body_lines_history[2].append(Line(o3, o4).convert_to_arr())
        self.body_lines_history[3].append(Line(o4, o1).convert_to_arr())

    def add_mw_lines(self, wm1, wm2):
        self.line_mass_weight_history[0].append(Line(wm1, wm2).convert_to_arr())

    def add_unsup_leg_line(self, d):
        unsupporting_point_1 = d
        unsupporting_point_2 = Point(d.x, d.y, d.z + 10)
        self.unsupporting_leg_lines_history[0].append(Line(unsupporting_point_1, unsupporting_point_2).convert_to_arr())

    # d1 - d4 = leg1.D - leg4.D
    def add_basement_lines(self, d1, d2, d3, d4, ground_z):
        LF_13 = LinearFunc(point1=d1, point2=d3)
        LF_24 = LinearFunc(point1=d2, point2=d4)
        intersection = calculate_intersection(LF_13, LF_24)
        legs_center = Point(intersection[0], intersection[1], ground_z)

        LM_12 = Point((d1.x + d2.x) / 2,
                      (d1.y + d2.y) / 2,
                      ground_z)
        LM_23 = Point((d2.x + d3.x) / 2,
                      (d2.y + d3.y) / 2,
                      ground_z)
        LM_34 = Point((d3.x + d4.x) / 2,
                      (d3.y + d4.y) / 2,
                      ground_z)
        LM_14 = Point((d1.x + d4.x) / 2,
                      (d1.y + d4.y) / 2,
                      ground_z)

        leg1_D_projection = Point(d1.x, d1.y, ground_z)
        leg2_D_projection = Point(d2.x, d2.y, ground_z)
        leg3_D_projection = Point(d3.x, d3.y, ground_z)
        leg4_D_projection = Point(d4.x, d4.y, ground_z)

        self.basement_lines_history[0].append(Line(leg1_D_projection, leg2_D_projection).convert_to_arr())
        self.basement_lines_history[1].append(Line(leg2_D_projection, leg3_D_projection).convert_to_arr())
        self.basement_lines_history[2].append(Line(leg3_D_projection, leg4_D_projection).convert_to_arr())
        self.basement_lines_history[3].append(Line(leg1_D_projection, leg4_D_projection).convert_to_arr())

        self.basement_lines_history[4].append(Line(LM_12, legs_center).convert_to_arr())
        self.basement_lines_history[5].append(Line(LM_23, legs_center).convert_to_arr())
        self.basement_lines_history[6].append(Line(LM_34, legs_center).convert_to_arr())
        self.basement_lines_history[7].append(Line(LM_14, legs_center).convert_to_arr())

    def add_leg_lines(self, leg1, leg2, leg3, leg4):
        i = 0
        for leg in [leg1, leg2, leg3, leg4]:
            self.leg_lines_history[4 * i].append(Line(leg.O, leg.A).convert_to_arr())
            self.leg_lines_history[4 * i + 1].append(Line(leg.A, leg.B).convert_to_arr())
            self.leg_lines_history[4 * i + 2].append(Line(leg.B, leg.C).convert_to_arr())
            self.leg_lines_history[4 * i + 3].append(Line(leg.C, leg.D).convert_to_arr())
            i += 1

    @property
    def lines_history(self):
        self._lines_history.extend(self.body_lines_history[:])
        self._lines_history.extend(self.leg_lines_history)
        self._lines_history.extend(self.line_mass_weight_history)
        self._lines_history.extend(self.basement_lines_history)
        self._lines_history.extend(self.unsupporting_leg_lines_history)
        return self._lines_history

    def add_angles_snapshot(self, leg1, leg2, leg3, leg4):
        # angles are : gamma1, beta1, alpha1, tetta1, gamma2, beta2, alpha2, tetta2 ...
        # for leg1 tetta = 45 means 0 for servo
        # leg2 tetta = -45, leg3 tetta = -135, leg4 tetta = 135

        position = []
        for leg in [leg1, leg2, leg3, leg4]:
            position.append(round(rad_to_angle(leg.gamma) + phi_angle, 2))
            position.append(round(rad_to_angle(leg.beta), 2))
            position.append(-1 * round(rad_to_angle(leg.alpha), 2))
            tetta = rad_to_angle(leg.tetta)
            if leg == leg1:
                tetta -= 45
            if leg == leg2:
                tetta += 45
            if leg == leg3:
                tetta += 135
            if leg == leg4:
                tetta -= 135
            if tetta > 270:
                tetta -= 360
                print('Got tetta {0}'.format(tetta))
            tetta = round(tetta, 2)
            position.append(tetta)
        self.angles_history.append(position)


#################################################################


class Leg:
    def __init__(self, number, name, O, D, alpha, beta, gamma, a, b, c, d):
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
        self.a = a
        self.b = b
        self.c = c
        self.d = d
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
        angles_pref = [self.alpha, self.beta, self.gamma]

        tetta = math.atan2(D.y - O.y, D.x - O.x)
        A = Point(O.x + self.d * cos(tetta), O.y + self.d * sin(tetta), O.z)
        l = math.sqrt((D.x - A.x) ** 2 + (D.y - A.y) ** 2)
        delta_z = D.z - O.z
        best_angles = self.get_leg_angles(l, delta_z, angles_pref)
        alpha, beta, gamma = best_angles[0], best_angles[1], best_angles[2]

        Bx = self.a * cos(alpha)
        By = self.a * sin(alpha)
        Cx = Bx + self.b * cos(alpha + beta)
        Cy = By + self.b * sin(alpha + beta)
        Dx = Cx + self.c * cos(alpha + beta + gamma)
        Dy = Cy + self.c * sin(alpha + beta + gamma)
        if abs(Dx - l) > 0.01 or abs(Dy - delta_z) > 0.01:
            print('WTF')

        B_xz = [self.a * cos(alpha), self.a * sin(alpha)]
        C_xz = [B_xz[0] + self.b * cos(alpha + beta), B_xz[1] + self.b * sin(alpha + beta)]
        D_xz = [C_xz[0] + self.c * cos(alpha + beta + gamma), C_xz[1] + self.c * sin(alpha + beta + gamma)]

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

    def get_leg_angles(self, delta_x, delta_z, angles_pref):
        #print('Looking for angles for ({0}, {1})'.format(delta_x, delta_z))
        possible_angles = self.find_angles(delta_x, delta_z)

        for item in possible_angles:
            alpha = item[0]
            beta = item[1]
            gamma = item[2]
            Bx = self.a * cos(alpha)
            By = self.a * sin(alpha)
            Cx = Bx + self.b * cos(alpha + beta)
            Cy = By + self.b * sin(alpha + beta)
            Dx = Cx + self.c * cos(alpha + beta + gamma)
            Dy = Cy + self.c * sin(alpha + beta + gamma)
            if abs(Dx - delta_x) > 0.01 or abs(Dy - delta_z) > 0.01:
                print('WTF')

        return get_best_angles(angles_pref, possible_angles)

    def find_angles(self, Dx, Dy):
        results = []
        full_dist = math.sqrt(Dx ** 2 + Dy ** 2)
        if full_dist > self.a + self.b + self.c:
            # print('No decisions. Full distance : {0}'.format(full_dist))
            raise Exception('No decisions. Full distance : {0}'.format(full_dist))
            # sys.exit(1)

        # for k in np.arange(-35.0, 35.0, 0.1):
        for k in np.arange(-45.0, 45.0, 0.5):
            ksi = angle_to_rad(k)

            Cx = Dx + self.c * math.cos(math.pi / 2 + ksi)
            Cy = Dy + self.c * math.sin(math.pi / 2 + ksi)
            dist = math.sqrt(Cx ** 2 + Cy ** 2)

            if dist > self.a + self.b or dist < abs(self.a - self.b):
                pass
            else:
                # print('Ksi : {0}'.format(k))
                alpha1 = math.acos((self.a ** 2 + dist ** 2 - self.b ** 2) / (2 * self.a * dist))
                beta1 = math.acos((self.a ** 2 + self.b ** 2 - dist ** 2) / (2 * self.a * self.b))
                beta = -1 * (pi - beta1)

                alpha2 = math.atan2(Cy, Cx)
                alpha = alpha1 + alpha2

                Bx = self.a * cos(alpha)
                By = self.a * sin(alpha)

                BD = math.sqrt((Dx - Bx) ** 2 + (Dy - By) ** 2)
                angle_C = math.acos((self.b ** 2 + self.c ** 2 - BD ** 2) / (2 * self.b * self.c))

                for coef in [-1, 1]:
                    gamma = coef * (pi - angle_C)

                    Cx = Bx + self.b * cos(alpha + beta)
                    Cy = By + self.b * sin(alpha + beta)
                    new_Dx = Cx + self.c * cos(alpha + beta + gamma)
                    new_Dy = Cy + self.c * sin(alpha + beta + gamma)
                    if abs(new_Dx - Dx) > 0.01 or abs(new_Dy - Dy) > 0.01:
                        continue

                    results.append([alpha, beta, gamma])

        return results


def angles_str(angles):
    result = ''
    for item in angles:
        result += '{0} '.format(round(180 * item / pi, 2))
    return result


def get_best_angles(angles_pref, all_angles):
    min_distance = 1000
    best_angles = None
    print_angles = False
    for item in all_angles:
        #print(angles_str(item))
        alpha = item[0]
        beta = item[1]
        gamma = item[2]

        cur_distance = get_angles_distance_2(item)
        # print('Angles : {0}. Distance : {1}'.format(angles_str(item), cur_distance))
        if cur_distance <= min_distance:
            min_distance = cur_distance
            best_angles = item[:]
    # print(angles_str(best_angles), min_distance)
    if best_angles is None:
        #print('No suitable angles found. Halt')
        raise Exception('No angles')
        # sys.exit(1)
    #distance = get_angles_distance(best_angles, angles_pref)
    #if distance > 2.5:
    #    print(distance)
    return best_angles





def get_angles_distance(angles1, angles2):
    return math.sqrt((angles1[0] - angles2[0]) ** 2 +
                     (angles1[1] - angles2[1]) ** 2 +
                     (angles1[2] - angles2[2]) ** 2)


def get_angles_distance_2(angles1):
    return math.sqrt((angles1[0] - angle_to_rad(target_1)) ** 2 +
                     (angles1[0] + angles1[1] - angle_to_rad(target_2)) ** 2 +
                     (angles1[0] + angles1[1] + angles1[2] - angle_to_rad(target_3)) ** 2)

###########################################################################


class MovementSequence:
    def __init__(self, Leg1, Leg2, Leg3, Leg4, step=0.5):
        self.step = step
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
        self.calculate_unsupporting_leg()
        self.save_angles()
        self.log_movement_history()

    def log_movement_history(self):
        self.mh.add_leg_lines(self.Leg1, self.Leg2, self.Leg3, self.Leg4)
        self.mh.add_body_lines(self.Leg1.O, self.Leg2.O, self.Leg3.O, self.Leg4.O)
        wm1 = Point(self.mass_center[0], self.mass_center[1], self.Leg1.O.z)
        wm2 = Point(self.mass_center[0], self.mass_center[1], self.ground_z)
        self.mh.add_mw_lines(wm1, wm2)
        self.mh.add_basement_lines(self.Leg1.D, self.Leg2.D, self.Leg3.D, self.Leg4.D, self.ground_z)
        self.mh.add_unsup_leg_line(self.unsupporting_leg.D)

        # LM - legs middle point, LM_12 - middle of legs 1 and 2
        # ALL projected to self.ground_z
    def calculate_unsupporting_leg(self):
        self.mass_center = self.calculate_mass_center()
        mass_center_xy = self.mass_center
        legs_center = self.calculate_basement_points()
        # LM_12 - middle of line between legs 1 and 2
        LM_12 = Point((self.Leg1.D.x + self.Leg2.D.x) / 2,
                      (self.Leg1.D.y + self.Leg2.D.y) / 2,
                      self.ground_z)
        LM_23 = Point((self.Leg2.D.x + self.Leg3.D.x) / 2,
                      (self.Leg2.D.y + self.Leg3.D.y) / 2,
                      self.ground_z)
        LM_34 = Point((self.Leg3.D.x + self.Leg4.D.x) / 2,
                      (self.Leg3.D.y + self.Leg4.D.y) / 2,
                      self.ground_z)
        LM_14 = Point((self.Leg1.D.x + self.Leg4.D.x) / 2,
                      (self.Leg1.D.y + self.Leg4.D.y) / 2,
                      self.ground_z)

        LF_12 = LinearFunc(point1=legs_center, point2=LM_12)
        LF_23 = LinearFunc(point1=legs_center, point2=LM_23)
        LF_34 = LinearFunc(point1=legs_center, point2=LM_34)
        LF_14 = LinearFunc(point1=legs_center, point2=LM_14)

        x, y = mass_center_xy[0], mass_center_xy[1]
        #self.mass_center_distance = [round(legs_center.x - x, 3), round(legs_center.y - y, 3)]

        if LF_14.get_x(y) <= x and LF_12.get_y(x) <= y:
            self.unsupporting_leg = self.Leg3
            #sector = 1
        if LF_23.get_x(y) <= x and LF_12.get_y(x) > y:
            self.unsupporting_leg = self.Leg4
            #sector = 2
        if LF_23.get_x(y) > x and LF_34.get_y(x) > y:
            self.unsupporting_leg = self.Leg1
            #sector = 3
        if LF_14.get_x(y) > x and LF_34.get_y(x) <= y:
            self.unsupporting_leg = self.Leg2
            #sector = 4

        if self.target_unsupporting_leg is None:
            pass
            #print('No target_unsupporting_leg')
        else:
        #try:
            target_leg_sector = define_sector(LF_12, LF_23, LF_34, LF_14,
                                   self.target_unsupporting_leg.D.x,
                                   self.target_unsupporting_leg.D.y)
            if target_leg_sector == 1:
                distance_1 = distance_to_line(self.mass_center[0], self.mass_center[1], LF_23, 3, 1)
                distance_2 = distance_to_line(self.mass_center[0], self.mass_center[1], LF_34, 3, 0)
            if target_leg_sector == 2:
                distance_1 = distance_to_line(self.mass_center[0], self.mass_center[1], LF_14, 4, 1)
                distance_2 = distance_to_line(self.mass_center[0], self.mass_center[1], LF_34, 4, 0)
            if target_leg_sector == 3:
                distance_1 = distance_to_line(self.mass_center[0], self.mass_center[1], LF_14, 1, 1)
                distance_2 = distance_to_line(self.mass_center[0], self.mass_center[1], LF_12, 1, 0)
            if target_leg_sector == 4:
                distance_1 = distance_to_line(self.mass_center[0], self.mass_center[1], LF_23, 2, 1)
                distance_2 = distance_to_line(self.mass_center[0], self.mass_center[1], LF_12, 2, 0)
            self.distances_to_margin = [abs(distance_1 - mc_magrin), abs(distance_2 - mc_magrin)]

    def body_movement(self, delta_x, delta_y, delta_z, leg_up=None, leg_up_delta=[0, 0, 0]):
        if delta_x == delta_y == delta_z == 0:
            #print('No movement required')
            return
        max_delta = max(abs(delta_x), abs(delta_y), abs(delta_z),
                        abs(leg_up_delta[0]), abs(leg_up_delta[1]), abs(leg_up_delta[2]))

        num_steps = int(max_delta / self.step)
        _delta_x = round(delta_x / num_steps, 4)
        _delta_y = round(delta_y / num_steps, 4)
        _delta_z = round(delta_z / num_steps, 4)
        _end_delta_x = round(leg_up_delta[0] / num_steps, 4)
        _end_delta_y = round(leg_up_delta[1] / num_steps, 4)
        _end_delta_z = round(leg_up_delta[2] / num_steps, 4)

        for m in range(num_steps):
            #print('----------------------------- next step ------------------------------')
            ms1 = copy.deepcopy(self)
            if leg_up == self.Leg1:
                self.Leg1.move_both_points(_delta_x, _delta_y, _delta_z,
                                           _end_delta_x, _end_delta_y, _end_delta_z)
            else:
                self.Leg1.move_mount_point(_delta_x, _delta_y, _delta_z)

            if leg_up == self.Leg2:
                self.Leg2.move_both_points(_delta_x, _delta_y, _delta_z,
                                           _end_delta_x, _end_delta_y, _end_delta_z)
            else:
                self.Leg2.move_mount_point(_delta_x, _delta_y, _delta_z)

            if leg_up == self.Leg3:
                self.Leg3.move_both_points(_delta_x, _delta_y, _delta_z,
                                           _end_delta_x, _end_delta_y, _end_delta_z)
            else:
                self.Leg3.move_mount_point(_delta_x, _delta_y, _delta_z)

            if leg_up == self.Leg4:
                self.Leg4.move_both_points(_delta_x, _delta_y, _delta_z,
                                           _end_delta_x, _end_delta_y, _end_delta_z)
            else:
                self.Leg4.move_mount_point(_delta_x, _delta_y, _delta_z)

            for leg1 in [self.Leg1, self.Leg2, self.Leg3, self.Leg4]:
                for leg2 in [ms1.Leg1, ms1.Leg2, ms1.Leg3, ms1.Leg4]:
                    if leg1.number == leg2.number:
                        deltas = [0, 0, 0]
                        if leg_up == leg1:
                            deltas = [_end_delta_x, _end_delta_y, _end_delta_z]
                        if abs(leg1.D.x - leg2.D.x + deltas[0]) > 0.1 \
                           or abs(leg1.D.y - leg2.D.y + deltas[1]) > 0.1 \
                           or abs(leg1.D.z - leg2.D.z + deltas[2]) > 0.1:
                            print(leg1)
                            print(leg2)
                            raise Exception('Leg should not move! ({0}, {1}, {2})'
                                            .format(leg1.D.x - leg2.D.x + deltas[0],
                                                    leg1.D.y - leg2.D.y + deltas[1],
                                                    leg1.D.z - leg2.D.z + deltas[2]))

            self.post_movement_actions()

    def body_to_center(self):
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

        self.body_movement(avg_d_x - avg_o_x, avg_d_y - avg_o_y, 0)

    def turn_body(self, angle):
        num_steps = int(abs(angle / turn_angle))
        step_angle = round(angle / num_steps, 4)

        for m in range(num_steps):
            for leg in self.Legs:
                x_new, y_new = turn_on_angle(leg.O.x, leg.O.y, step_angle)
                delta_x = x_new - leg.O.x
                delta_y = y_new - leg.O.y
                leg.move_mount_point(delta_x, delta_y, 0)
            self.post_movement_actions()

    @property
    def lines_history(self):
        return self.mh.lines_history

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

    def leg_movement(self, leg_num, leg_delta):
        if leg_num == 1:
            leg = self.Leg1
        elif leg_num == 2:
            leg = self.Leg2
        elif leg_num == 3:
            leg = self.Leg3
        elif leg_num == 4:
            leg = self.Leg4

        max_delta = max(abs(x) for x in leg_delta)
        num_steps = int(max_delta / self.step)
        leg_delta = [round(x / num_steps, 4) for x in leg_delta]
        for m in range(num_steps):
            for my_leg in [self.Leg1, self.Leg2, self.Leg3, self.Leg4]:
                if my_leg == leg:
                    #self._leg_move(my_leg, leg_delta)
                    my_leg.move_end_point(leg_delta[0], leg_delta[1], leg_delta[2])
                else:
                    #self._leg_move(my_leg, None)
                    my_leg.move_end_point(0, 0, 0)
            self.post_movement_actions()

    @staticmethod
    def _leg_move(Leg, delta=None):
        if delta is None:
            Leg.move_end_point(0, 0, 0)
        else:
            Leg.move_end_point(delta[0], delta[1], delta[2])

    def print_to_sequence_file(self):
        with open(sequence_file, 'w') as f:
            f.write('\n'.join(str(x) for x in self.mh.angles_history))

    def run_animation(self):
        animate(self.lines_history)


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


def create_new_ms(step=0.5, ms_array=None):

    a = 10.5
    b = 5.4
    c = 11.1
    d = 5.4

    if ms_array is None:
        O1 = Point(4.0, 4.0, 0)
        D1 = Point(k, k, ground_z)
        Leg1 = Leg(1, "Leg1", O1, D1, angle_to_rad(start_alpha), angle_to_rad(start_beta), angle_to_rad(start_gamma),
                   a, b, c, d)

        O2 = Point(4.0, -4.0, 0)
        D2 = Point(k, -k, ground_z)
        Leg2 = Leg(2, "Leg2", O2, D2, angle_to_rad(start_alpha), angle_to_rad(start_beta), angle_to_rad(start_gamma),
                   a, b, c, d)

        O3 = Point(-4.0, -4.0, 0)
        D3 = Point(-k, -k, ground_z)
        Leg3 = Leg(3, "Leg3", O3, D3, angle_to_rad(start_alpha), angle_to_rad(start_beta), angle_to_rad(start_gamma),
                   a, b, c, d)

        O4 = Point(-4.0, 4.0, 0)
        D4 = Point(-k, k, ground_z)
        Leg4 = Leg(4, "Leg4", O4, D4, angle_to_rad(start_alpha), angle_to_rad(start_beta), angle_to_rad(start_gamma),
                   a, b, c, d)
    else:
        for i in range(4):
            leg = ms_array[i]
            O = Point(leg[0], leg[1], leg[2])
            D = Point(leg[3], leg[4], leg[5])
            if i == 0:
                Leg1 = Leg(1, "Leg1", O, D, leg[6], leg[7], leg[8])
            if i == 1:
                Leg2 = Leg(2, "Leg2", O, D, leg[6], leg[7], leg[8])
            if i == 2:
                Leg3 = Leg(3, "Leg3", O, D, leg[6], leg[7], leg[8])
            if i == 3:
                Leg4 = Leg(4, "Leg4", O, D, leg[6], leg[7], leg[8])

    return MovementSequence(Leg1, Leg2, Leg3, Leg4, step=step)


def body_compensation(ms, leg_num, return_value=0):
    ms1 = copy.deepcopy(ms)
    if leg_num == 1:
        leg = ms1.Leg1
    elif leg_num == 2:
        leg = ms1.Leg2
    elif leg_num == 3:
        leg = ms1.Leg3
    elif leg_num == 4:
        leg = ms1.Leg4

    ms1.target_unsupporting_leg = leg
    ms1.calculate_unsupporting_leg()

    total_results = []
    prev_best_result = 0
    for i in range(30):
        if i == 0:
            results = compensation_iteration_v2(ms1, i+1)
        else:
            results = compensation_iteration_v2(ms1, i+1, best_i, best_j)
        results = sorted(results, key=lambda a_entry: a_entry[0])
        best_i = results[0][1]
        best_j = results[0][2]
        total_results.extend(results)
        #print('Best results : {0}'.format(results[0]))
        if abs(results[0][0] - prev_best_result) < 0.001:
            #print('No more movement made')
            break
        prev_best_result = results[0][0]
    total_results = sorted(total_results, key=lambda a_entry: a_entry[0])

    for item in total_results:
        #print('Checking {0}'.format(item))
        #if item[0] > 1:
        if item[0] > 1:
            raise Exception('Bad attempt : {0}'.format(item[0]))
        try:
            ms2 = copy.deepcopy(ms1)
            ms2.body_movement(item[1], item[2], 0)
            #print('Best move : ({0}, {1})'.format(item[1], item[2]))
            if item[1] == 0 and item[2] == 0:
                if return_value == 0:
                    pass
                else:
                    return [item[1], item[2]]
            else:
                if return_value == 0:
                    ms.body_movement(item[1], item[2], 0)
                else:
                    return [item[1], item[2]]
            break
        except:
            continue


def compensation_iteration_v2(ms1, iternum, x=0, y=0):
    results = []
    step = 0.5
    mult = 5

    tries_x = np.arange(x - mult*step, x + mult*step + 0.1, step)
    tries_y = np.arange(y - mult*step, y + mult*step + 0.1, step)

    for i in tries_x:
        for j in tries_y:
            #print('Trying Move ({0}, {1})'.format(i, j))
            ms2 = copy.deepcopy(ms1)
            try:
                for leg in ms2.Legs:
                    #print('Leg : {0}'.format(leg.number))
                    leg.move_mount_point(i, j, 0)
                    leg.calculate_angles()
            except:
                #print('Failed')
                continue

            ms2.calculate_unsupporting_leg()
            distance = ms2.distances_to_margin[0] + ms2.distances_to_margin[1]
            #print('Succesful. Distance : {0}'.format(distance))
            results.append([distance, i, j])

    return results


def compensated_leg_movement(ms, leg_num, leg_delta):
    if leg_num == 1:
        leg = ms.Leg1
    elif leg_num == 2:
        leg = ms.Leg2
    elif leg_num == 3:
        leg = ms.Leg3
    elif leg_num == 4:
        leg = ms.Leg4

    max_delta = max(abs(x) for x in leg_delta)
    num_steps = int(max_delta / ms.step)
    leg_delta = [round(x / num_steps, 4) for x in leg_delta]
    for m in range(num_steps):
        ms2 = copy.deepcopy(ms)
        for my_leg in [ms2.Leg1, ms2.Leg2, ms2.Leg3, ms2.Leg4]:
            if my_leg == leg:
                my_leg.move_end_point(leg_delta[0], leg_delta[1], leg_delta[2])
            else:
                my_leg.move_end_point(0, 0, 0)
        ms2.post_movement_actions()
        required_compensation = body_compensation(ms2, leg_num, 1)

        for my_leg in [ms.Leg1, ms.Leg2, ms.Leg3, ms.Leg4]:
            if my_leg == leg:
                my_leg.move_end_point(leg_delta[0], leg_delta[1], leg_delta[2])
            else:
                my_leg.move_end_point(0, 0, 0)
            my_leg.move_mount_point(required_compensation[0], required_compensation[1], 0)
        ms.post_movement_actions()


def leg_move_with_compensation(ms, leg_num, delta_x, delta_y):
    print('Leg {0} started'.format(leg_num))
    body_compensation(ms, leg_num)
    #compensated_leg_movement(ms, leg_num, [0, 0, z_up])
    #compensated_leg_movement(ms, leg_num, [delta_x, delta_y, 0])
    compensated_leg_movement(ms, leg_num, [delta_x, delta_y, z_up])
    compensated_leg_movement(ms, leg_num, [0, 0, -z_up])


def turn_body(ms, angle_deg):
    angle = angle_to_rad(angle_deg)
    # move leg one by one
    for leg in [ms.Leg1, ms.Leg2, ms.Leg3, ms.Leg4]:
        x_new, y_new = turn_on_angle(leg.D.x, leg.D.y, angle)
        delta_x = x_new - leg.D.x
        delta_y = y_new - leg.D.y
        leg_move_with_compensation(ms, leg.number, delta_x, delta_y)

    ms.body_to_center()

    ms.turn_body(angle)


def move_body_straight(ms, delta_x, delta_y, leg_seq=[1, 2, 3, 4], body_to_center=False):
    for leg in leg_seq:
        leg_move_with_compensation(ms, leg, delta_x, delta_y)
    if body_to_center:
        ms.body_to_center()

"""
for _i in [2, 4, 5, 6, 7, 8]:
    for _k in [16, 18, 20, 22]:
        for _z in [-5, -10, -15, -20]:
            for _a in [8.5, 10.5, 12.5]:
                for _b in [5.5, 7.5, 9.5]:
                    for _seq in [[3, 1, 2, 4], [1, 2, 3, 4], [3, 4, 1, 2]]:
                        try:
                            print('--------------')
                            print('Trying I = {0}. k = {1}. ground_z = {2}, b = {3}'.format(_i, _k, _z, _b))
                            a = _a
                            b = _b
                            c = 21.5
                            d = 5.5
                            ground_z = _z
                            k = _k
                            ms = create_new_ms()
                            #turn_body(ms, _i)
                            move_body_straight(ms, _i, _i, leg_seq=_seq)
                            #print('Succeeded I = {0}. k = {1}. ground_z = {2}, b = {3}'.format(_i, _k, _z, _b))
                            with open(tmp_file, 'a') as f:
                                f.write('1,{0},{1},{2},{3},{4},{5},{6}\n'
                                        .format(_i,
                                                ''.join(str(x) for x in _seq),
                                                _k,
                                                _z,
                                                _a,
                                                _b,
                                                len(ms.lines_history[0])))
                        except:
                            with open(tmp_file, 'a') as f:
                                f.write('0,{0},{1},{2},{3},{4},{5},0\n'
                                        .format(_i,
                                                ''.join(str(x) for x in _seq),
                                                _k,
                                                _z,
                                                _a,
                                                _b))
"""

ms = create_new_ms(step=0.5)
#print(ms_to_array(ms))

z = 6


try:
    #print('------------------------------------------------------- 1 ------------------------------------------------')
    #ms.body_movement(0, 0, z)
    #print('------------------------------------------------------- 2 ------------------------------------------------')
    #move_body_straight(ms, 7, 0, leg_seq=[3, 4, 1, 2])
    #move_body_straight(ms, 0, 7, leg_seq=[1, 2, 3, 4])
    #move_body_straight(ms, -5, 5, leg_seq=[3, 4, 1, 2], body_to_center=True)
    #move_body_straight(ms, -8, 0, leg_seq=[4, 3, 2, 1], body_to_center=True)
    #move_body_straight(ms, 0, -8, leg_seq=[2, 3, 1, 4], body_to_center=True)
    #move_body_straight(ms, 8, 0, leg_seq=[1, 2, 3, 4], body_to_center=True)
    turn_body(ms, 30)
    #ms.body_to_center()
    #ms.body_movement(0, 0, -z)
    ms.print_to_sequence_file()
except:
    pass
    print('Fail')


ms.run_animation()
