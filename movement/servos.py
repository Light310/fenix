from lx16a_servos import LX16A

class Fenix():
    def __init__(self):
        self.m1 = LX16A(Port='/dev/ttyAMA0') # 5-8   # 1-4
        self.m2 = LX16A(Port='/dev/ttyAMA2') # 9-12  # 5-8
        self.m3 = LX16A(Port='/dev/ttyAMA3') # 13-16 # 9-12
        self.m4 = LX16A(Port='/dev/ttyAMA1') # 1-4   # 13-16
    
    """
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
    """
    @staticmethod
    def convert_angles(angles):
        return angles

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

if __name__ == '__main__':
    fnx = Fenix()
    #angles = [-23.43, -106.62, 40.0, -45.0, -46.26, -71.5, 27.75, 35.14, -86.69, -25.02, 27.49, -45.0, -46.26, -71.5, 27.75, 54.86]
    #angles = [-23.43, -106.62, 40.0, -45.0, -46.26, -71.5, 24.75, 35.14, -86.69, -25.02, 27.49, -45.0, -46.26, -71.5, 24.75, 54.86]
    angles = [0.0, 40.0, 106.62, -23.43, -9.86, 27.75, 71.5, -46.26, 0.0, 27.49, 25.02, -86.69, 9.86, 27.75, 71.5, -46.26]
    fnx.set_servo_values(angles, rate=5000)
    import time
    for i in range(10):
        fnx.angles_are_close(angles)
        time.sleep(0.5)

    # [0.48, 39.6, 107.52, -24.96, -9.12, 31.92, 69.84, -46.8, -0.72, 27.36, 25.68, -87.36, 8.4, 30.72, 70.56, -47.52]
    # 31.92 and 30.72 must go to 27.75
    # 30.96, 29.28
    # 28.8, 26.16
    # 6, 14
