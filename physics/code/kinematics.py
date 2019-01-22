import math
import sys
from math import pi, sin, cos
import random
sys.path.append('/nexus/fenix/fenix/')
import numpy as np


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
    return rad * 180/pi

"""
a = 10.5
b = 5.5
c = 15
d = 5.5
"""
a = 10.5
b = 5.5
c = 14.5
d = 5.5

phi_angle = 15
phi = angle_to_rad(phi_angle)

body_weight = 300
leg_CD_weight = 250
leg_BC_weight = 50
leg_AB_weight = 150
leg_OA_weight = 50

start_gamma = -55
start_beta = -60
start_alpha = 25


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


class Leg:
    def __init__(self, name, O, D, alpha, beta, gamma):
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
        self.lines_history = [[], [], [], []]
        self.get_all_angles()
        #print(self)

    def __str__(self):
        return '{0}. O: {1} -> A: {2} -> B: {3} -> C: {4} -> D: {5}. Angles : {6}'\
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

    def save_lines_history(self):
        self.lines_history[0].append(Line(self.O, self.A).convert_to_arr())
        self.lines_history[1].append(Line(self.A, self.B).convert_to_arr())
        self.lines_history[2].append(Line(self.B, self.C).convert_to_arr())
        self.lines_history[3].append(Line(self.C, self.D).convert_to_arr())

    def move_point(self, point, delta_x, delta_y, delta_z):
        point.x += delta_x
        point.y += delta_y
        point.z += delta_z

    def move_mount_point(self, delta_x, delta_y, delta_z):
        self.move_point(self.O, delta_x, delta_y, delta_z)
        self.get_all_angles()

    def move_end_point(self, delta_x, delta_y, delta_z):
        self.move_point(self.D, delta_x, delta_y, delta_z)
        self.get_all_angles()

    # means one leg is raised and moves with the body
    # end_delta = 0 means that leg is not moving, else it is also moving somehow
    def move_both_points(self, delta_x, delta_y, delta_z, end_delta_x, end_delta_y, end_delta_z):
        self.move_point(self.O, delta_x, delta_y, delta_z)
        self.move_point(self.D,
                        delta_x + end_delta_x,
                        delta_y + end_delta_y,
                        delta_z + end_delta_z)
        self.get_all_angles()

    # angles_pref = [alpha_pref, beta_pref, gamma_pref]
    def get_all_angles(self):
        O = self.O
        D = self.D
        angles_pref = [self.alpha, self.beta, self.gamma]

        tetta = math.atan2(D.y - O.y, D.x - O.x)
        A = Point(O.x + d * cos(tetta), O.y + d * sin(tetta), O.z)
        l = math.sqrt((D.x - A.x) ** 2 + (D.y - A.y) ** 2)
        delta_z = D.z - O.z
        best_angles = get_leg_angles(l, delta_z, angles_pref)
        alpha, beta, gamma = best_angles[0], best_angles[1], best_angles[2]

        B_xz = [a * cos(alpha), a * sin(alpha)]
        C_xz = [B_xz[0] + b * cos(alpha + beta), B_xz[1] + b * sin(alpha + beta)]
        D_xz = [C_xz[0] + c * cos(alpha + beta + gamma), C_xz[1] + c * sin(alpha + beta + gamma)]

        #print('XZ-projection. B : {0}. C : {1}. D : {2}.'.format(B_xz, C_xz, D_xz))
        self.A = A
        self.B = Point(A.x + B_xz[0] * cos(tetta), A.y + B_xz[0] * sin(tetta), A.z + B_xz[1])
        self.C = Point(A.x + C_xz[0] * cos(tetta), A.y + C_xz[0] * sin(tetta), A.z + C_xz[1])
        self.D = Point(A.x + D_xz[0] * cos(tetta), A.y + D_xz[0] * sin(tetta), A.z + D_xz[1])
        #print('XYZ-projection. B : {0}. C : {1}. D : {2}.'.format(self.B, self.C, self.D))

        self.tetta, self.alpha, self.beta, self.gamma = tetta, alpha, beta, gamma
        self.save_lines_history()


def get_leg_angles(delta_x, delta_z, angles_pref):
    possible_angles = find_angles(delta_x, delta_z)
    return get_best_angles(angles_pref, possible_angles)


def angles_str(angles):
    result = ''
    for item in angles:
        result += '{0} '.format(round(180*item/pi, 2))
    return result


def get_best_angles(angles_pref, all_angles):
    min_distance = 1000
    best_angles = None
    print_angles = False
    for item in all_angles:
        #print(angles_str(item))
        if item[0] < angle_to_rad(-60) or item[0] > angle_to_rad(80):
            if print_angles:
                print('Bad alpha : {0}'.format(rad_to_angle(item[0])))
            continue
        if item[1] < angle_to_rad(-120) or item[1] > angle_to_rad(60):
            if print_angles:
                print('Bad beta : {0}'.format(rad_to_angle(item[1])))
            continue
        if (item[0] + item[1] < angle_to_rad(-90)) or (item[0] + item[1] > angle_to_rad(60)):
            if print_angles:
                print('Bad alpha + beta : {0}'.format(rad_to_angle(item[0] + item[1])))
            continue
        if item[2] < angle_to_rad(-120) or item[2] > angle_to_rad(15): # !!! changed 90 to 0. Mb it should be -15
            if print_angles:
                print('Bad gamma : {0}'.format(rad_to_angle(item[2])))
            continue
        if (item[0] + item[1] + item[2] < angle_to_rad(-120)) or (item[0] + item[1] + item[2] > angle_to_rad(-60)):
            if print_angles:
                print('Bad alpha + beta + gamma : {0}'.format(rad_to_angle(item[0] + item[1] + item[2])))
            continue
        cur_distance = get_angles_distance(item, angles_pref)
        #print('Angles : {0}. Distance : {1}'.format(angles_str(item), cur_distance))
        if cur_distance <= min_distance:
            min_distance = cur_distance
            best_angles = item[:]
    #print(angles_str(best_angles), min_distance)
    if best_angles is None:
        print('No suitable angles found. Halt')
        #sys.exit(1)
    return best_angles


def find_angles(Dx, Dy):
    results = []
    full_dist = math.sqrt(Dx ** 2 + Dy ** 2)
    if full_dist > a + b + c:
        print('No decisions')
        sys.exit(1)

    #for k in range(-70, 71, 1):
    for k in np.arange(-70.0, 70.0, 0.25):
        ksi = angle_to_rad(k)

        Cx = Dx + c * math.cos(math.pi / 2 + ksi)
        Cy = Dy + c * math.sin(math.pi / 2 + ksi)
        dist = math.sqrt(Cx ** 2 + Cy ** 2)

        if dist > a + b or dist < abs(a - b):
            pass
        else:
            #print('Ksi : {0}'.format(k))
            alpha1 = math.acos((a ** 2 + dist ** 2 - b ** 2) / (2 * a * dist))
            beta1 = math.acos((a ** 2 + b ** 2 - dist ** 2) / (2 * a * b))
            beta = -1 * (pi - beta1)

            alpha2 = math.atan2(Cy, Cx)
            alpha = alpha1 + alpha2

            Bx = a * cos(alpha)
            By = a * sin(alpha)

            BD = math.sqrt((Dx - Bx) ** 2 + (Dy - By) ** 2)
            angle_C = math.acos((b**2 + c**2 - BD**2) / (2*b*c))

            for coef in [-1, 1]:
                gamma = coef * (pi - angle_C)

                Cx = Bx + b * cos(alpha + beta)
                Cy = By + b * sin(alpha + beta)
                new_Dx = Cx + c * cos(alpha + beta + gamma)
                new_Dy = Cy + c * sin(alpha + beta + gamma)
                if abs(new_Dx - Dx) > 0.1 or abs(new_Dy - Dy) > 0.1:
                    continue

                results.append([alpha, beta, gamma])

    return results


def get_angles_distance(angles1, angles2):
    # weight of gamma is 1.5 !!!
    return math.sqrt((angles1[0] - angles2[0]) ** 2 +
                     (angles1[1] - angles2[1]) ** 2 +
                     1.5 * (angles1[2] - angles2[2]) ** 2)


class LinearFunc:
    def __init__(self, point1, point2):
        delta_x = (point2.x - point1.x)
        if delta_x == 0:
            delta_x = 0.00001
        self.k = (point2.y - point1.y) / delta_x
        self.b = (point2.x * point1.y - point1.x * point2.y) / delta_x

    def get_y(self, x):
        return self.k * x + self.b

    def get_x(self, y):
        return (y - self.b) / self.k


def calculate_intersection(func1, func2):
    x = (func1.b - func2.b) / (func2.k - func1.k)
    y = func1.k*x + func1.b
    return [x, y]


class movement_sequence:
    def __init__(self, Leg1, Leg2, Leg3, Leg4, step=0.5):
        self.step = step
        self.ground_z = -10
        self.result = 1
        self.unsupporting_leg = None

        self._lines_history = []
        self.body_lines_history = [[], [], [], []]
        self.line_mass_weight_history = [[]]
        self.basement_lines_history = [[], [], [], [], [], [], [], []]
        self.unsupporting_leg_lines_history = [[]]
        self.angles_history = []
        self.Leg1 = Leg1
        self.Leg2 = Leg2
        self.Leg3 = Leg3
        self.Leg4 = Leg4
        self.body_points_movement()

    # angles are : gamma1, beta1, alpha1, tetta1, gamma2, beta2, alpha2, tetta2 ...
    # for leg1 tetta = 45 means 0 for servo
    # leg2 tetta = -45, leg3 tetta = -135, leg4 tetta = 135
    def save_angles(self):
        position = []
        #for leg in [self.Leg1, self.Leg2, self.Leg3, self.Leg4]:
        for leg in [self.Leg1, self.Leg4, self.Leg3, self.Leg2]:
            position.append(round(rad_to_angle(leg.gamma), 2))
            position.append(round(rad_to_angle(leg.beta), 2))
            position.append(-1*round(rad_to_angle(leg.alpha), 2))
            tetta = rad_to_angle(leg.tetta)
            if leg == self.Leg1:
                tetta -= 45
            if leg == self.Leg2:
                tetta += 45
            if leg == self.Leg3:
                tetta += 135
            if leg == self.Leg4:
                tetta -= 135
            tetta = round(tetta, 2)
            position.append(tetta)
        #print('Angles : {0}'.format(position))
        #print('{0}\n{1}\n{2}\n{3}\n'.format(self.Leg1, self.Leg2, self.Leg3, self.Leg4))
        self.angles_history.append(position)

    def body_points_movement(self):
        self.body_lines_history[0].append(Line(self.Leg1.O, self.Leg2.O).convert_to_arr())
        self.body_lines_history[1].append(Line(self.Leg2.O, self.Leg3.O).convert_to_arr())
        self.body_lines_history[2].append(Line(self.Leg3.O, self.Leg4.O).convert_to_arr())
        self.body_lines_history[3].append(Line(self.Leg4.O, self.Leg1.O).convert_to_arr())

        mass_center = self.calculate_mass_center()
        wm1 = Point(mass_center[0], mass_center[1], self.Leg1.O.z)
        wm2 = Point(mass_center[0], mass_center[1], self.ground_z)
        self.line_mass_weight_history[0].append(Line(wm1, wm2).convert_to_arr())

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

        leg1_D_projection = Point(self.Leg1.D.x, self.Leg1.D.y, self.ground_z)
        leg2_D_projection = Point(self.Leg2.D.x, self.Leg2.D.y, self.ground_z)
        leg3_D_projection = Point(self.Leg3.D.x, self.Leg3.D.y, self.ground_z)
        leg4_D_projection = Point(self.Leg4.D.x, self.Leg4.D.y, self.ground_z)

        self.basement_lines_history[0].append(Line(leg1_D_projection, leg2_D_projection).convert_to_arr())
        self.basement_lines_history[1].append(Line(leg2_D_projection, leg3_D_projection).convert_to_arr())
        self.basement_lines_history[2].append(Line(leg3_D_projection, leg4_D_projection).convert_to_arr())
        self.basement_lines_history[3].append(Line(leg1_D_projection, leg4_D_projection).convert_to_arr())

        #self.basement_lines_history[4].append(Line(leg1_D_projection, leg3_D_projection).convert_to_arr())
        #self.basement_lines_history[5].append(Line(leg2_D_projection, leg4_D_projection).convert_to_arr())

        self.basement_lines_history[4].append(Line(LM_12, legs_center).convert_to_arr())
        self.basement_lines_history[5].append(Line(LM_23, legs_center).convert_to_arr())
        self.basement_lines_history[6].append(Line(LM_34, legs_center).convert_to_arr())
        self.basement_lines_history[7].append(Line(LM_14, legs_center).convert_to_arr())

        self.unsupporting_leg = self.calculate_unsupporting_leg(mass_center, legs_center, LM_12, LM_23, LM_34, LM_14)
        unsupporting_point_1 = self.unsupporting_leg.D
        unsupporting_point_2 = Point(self.unsupporting_leg.D.x, self.unsupporting_leg.D.y, self.unsupporting_leg.D.z + 10)
        self.unsupporting_leg_lines_history[0].append(Line(unsupporting_point_1, unsupporting_point_2).convert_to_arr())

        self.save_angles()
        self.check_supporting_leg()

    def check_supporting_leg(self):
        for leg in [self.Leg1, self.Leg2, self.Leg3, self.Leg4]:
            #print(leg)
            #print(self.unsupporting_leg)
            #print(round(leg.D.z, 2))
            if leg != self.unsupporting_leg and round(leg.D.z, 2) >= self.ground_z + 2:
                self.result = 0
                #print('Supporting leg went up, HALT! D : {0}'.format(leg.D))
                #print(leg)
                #sys.exit(0)

    # LM - legs middle point, LM_12 - middle of legs 1 and 2
    # ALL projected to self.ground_z
    def calculate_unsupporting_leg(self, mass_center_xy, LM, LM_12, LM_23, LM_34, LM_14):
        LF_12 = LinearFunc(LM, LM_12)
        LF_23 = LinearFunc(LM, LM_23)
        LF_34 = LinearFunc(LM, LM_34)
        LF_14 = LinearFunc(LM, LM_14)

        x, y = mass_center_xy[0], mass_center_xy[1]
        if LF_14.get_x(y) <= x and LF_12.get_y(x) <= y:
            return self.Leg3
        if LF_23.get_x(y) <= x and LF_12.get_y(x) > y:
            return self.Leg4
        if LF_23.get_x(y) > x and LF_34.get_y(x) > y:
            return self.Leg1
        if LF_14.get_x(y) > x and LF_34.get_y(x) <= y:
            return self.Leg2

    def body_movement(self, delta_x, delta_y, delta_z, leg_up=None, leg_up_delta=[0, 0, 0]):
        max_delta = max(abs(delta_x), abs(delta_y), abs(delta_z),
                        abs(leg_up_delta[0]), abs(leg_up_delta[1]), abs(leg_up_delta[2]))

        """
        # WTF mb dangerous
        if round(max_delta, 2) % round(self.step, 2) != 0:
            print('Bad delta : {0}. Div : {1}. Halt'.format(max_delta, round(max_delta % self.step, 2)))
            sys.exit(0)
        """
        num_steps = int(max_delta / self.step)
        _delta_x = round(delta_x / num_steps, 4)
        _delta_y = round(delta_y / num_steps, 4)
        _delta_z = round(delta_z / num_steps, 4)
        _end_delta_x = round(leg_up_delta[0] / num_steps, 4)
        _end_delta_y = round(leg_up_delta[1] / num_steps, 4)
        _end_delta_z = round(leg_up_delta[2] / num_steps, 4)
        for m in range(num_steps):
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

            self.body_points_movement()

    def leg_movement(self, leg, leg_delta):
        max_delta = max(abs(x) for x in leg_delta)
        """
        if max_delta % self.step != 0:
            print('Bad delta : {0}. Halt'.format(max_delta))
            sys.exit(0)
        """
        num_steps = int(max_delta / self.step)
        leg_delta = [round(x/num_steps, 4) for x in leg_delta]
        for m in range(num_steps):
            for my_leg in [self.Leg1, self.Leg2, self.Leg3, self.Leg4]:
                if my_leg == leg:
                    self._leg_move(my_leg, leg_delta)
                else:
                    self._leg_move(my_leg, None)
            self.body_points_movement()

    @staticmethod
    def _leg_move(Leg, delta=None):
        if delta is None:
            Leg.move_end_point(0, 0, 0)
        else:
            Leg.move_end_point(delta[0], delta[1], delta[2])

    @property
    def lines_history(self):
        self._lines_history.extend(self.body_lines_history[:])
        self._lines_history.extend(self.Leg1.lines_history)
        self._lines_history.extend(self.Leg2.lines_history)
        self._lines_history.extend(self.Leg3.lines_history)
        self._lines_history.extend(self.Leg4.lines_history)
        self._lines_history.extend(self.line_mass_weight_history)
        self._lines_history.extend(self.basement_lines_history)
        self._lines_history.extend(self.unsupporting_leg_lines_history)
        return self._lines_history

    # LM - legs middle point, LM12 - middle point between legs 1 and 2, and so on
    def calculate_basement_points(self):
        LF_13 = LinearFunc(self.Leg1.D, self.Leg3.D)
        LF_24 = LinearFunc(self.Leg2.D, self.Leg4.D)

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

        return [round(mass_center_x/weight_sum, 3), round(mass_center_y/weight_sum, 3)]

    def move_leg_gen(self, leg, leg_delta_x, leg_delta_y, body_delta_x, body_delta_y):
        self.leg_movement(leg, [0, 0, 10])
        self.body_movement(body_delta_x, body_delta_y, 0, leg_up=leg, leg_up_delta=[leg_delta_x, leg_delta_y, 0])
        self.leg_movement(leg, [0, 0, -10])

    def movement_specie(self):
        self.result = 1
        rnd_range = 10
        print('O start : {0}'.format(self.Leg1.O))
        step = 0
        for i in range(2):
            #for item in [self.Leg1, self.Leg3, self.Leg2, self.Leg4]:
            for item in [self.Leg1, self.Leg3, self.Leg2, self.Leg4]:
                if len(movement[step]) > 0:
                    r1, r2, r3 = movement[step][0], movement[step][1], movement[step][2]
                    r4, r5, r6 = movement[step][3], movement[step][4], movement[step][5]
                else:
                    r1 = int(random.randint(0, rnd_range) * 0.5)
                    r2 = int(random.randint(0, rnd_range) * 0.5)
                    r3 = int(random.randint(-rnd_range, rnd_range) * 0.5)
                    r4 = int(random.randint(-rnd_range, rnd_range) * 0.5)
                    r5 = int(random.randint(-rnd_range, rnd_range) * 0.5)
                    r6 = int(random.randint(-rnd_range, rnd_range) * 0.5)

                self.body_movement(r5, r6, 0)
                self.move_leg_gen(item, r1, r2, r3, r4)
                print('Step : {0}. R : {1}, {2}, {3}, {4}, {5}, {6}'.format(step, r1, r2, r3, r4, r5, r6))
                if self.result == 1:
                    movement[step] = [r1, r2, r3, r4, r5, r6]
                step += 1
        global abs_result
        abs_result = [round(self.Leg1.O.x - 4.5, 2), round(self.Leg1.O.y - 4.5, 2)]
        print('O finish : {0}'.format(self.Leg1.O))

    def print_to_sequence_file(self):
        with open(sequence_file, 'w') as f:
            f.write('\n'.join(str(x) for x in self.angles_history))

    def run_animation(self):
        animate(self.lines_history)


def create_new_ms(step=0.5):
    k = 18
    O1 = Point(4.5, 4.5, 0)
    D1 = Point(k, k, -10)
    Leg1 = Leg("Leg1", O1, D1, angle_to_rad(start_alpha), angle_to_rad(start_beta), angle_to_rad(start_gamma))

    O2 = Point(4.5, -4.5, 0)
    D2 = Point(k, -k, -10)
    Leg2 = Leg("Leg2", O2, D2, angle_to_rad(start_alpha), angle_to_rad(start_beta), angle_to_rad(start_gamma))

    O3 = Point(-4.5, -4.5, 0)
    D3 = Point(-k, -k, -10)
    Leg3 = Leg("Leg3", O3, D3, angle_to_rad(start_alpha), angle_to_rad(start_beta), angle_to_rad(start_gamma))

    O4 = Point(-4.5, 4.5, 0)
    D4 = Point(-k, k, -10)
    Leg4 = Leg("Leg4", O4, D4, angle_to_rad(start_alpha), angle_to_rad(start_beta), angle_to_rad(start_gamma))

    return movement_sequence(Leg1, Leg2, Leg3, Leg4, step=step)


class Res:
    def __init__(self, result, moves):
        self.result = result
        self.moves = moves

    def __str__(self):
        return 'Result : {0}. Moves : {1}'.format(self.result, self.moves)

# if movement is passed, creates a movement sequence for displaying it,
# else generates species
def genetics(attempts_total=10000, attempts_specie=1000, _movement=None, _step=0.5):
    global movement, abs_result
    result = 0
    abs_result = []
    attempts = 0
    attempts2 = 0
    if _movement is not None:
        movement = _movement[:]
        attempts_total = 1
        attempts_specie = 1
    else:
        movement = [[], [], [], [], [], [], [], []]
    results_list = []

    while attempts < attempts_total:
        print('Attempt #{0}.{1}'.format(attempts, attempts2))
        if attempts2 >= attempts_specie - 1:
            print('Reset movement')
            with open(tmp_file, 'a') as f:
                f.write('{0}\n'.format(Res(abs_result, movement)))
            movement = [[], [], [], [], [], [], [], []]
            attempts2 = 0
        print(movement)
        ms = create_new_ms(step=_step)
        try:
            ms.movement_specie()
            if ms.result == 1:
                results_list.append(Res(abs_result, movement))
                with open(tmp_file, 'a') as f:
                    f.write('{0}\n'.format(Res(abs_result, movement)))
                movement = [[], [], [], [], [], [], [], []]
                attempts2 = 0
        except:
            pass
        attempts += 1
        attempts2 += 1

    #for item in results_list:
    #    print(item)
    return ms


movement = [[4, 4, -3, 0, -1, -2], [0, 2, 3, -3, 3, 5], [2, 2, 4, 5, -3, -1], [0, 4, 1, 2, 3, -4],
            [5, 0, 2, -1, -1, -2], [3, 1, 3, 0, 2, 4], [2, 0, 0, 1, -4, -1], [2, 0, 1, 1, 5, -2]]

#ms = genetics(_movement=movement, _step=0.1)
ms = genetics(100000, 1000)
"""
ms = create_new_ms(0.1)
m = 7
ms.body_movement(m, m, 0)
ms.body_movement(-2*m, 0, 0)
ms.body_movement(0, -2*m, 0)
ms.body_movement(2*m, 0, 0)
ms.body_movement(-m, m, 0)
ms.body_movement(0, 0, 15)
ms.body_movement(0, 0, -15)

"""
ms.print_to_sequence_file()

#ms.run_animation()
