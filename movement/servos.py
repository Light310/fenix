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

    def angles_are_close(self, target_angles):
        """
        compares self angles to target angles
        if they are different, return false
        """
        current_angles = []
        j = 1
        for m in [self.m1, self.m2, self.m3, self.m4]:            
            for _ in range(4):
                current_angles.append(m.readAngle(j))
                j += 1
        print('Current angles :')
        print(current_angles)

        target_angles = self.convert_angles(target_angles)
        for i in range(16):
            if abs(current_angles[i] - target_angles[i]) > 2:
                print('Angles {0} diff too big. {1}, {2}'.format(i, current_angles[i], target_angles[i]))
                return False

        return True

    def set_servo_values(self, angles, rate=0):
        print('Sending values {0}'.format(angles))
        angles = self.convert_angles(angles)
        j = 1
        for m in [self.m1, self.m2, self.m3, self.m4]:
            for _ in range(4):
                m.moveServoToAngle(j, angles[j-1], rate)
                j += 1

        """
        self.m1.moveServoToAngle(1, angles[0], rate)
        self.m1.moveServoToAngle(2, angles[1], rate)
        self.m1.moveServoToAngle(3, angles[2], rate)
        self.m1.moveServoToAngle(4, angles[3], rate)

        self.m2.moveServoToAngle(5, angles[4], rate)
        self.m2.moveServoToAngle(6, angles[5], rate)
        self.m2.moveServoToAngle(7, angles[6], rate)
        self.m2.moveServoToAngle(8, angles[7], rate)

        self.m3.moveServoToAngle(9, angles[8], rate)
        self.m3.moveServoToAngle(10, angles[9], rate)
        self.m3.moveServoToAngle(11, angles[10], rate)
        self.m3.moveServoToAngle(12, angles[11], rate)

        self.m4.moveServoToAngle(13, angles[12], rate)
        self.m4.moveServoToAngle(14, angles[13], rate)
        self.m4.moveServoToAngle(15, angles[14], rate)
        self.m4.moveServoToAngle(16, angles[15], rate)
        """

if __name__ == '__main__':
    fnx = Fenix()
    fnx.set_servo_values([-44.26, -74.76, 29.02, -45.0, -44.26, -74.76, 29.02, 45.0, -44.26, -74.76, 29.02, -45.0, -44.26, -74.76, 29.02, 45.0])
    #[0.0, 23.96, 73.61, -40.36, 0.0, 23.96, 73.61, -40.36, 0.0, 23.96, 73.61, -40.36, 0.0, 23.96, 73.61, -40.36]