from lx16a_servos import LX16A

class Fenix():
    def __init__(self):
        self.m1 = LX16A(Port='/dev/ttyAMA0') # 5-8   # 1-4
        self.m2 = LX16A(Port='/dev/ttyAMA2') # 9-12  # 5-8
        self.m3 = LX16A(Port='/dev/ttyAMA3') # 13-16 # 9-12
        self.m4 = LX16A(Port='/dev/ttyAMA1') # 1-4   # 13-16
    
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
        #print(angles)
        print('converted to')
        print(out_angles)
        return out_angles

    def set_servo_values(self, angles):
        print('Sending values {0}'.format(angles))
        angles = self.convert_angles(angles)
        self.m1.moveServoToAngle(1, angles[0])
        self.m1.moveServoToAngle(2, angles[1])
        self.m1.moveServoToAngle(3, angles[2])
        self.m1.moveServoToAngle(4, angles[3])

        self.m2.moveServoToAngle(5, angles[4])
        self.m2.moveServoToAngle(6, angles[5])
        self.m2.moveServoToAngle(7, angles[6])
        self.m2.moveServoToAngle(8, angles[7])

        self.m3.moveServoToAngle(9, angles[8])
        self.m3.moveServoToAngle(10, angles[9])
        self.m3.moveServoToAngle(11, angles[10])
        self.m3.moveServoToAngle(12, angles[11])

        self.m4.moveServoToAngle(13, angles[12])
        self.m4.moveServoToAngle(14, angles[13])
        self.m4.moveServoToAngle(15, angles[14])
        self.m4.moveServoToAngle(16, angles[15])

if __name__ == '__main__':
    fnx = Fenix()
    fnx.set_servo_values([-44.26, -74.76, 29.02, -45.0, -44.26, -74.76, 29.02, 45.0, -44.26, -74.76, 29.02, -45.0, -44.26, -74.76, 29.02, 45.0])
    #[0.0, 23.96, 73.61, -40.36, 0.0, 23.96, 73.61, -40.36, 0.0, 23.96, 73.61, -40.36, 0.0, 23.96, 73.61, -40.36]