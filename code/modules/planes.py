import math

class Plane:
    def __init__(self, angle_x, angle_y):
        # equitation is Ax + By + Cz + D = 0
        # point is (0, 0, 0), so D is always 0

        vector_1 = [math.cos(math.radians(angle_x)), 0, math.sin(math.radians(angle_x))]
        vector_2 = [0, math.cos(math.radians(angle_y)), math.sin(math.radians(angle_y))]

        self.D = 0
        self.A = -vector_1[2] * vector_2[1]
        self.B = -vector_1[0] * vector_2[2]
        self.C =  vector_1[0] * vector_2[1]

    def __str__(self):
        return '{0}x + {1}y + {2}z = 0'.format(self.A, self.B, self.C)

# accepts ([1st_plane_x_angle, 1st_plane_y_angle], [2nd_plane_x_angle, 2nd_plane_y_angle])
def angle_between_planes(angles_xy_1, angles_xy_2):
    Plane1 = Plane(angles_xy_1[0], angles_xy_1[1])
    Plane2 = Plane(angles_xy_2[0], angles_xy_2[1])
    d = ( Plane1.A * Plane2.A + Plane1.B * Plane2.B + Plane1.C * Plane2.C ) 
    e1 = math.sqrt( Plane1.A ** 2 + Plane1.B ** 2 + Plane1.C ** 2) 
    e2 = math.sqrt( Plane2.A ** 2 + Plane2.B ** 2 + Plane2.C ** 2) 
    d = d / (e1 * e2) 
    return math.degrees(math.acos(d)) 

# example
# print(angle_between_planes([1.38, 2.21], [10.98, -3.86]))