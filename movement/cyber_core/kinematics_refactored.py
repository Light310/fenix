import math
from dataclasses import dataclass
from functools import lru_cache


@dataclass
class Point:
    x: float
    y: float
    z: float


class LinearFunc:
    def __init__(self, point1, point2):
        delta_x = (point2.x - point1.x)
        if delta_x == 0:
            delta_x = 0.01
        self.k = (point2.y - point1.y) / delta_x
        self.b = (point2.x * point1.y - point1.x * point2.y) / delta_x
        self.angle = math.atan2(point2.y - point1.y, point2.x - point1.x)


def calculate_intersection(func1, func2):
    x = (func1.b - func2.b) / (func2.k - func1.k)
    y = func1.k * x + func1.b
    return x, y


# function, that moves on a line from a given point to a target point for a margin distance
def move_on_a_line(intersection_point, target_point, margin):
    function = LinearFunc(intersection_point, target_point)
    new_point_x = round(intersection_point.x +
                        math.cos(function.angle) * margin,
                        2)
    new_point_y = round(intersection_point.y +
                        math.sin(function.angle) * margin,
                        2)

    return [new_point_x, new_point_y]


def get_angle_by_coords(x1, y1):
    l = math.sqrt(x1 ** 2 + y1 ** 2)
    initial_angle = math.asin(abs(y1) / l)
    if x1 >= 0 and y1 >= 0:
        return initial_angle
    if x1 >= 0 and y1 < 0:
        return 2*math.pi - initial_angle
    if x1 < 0 and y1 >= 0:
        return math.pi - initial_angle
    if x1 < 0 and y1 < 0:
        return initial_angle + math.pi


def turn_on_angle(x1, y1, angle):
    l = math.sqrt(x1 ** 2 + y1 ** 2)
    initial_angle = get_angle_by_coords(x1, y1)
    result_angle = angle + initial_angle
    print(f'{math.degrees(initial_angle)} -> {math.degrees(result_angle)}')

    return round(math.cos(result_angle) * l, 2), \
           round(math.sin(result_angle) * l, 2)


class Leg:
    d = 5.3
    a = 8.7
    b = 6.9
    c = 13.2

    def __init__(self, O, D):
        self.O = O
        self.D = D
        self.update_angles()

    def update_angles(self):
        self.tetta, self.alpha, self.beta, self.gamma = self.calculate_angles()

    def calculate_angles(self):
        O = self.O
        D = self.D
        tetta = math.atan2(D.y - O.y, D.x - O.x)
        A = Point(O.x + self.d * math.cos(tetta),
                  O.y + self.d * math.sin(tetta),
                  O.z)

        l = round(math.sqrt((D.x - A.x) ** 2 + (D.y - A.y) ** 2), 2)
        delta_z = round(D.z - O.z, 2)

        alpha, beta, gamma = get_leg_angles(l, delta_z)

        Bx = self.a * math.cos(alpha)
        By = self.a * math.sin(alpha)
        Cx = Bx + self.b * math.cos(alpha + beta)
        Cy = By + self.b * math.sin(alpha + beta)
        Dx = Cx + self.c * math.cos(alpha + beta + gamma)
        Dy = Cy + self.c * math.sin(alpha + beta + gamma)
        if abs(Dx - l) > 0.01 or abs(Dy - delta_z) > 0.01:
            print('WTF')

        B_xz = [self.a * math.cos(alpha),
                self.a * math.sin(alpha)]
        C_xz = [B_xz[0] + self.b * math.cos(alpha + beta),
                B_xz[1] + self.b * math.sin(alpha + beta)]
        D_xz = [C_xz[0] + self.c * math.cos(alpha + beta + gamma),
                C_xz[1] + self.c * math.sin(alpha + beta + gamma)]

        D_prev = D
        self.A = A
        self.B = Point(A.x + B_xz[0] * math.cos(tetta),
                       A.y + B_xz[0] * math.sin(tetta),
                       A.z + B_xz[1])
        self.C = Point(A.x + C_xz[0] * math.cos(tetta),
                       A.y + C_xz[0] * math.sin(tetta),
                       A.z + C_xz[1])
        self.D = Point(A.x + D_xz[0] * math.cos(tetta),
                       A.y + D_xz[0] * math.sin(tetta),
                       A.z + D_xz[1])

        if abs(D_prev.x - self.D.x) > 0.01 or \
           abs(D_prev.y - self.D.y) > 0.01 or \
           abs(D_prev.z - self.D.z) > 0.01:
            raise Exception('D_prev far from D. Angles : {0}'
                            .format(([tetta, alpha, beta, gamma])))

        return tetta, alpha, beta, gamma

    @staticmethod
    def move_point(point, delta_x, delta_y, delta_z):
        point.x += delta_x
        point.y += delta_y
        point.z += delta_z

    def move_mount_point(self, delta_x, delta_y, delta_z):
        self.move_point(self.O, delta_x, delta_y, delta_z)
        self.update_angles()

    def move_end_point(self, delta_x, delta_y, delta_z):
        self.move_point(self.D, delta_x, delta_y, delta_z)
        self.update_angles()

    # means one leg is raised and moves with the body
    # end_delta = 0 means that leg is not moving, else it is also moving somehow
    # wtf something weird here
    def move_both_points(self, delta_x, delta_y, delta_z, end_delta_x, end_delta_y, end_delta_z):
        self.move_point(self.O, delta_x, delta_y, delta_z)
        self.move_point(self.D,
                        delta_x + end_delta_x,
                        delta_y + end_delta_y,
                        delta_z + end_delta_z)
        self.update_angles()


@lru_cache(maxsize=None)
def get_leg_angles(delta_x, delta_z):
    possible_angles = find_angles(delta_x, delta_z)

    return get_best_angles(possible_angles)


def find_angles(Dx, Dy):
    a, b, c = Leg.a, Leg.b, Leg.c
    results = []
    full_dist = math.sqrt(Dx ** 2 + Dy ** 2)
    if full_dist > a + b + c:
        raise Exception('No decisions. Full distance : {0}'.format(full_dist))

    # from_angle = -45.0
    # to_angle = 45.0
    # angle_step = 1.5
    # for k in np.arange(from_angle, to_angle, angle_step):
    for k in range(-45, 46, 1):
        ksi = math.radians(k)

        Cx = Dx + c * math.cos(math.pi / 2 + ksi)
        Cy = Dy + c * math.sin(math.pi / 2 + ksi)
        dist = math.sqrt(Cx ** 2 + Cy ** 2)

        if dist > a + b or dist < abs(a - b):
            pass
        else:
            alpha1 = math.acos((a ** 2 + dist ** 2 - b ** 2) / (2 * a * dist))
            beta1 = math.acos((a ** 2 + b ** 2 - dist ** 2) / (2 * a * b))
            beta = -1 * (math.pi - beta1)

            alpha2 = math.atan2(Cy, Cx)
            alpha = alpha1 + alpha2

            Bx = a * math.cos(alpha)
            By = a * math.sin(alpha)

            BD = math.sqrt((Dx - Bx) ** 2 + (Dy - By) ** 2)
            angle_C = math.acos((b ** 2 + c ** 2 - BD ** 2) / (2 * b * c))

            for coef in [-1, 1]:
                gamma = coef * (math.pi - angle_C)

                Cx = Bx + b * math.cos(alpha + beta)
                Cy = By + b * math.sin(alpha + beta)
                new_Dx = Cx + c * math.cos(alpha + beta + gamma)
                new_Dy = Cy + c * math.sin(alpha + beta + gamma)
                if abs(new_Dx - Dx) > 0.01 or abs(new_Dy - Dy) > 0.01:
                    continue

                results.append([alpha, beta, gamma])

    return results


def check_angles(angles):
    # wtf check this on Fenix
    alpha = math.degrees(angles[0])
    beta = math.degrees(angles[1])
    gamma = math.degrees(angles[2])

    if alpha < -35 or alpha > 55:
        return False
    if beta < -115 or beta > -20:
        return False
    if gamma < -110 or gamma > 0:
        return False

    mode = 40
    if alpha + beta + gamma < -90 - mode or alpha + beta + gamma > -90 + mode:
        return False

    return True


def get_best_angles(all_angles):
    min_distance = 100000000
    best_angles = None
    min_distance_num = 0

    for item in all_angles:
        if not check_angles(item):
            continue
        cur_distance = get_angles_distance(item)

        if cur_distance <= min_distance:
            min_distance = cur_distance
            best_angles = item[:]

    if min_distance > 0.1:
        min_distance_num += 1
        if min_distance_num > 1:
            # print('best_angles : {0}'.format([math.degrees(x) for x in best_angles]))
            raise Exception('Min distance found : {0}'.format(min_distance))

    if best_angles is None:
        raise Exception('No angles\n')

    return best_angles


def get_angles_distance(angles):
    # no diff, just distance with perpendicular
    # 100 -> endleg leaning inside
    return (math.degrees(angles[0] + angles[1] + angles[2]) + 90) ** 2


class MovementSequence:
    def __init__(self, legs_offset_h, legs_offset_v):
        self.legs_offset_v = legs_offset_v
        self.legs_offset_h = legs_offset_h

        self.current_angle = 0
        self.margin = 3 #4
        self.leg_up = 6
        self.mode = 90  # needed?
        self.mount_point_offset = 3.8

        self.legs = self.initiate_legs()

        self.angles_history = []
        self.add_angles_snapshot()

    def reset_history(self):
        self.angles_history = []

    def add_angles_snapshot(self):
        # angles are : gamma1, beta1, alpha1, tetta1, gamma2, beta2, alpha2, tetta2 ...
        # for leg1 tetta = 45 means 0 for servo
        # leg2 tetta = -45, leg3 tetta = -135, leg4 tetta = 135

        position = []
        for leg_number, leg in self.legs.items():
            position.append(round(math.degrees(leg.gamma), 2))
            position.append(round(math.degrees(leg.beta), 2))
            position.append(round(math.degrees(leg.alpha), 2))
            tetta = math.degrees(leg.tetta)
            if leg_number == 1:
                tetta -= 90
            if leg_number == 2:
                tetta += 90
            if leg_number == 3:
                tetta += 90
            if leg_number == 4:
                tetta -= 90
            tetta = round(tetta, 2)
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
                        tetta = round(cur_value + 45, 2)
                    else:
                        tetta = round(cur_value - 45, 2)
                    if tetta > 60 or tetta < - 60:
                        raise Exception(f'Wrong tetta angle : {tetta}')
                    out_angles.append(tetta)
                else:
                    out_angles.append(cur_value)

        return out_angles

    @property
    def sequence(self):
        return self.angles_history

    def initiate_legs(self):
        O1 = Point(self.mount_point_offset,
                   self.mount_point_offset,
                   0)
        D1 = Point(self.legs_offset_h,
                   self.legs_offset_h,
                   self.legs_offset_v)
        Leg1 = Leg(O1, D1)

        O2 = Point(self.mount_point_offset,
                   -self.mount_point_offset,
                   0)
        D2 = Point(self.legs_offset_h,
                   -self.legs_offset_h,
                   self.legs_offset_v)
        Leg2 = Leg(O2, D2)

        O3 = Point(-self.mount_point_offset,
                   -self.mount_point_offset,
                   0)
        D3 = Point(-self.legs_offset_h,
                   -self.legs_offset_h,
                   self.legs_offset_v)
        Leg3 = Leg(O3, D3)

        O4 = Point(-self.mount_point_offset,
                   self.mount_point_offset,
                   0)
        D4 = Point(-self.legs_offset_h,
                   self.legs_offset_h,
                   self.legs_offset_v)
        Leg4 = Leg(O4, D4)

        return {1: Leg1, 2: Leg2, 3: Leg3, 4: Leg4}

    ################## MOVEMENTS START HERE ##################
    def leg_movement(self, leg_num, leg_delta):
        leg = self.legs[leg_num]

        leg.move_end_point(leg_delta[0], leg_delta[1], leg_delta[2])
        self.add_angles_snapshot()

    def body_movement(self, delta_x, delta_y, delta_z):
        if delta_x == delta_y == delta_z == 0:
            return

        for leg in self.legs.values():
            leg.move_mount_point(delta_x, delta_y, delta_z)

        self.add_angles_snapshot()

    def body_to_center(self, delta_y=0, delta_x=0):
        # move body to center
        avg_o_x, avg_o_y, avg_d_x, avg_d_y = 0, 0, 0, 0
        for leg in self.legs.values():
            avg_o_x += leg.O.x
            avg_o_y += leg.O.y
            avg_d_x += leg.D.x
            avg_d_y += leg.D.y

        avg_o_x /= 4
        avg_o_y /= 4
        avg_d_x /= 4
        avg_d_y /= 4

        self.body_movement(avg_d_x - avg_o_x + delta_x,
                           avg_d_y - avg_o_y + delta_y,
                           0)

    # body compensation for moving up one leg
    def target_body_position(self, leg_in_the_air_number):
        """
        provide the number of leg_in_the_air
        return target position of body to let the leg go into the air
        """

        # find intersection point of basement lines
        func1 = LinearFunc(self.legs[1].D, self.legs[3].D)
        func2 = LinearFunc(self.legs[2].D, self.legs[4].D)
        intersection = Point(*calculate_intersection(func1, func2), 0)

        target_leg_number_by_air_leg_number = {1: 3, 2: 4, 3: 1, 4: 2}
        target_leg_number = target_leg_number_by_air_leg_number[leg_in_the_air_number]
        target_leg = self.legs[target_leg_number]
        body_target_point = move_on_a_line(intersection,
                                           target_leg.D,
                                           self.margin)

        return body_target_point

    def body_compensation_for_a_leg(self, leg_num):
        target = self.target_body_position(leg_num)

        current_body_x = (self.legs[1].O.x +
                          self.legs[2].O.x +
                          self.legs[3].O.x +
                          self.legs[4].O.x) / 4

        current_body_y = (self.legs[1].O.y +
                          self.legs[2].O.y +
                          self.legs[3].O.y +
                          self.legs[4].O.y) / 4

        self.body_movement(target[0] - current_body_x,
                           target[1] - current_body_y,
                           0)

    def compensated_leg_movement(self, leg_num, leg_delta):
        # moving body to compensate future movement
        self.body_compensation_for_a_leg(leg_num)

        self.legs[leg_num].move_end_point(*leg_delta)
        self.add_angles_snapshot()

    def leg_move_with_compensation(self, leg_num, delta_x, delta_y):
        self.compensated_leg_movement(leg_num, [delta_x, delta_y, self.leg_up])
        self.move_leg_endpoint(leg_num, [0, 0, -self.leg_up])
        #self.compensated_leg_movement(leg_num, [0, 0, -self.leg_up])

    def move_leg_endpoint(self, leg_num, leg_delta):
        self.legs[leg_num].move_end_point(*leg_delta)
        self.add_angles_snapshot()

    # 1-legged movements
    def move_body_straight(self, delta_x, delta_y, leg_seq=[1, 2, 3, 4]):
        for leg_number in leg_seq:
            self.leg_move_with_compensation(leg_number, delta_x, delta_y)
        self.body_to_center()

    # 2-legged movements
    def move_2_legs(self, delta_y):
        full_leg_delta_1 = [0, delta_y, self.leg_up]
        full_leg_delta_2 = [0, 0, -self.leg_up]

        for leg in [self.legs[2], self.legs[4]]:
            leg.move_end_point(*full_leg_delta_1)
        self.add_angles_snapshot()

        for leg in [self.legs[2], self.legs[4]]:
            leg.move_end_point(*full_leg_delta_2)
        self.add_angles_snapshot()

        self.body_movement(0, delta_y, 0)

        for leg in [self.legs[1], self.legs[3]]:
            leg.move_end_point(*full_leg_delta_1)
        self.add_angles_snapshot()

        for leg in [self.legs[1], self.legs[3]]:
            leg.move_end_point(*full_leg_delta_2)
        self.add_angles_snapshot()

    def reposition_legs(self, delta_x, delta_y):
        self.legs[2].move_end_point(delta_x, -delta_y, self.leg_up)
        self.legs[4].move_end_point(-delta_x, delta_y, self.leg_up)
        self.add_angles_snapshot()

        self.legs[2].move_end_point(0, 0, -self.leg_up)
        self.legs[4].move_end_point(0, 0, -self.leg_up)
        self.add_angles_snapshot()

        self.legs[1].move_end_point(delta_x, delta_y, self.leg_up)
        self.legs[3].move_end_point(-delta_x, -delta_y, self.leg_up)
        self.add_angles_snapshot()

        self.legs[1].move_end_point(0, 0, -self.leg_up)
        self.legs[3].move_end_point(0, 0, -self.leg_up)
        self.add_angles_snapshot()

    def turn_body_and_legs(self, angle_deg):
        angle = math.radians(angle_deg)

        for leg in [self.legs[2], self.legs[4]]:
            x_new, y_new = turn_on_angle(leg.D.x, leg.D.y, angle)
            delta_x = x_new - leg.D.x
            delta_y = y_new - leg.D.y

            leg.move_end_point(delta_x, delta_y, self.leg_up)

        self.add_angles_snapshot()

        for leg in [self.legs[2], self.legs[4]]:
            leg.move_end_point(0, 0, -self.leg_up)
        
        self.add_angles_snapshot()

        for leg in [self.legs[1], self.legs[3]]:
            x_new, y_new = turn_on_angle(leg.D.x, leg.D.y, angle)
            delta_x = x_new - leg.D.x
            delta_y = y_new - leg.D.y

            leg.move_end_point(delta_x, delta_y, self.leg_up)

        self.add_angles_snapshot()

        for leg in [self.legs[1], self.legs[3]]:
            leg.move_end_point(0, 0, -self.leg_up)

        self.add_angles_snapshot()

        self.turn_only_body(angle_deg)


    # no leg movements
    def turn_only_body(self, angle_deg):
        angle = math.radians(angle_deg)

        for leg in self.legs.values():
            x_new, y_new = turn_on_angle(leg.O.x, leg.O.y, angle)
            delta_x = x_new - leg.O.x
            delta_y = y_new - leg.O.y
            print(f'[{leg.O.x},{leg.O.y}] -> [{x_new}, {y_new}]')
            leg.move_mount_point(delta_x, delta_y, 0)
        self.add_angles_snapshot()

    def look_on_angle(self, angle):
        current_angle = self.current_angle

        x_current = self.mount_point_offset * \
                    math.cos(math.radians(current_angle))
        z_current = self.mount_point_offset * \
                    math.sin(math.radians(current_angle))

        x_target = self.mount_point_offset * math.cos(math.radians(angle))
        z_target = self.mount_point_offset * math.sin(math.radians(angle))

        x = x_current - x_target
        z = z_current - z_target

        for leg in [self.legs[1], self.legs[4]]:
            leg.move_mount_point(0, -x, z)
        for leg in [self.legs[2], self.legs[3]]:
            leg.move_mount_point(0, x, -z)

        self.add_angles_snapshot()

        self.current_angle = angle
