import time
from lx16a_servos import LX16A


class Fenix():
    def __init__(self):
        self.m1 = LX16A(Port='/dev/ttyAMA0') # 5-8   # 1-4
        self.m2 = LX16A(Port='/dev/ttyAMA2') # 9-12  # 5-8
        self.m3 = LX16A(Port='/dev/ttyAMA3') # 13-16 # 9-12
        self.m4 = LX16A(Port='/dev/ttyAMA1') # 1-4   # 13-16
        self.speed = 1000
    
    def set_speed(self, new_speed):
        if new_speed > 10000 or new_speed < 500:
            raise Exception('Invalid speed value {0}. Should be between 500 and 10000'.format(new_speed))
        self.speed = new_speed

    def get_current_angles(self):
        current_angles = []
        j = 1
        for m in [self.m1, self.m2, self.m3, self.m4]:            
            for _ in range(4):
                current_angles.append(m.readAngle(j))
                j += 1
        print('Current angles :')
        print(current_angles)
        return current_angles

    def angles_are_close(self, target_angles):
        """
        compares self angles to target angles
        if they are different, return false
        """
        current_angles = self.get_current_angles()
        """
        j = 1
        for m in [self.m1, self.m2, self.m3, self.m4]:            
            for _ in range(4):
                current_angles.append(m.readAngle(j))
                j += 1
        print('Current angles :')
        print(current_angles)
        """
        for i in range(16):
            if abs(current_angles[i] - target_angles[i]) > 2:
                print('Angles {0} diff too big. {1}, {2}'.format(i, current_angles[i], target_angles[i]))
                return False

        return True

    def set_servo_values(self, angles, rate=0):
        print('Sending values {0}'.format(angles))
        self.get_angles_diff(angles)
        j = 1
        for m in [self.m1, self.m2, self.m3, self.m4]:
            for _ in range(4):
                m.moveServoToAngle(j, angles[j-1], rate)
                j += 1

    def set_servo_values_paced(self, angles):        
        _, max_angle_diff = self.get_angles_diff(angles)
        rate = max(self.speed * max_angle_diff / 45, 500) # speed is normalized
        print('Rate : {0}'.format(rate))
        avg_wait = self.calculate_wait_time(max_angle_diff, rate)
        print('Avg wait : {0}'.format(avg_wait))
        j = 1
        for m in [self.m1, self.m2, self.m3, self.m4]:
            for _ in range(4):
                m.moveServoToAngle(j, angles[j-1], rate)
                j += 1
        time.sleep(1*avg_wait)
        

    def get_angles_diff(self, target_angles):
        current_angles = self.get_current_angles()
        angles_diff = []
        for current, target in zip(current_angles, target_angles):
            angles_diff.append(round(current - target, 2))
        print('Angles diff : {0}'.format(angles_diff))
        max_angle_diff = max([abs(x) for x in angles_diff])
        print('Max angle diff : {0}'.format(max_angle_diff))
        return angles_diff, max_angle_diff

    
    @staticmethod
    def calculate_wait_time(degrees, speed):
        return round(abs(degrees / 40) * (speed / 1000), 2)

    @staticmethod
    def calculate_speed(degrees, wait_time):
        if abs(degrees) < 5:
            return 500
        speed = round(1.0 * wait_time * 1000 / abs(degrees / 40))
        return max(min(speed, 10000), 500)


if __name__ == '__main__':
    fnx = Fenix()
    
    fnx.set_speed(2000)

    angles = [0.0, 30.76, 80.3, -40.46, 0.0, 30.76, 80.3, -40.46, 0.0, 30.76, 80.3, -40.46, 0.0, 30.76, 80.3, -40.46]
    fnx.set_servo_values_paced(angles)
    
    angles = [0.0, 33.54, 103.53, -41.01, -22.29, 23.81, 62.49, -51.32, 0.0, 13.38, 45.71, -36.67, 22.29, 23.81, 62.49, -51.32]
    #fnx.set_servo_values(angles, rate=500)
    fnx.set_servo_values_paced(angles)
    #time.sleep(2)
    angles = [0.0, 30.76, 80.3, -40.46, 0.0, 30.76, 80.3, -40.46, 0.0, 30.76, 80.3, -40.46, 0.0, 30.76, 80.3, -40.46]
    fnx.set_servo_values_paced(angles)
