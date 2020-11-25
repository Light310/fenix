import threading
import time

from lx16a_servos import LX16A


class Fenix(threading.Thread):

    thread_sleep_time = 0.1

    def __init__(self):
        self.m1 = LX16A(Port='/dev/ttyAMA0') # 5-8   # 1-4
        self.m2 = LX16A(Port='/dev/ttyAMA2') # 9-12  # 5-8
        self.m3 = LX16A(Port='/dev/ttyAMA3') # 13-16 # 9-12
        self.m4 = LX16A(Port='/dev/ttyAMA1') # 1-4   # 13-16

        self.target = -1000
        self.prev_target = -1000
        self.prev_value = -1000
        self.delta = 0

        self.targets = [-200 for _ in range(16)]
        self.prev_targets = [-200 for _ in range(16)]
        self.prev_values = [-200 for _ in range(16)]
        # self.angles_sent = []
        #self.target_angles = []
        self.deltas = [0 for _ in range(16)]
        self.stop_thread = False

        threading.Thread.__init__(self, daemon=True)
        self.start()        
    
    def run(self):
        while True:
            if self.targets[0] > -200:
                angle_step = 2
                values_to_send = [0 for _ in range(16)]
                current_angles = self.get_current_angles()
                for servo in range(16):
                    current_angle = current_angles[servo]
                    print('Target : {0}. Prev tgt : {1}. Current : {2}. Prev crnt: {3}'
                            .format(self.targets[servo], self.prev_targets[servo], current_angle, self.prev_values[servo]))
                    if abs(current_angle - self.targets[servo]) < 0.13:
                        print('All ok')
                    else:                
                        if current_angle == self.prev_values[servo] and self.targets[servo] == self.prev_targets[servo]:
                            add_delta = self.targets[servo] - current_angle
                            if add_delta > angle_step:
                                add_delta = angle_step
                            if add_delta < -angle_step:
                                add_delta = -angle_step
                            self.deltas[servo] = round(self.deltas[servo] + add_delta, 2)
                            print('New delta : {0}'.format(self.deltas[servo]))
                    values_to_send[servo] = round(self.targets[servo] + self.deltas[servo], 2)
                        # self.set_single_servo_value(self.targets[servo] + self.deltas[servo])
                    self.prev_targets[servo] = self.targets[servo]
                    self.prev_values[servo] = current_angle
                print('Current deltas : {0}'.format(self.deltas))
                self.set_servo_values(values_to_send)            

            if self.stop_thread:
                print('Breaking the infinite loop')
                break
            time.sleep(self.thread_sleep_time)
    
    def stop(self):
        print('Sent command to stop')
        self.stop_thread = True

    def angles_are_close(self, target_angles):
        """
        compares self angles to target angles
        if they are different, return false
        """
        current_angles = self.get_current_angles()

        for i in range(16):
            if abs(current_angles[i] - target_angles[i]) > 5:
                print('Angles {0} diff too big. {1}, {2}'.format(i, current_angles[i], target_angles[i]))
                return False

        return True

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

    def set_servo_values_adj(self, angles):
        self.targets = angles[:]
    
    def set_single_servo_value(self, angle, rate=0):
        print('Sending value {0}'.format(angle))
        self.m1.moveServoToAngle(4, angle, rate)

    def set_servo_values(self, angles, rate=0):
        print('Sending values {0}'.format(angles))
        if sum([abs(x) for x in angles]) < 1:
            print('Doing nothing')
        else:        
            self.angles_sent = angles[:]
            j = 1
            for m in [self.m1, self.m2, self.m3, self.m4]:
                for _ in range(4):
                    m.moveServoToAngle(j, angles[j-1], rate)
                    j += 1
    

if __name__ == '__main__':
    fnx = Fenix()
    
    #angles = [0.0, 39.99, 68.51, -63.45, 0.0, 39.99, 68.51, -63.45, 0.0, 39.99, 68.51, -63.45, 0.0, 39.99, 68.51, -63.45]
    print('Phase 1 start ===============================')
    # angles = [0.0, 39.99, 68.51, -63.45, 0.0, 39.99, 68.51, -63.45, 0.0, 39.99, 68.51, -63.45, 0.0, 39.99, 68.51, -63.45] # alpha < 40
    # angles = [0.0, 34.99, 58.39, -73.58, 0.0, 34.99, 58.39, -73.58, 0.0, 34.99, 58.39, -73.58, 0.0, 34.99, 58.39, -73.58] # alpha < 35
    angles = [0.0, 30.76, 80.3, -40.46, 0.0, 30.76, 80.3, -40.46, 0.0, 30.76, 80.3, -40.46, 0.0, 30.76, 80.3, -40.46]
    fnx.set_servo_values(angles, rate=3000)
    time.sleep(5)

    #angles = [0.0, 40.0, 106.62, -23.43, -9.86, 27.75, 71.5, -46.26, 0.0, 27.49, 25.02, -86.69, 9.86, 27.75, 71.5, -46.26]
    print('Phase 2 start ===============================')
    # angles = [0.0, 40.0, 106.62, -23.43, -9.86, 27.75, 71.5, -46.26, 0.0, 12.26, 25.01, -75.76, 9.86, 27.75, 71.5, -46.26] # up 1 cm 3 margin
    # angles = [0.0, 40.0, 106.62, -23.43, -9.86, 27.75, 71.5, -46.26, 0.0, 16.06, 25.04, -79.14, 9.86, 27.75, 71.5, -46.26] # up 2 cm 3 margin
    # angles = [0.0, 40.0, 107.67, -28.5, -13.06, 26.73, 68.88, -47.85, 0.0, 15.69, 25.0, -71.94, 13.06, 26.73, 68.88, -47.85] # up 2 cm 4 margin
    # angles = [0.0, 34.99, 95.45, -44.33, -13.06, 26.73, 68.88, -47.85, 0.0, 15.69, 25.0, -71.94, 13.06, 26.73, 68.88, -47.85] # --||-- alpha < 35
    # new lengths, 3 cm up
    angles = [0.0, 34.99, 95.96, -40.06, -13.06, 28.69, 74.84, -43.84, 0.0, 19.23, 25.02, -80.41, 13.06, 28.69, 74.84, -43.84]
    fnx.set_servo_values(angles, rate=3000)
    time.sleep(5)
    #angles = [0.0, 45, 75, -70, 0.0, 39.99, 68.51, -63.45, 0.0, 39.99, 68.51, -63.45, 0.0, 39.99, 68.51, -63.45]
    print('Phase 3 start ===============================')
    fnx.set_servo_values_adj(angles)
    # fnx.set_servo_values_adj(-60)
    # fnx.join()
    time.sleep(10)
    fnx.stop()
    time.sleep(1)
    print('Phase 4 start ===============================')
    # angles = [0.0, 39.99, 68.51, -63.45, 0.0, 39.99, 68.51, -63.45, 0.0, 39.99, 68.51, -63.45, 0.0, 39.99, 68.51, -63.45] # alpha < 40
    # angles = [0.0, 34.99, 58.39, -73.58, 0.0, 34.99, 58.39, -73.58, 0.0, 34.99, 58.39, -73.58, 0.0, 34.99, 58.39, -73.58] # alpha < 35
    angles = [0.0, 30.76, 80.3, -40.46, 0.0, 30.76, 80.3, -40.46, 0.0, 30.76, 80.3, -40.46, 0.0, 30.76, 80.3, -40.46]
    fnx.set_servo_values(angles, rate=3000)
    # time.sleep(5)
    """
    import time
    for i in range(10):
        fnx.angles_are_close(angles)
        time.sleep(0.5)
    """

    # [0.48, 39.6, 107.52, -24.96, -9.12, 31.92, 69.84, -46.8, -0.72, 27.36, 25.68, -87.36, 8.4, 30.72, 70.56, -47.52]
    # 31.92 and 30.72 must go to 27.75
    # 30.96, 29.28
    # 28.8, 26.16
    # 6, 14
