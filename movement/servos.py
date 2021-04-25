import time
import datetime
from lx16a_servos import LX16A, read_values
from modules.utils import timing
import multiprocessing
import concurrent.futures


class Fenix():
    def __init__(self):
        self.m1 = LX16A(Port='/dev/ttyAMA0') # 5-8   # 1-4
        self.m2 = LX16A(Port='/dev/ttyAMA2') # 9-12  # 5-8
        self.m3 = LX16A(Port='/dev/ttyAMA3') # 13-16 # 9-12
        self.m4 = LX16A(Port='/dev/ttyAMA1') # 1-4   # 13-16
        self.speed = 1000
        self.max_speed = 100 # 130 # 0 is instant, 10000 is very slow
        self.diff_from_target_limit = 5.0 # when it's time to start next movement
        self.diff_from_prev_limit = 1.0 # start next movement if we're stuck
        
        # 0.16 sec / 60 degrees for 7.4V+
        # 0.18 sec / 60 degrees for 6V+
        # my max speed is for 45 degrees
        # that means that max speed should be 120 for 7.4V+ and 135 for 6V+

    def print_status(self):
        j = 1
        for m in [self.m1, self.m2, self.m3, self.m4]:
            for _ in range(4):
                m.read_values(j)
                j += 1
    
    def set_speed(self, new_speed):
        if new_speed > 10000 or new_speed < self.max_speed:
            raise Exception(f'Invalid speed value {new_speed}. Should be between {self.max_speed} and 10000')
        self.speed = new_speed
    
    #@timing
    def get_current_angles_not_threaded(self):
        current_angles = []
        j = 1
        for m in [self.m1, self.m2, self.m3, self.m4]:            
            for _ in range(4):
                current_angles.append(m.readAngle(j))
                j += 1
        #print('Current angles :')
        #print(current_angles)
        return current_angles
    
    #@timing
    def get_current_angles(self): # futures
        
        boards = [self.m1, self.m2, self.m3, self.m4]

        with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
            result = executor.map(self.get_angles_from_board, boards)
        
        current_angles = [val for board in result for val in board]
        
        return current_angles

    # return 4 angles from one board
    def get_angles_from_board(self, board):
        angles = []
        start_numbers = {self.m1 : 1, self.m2 : 5, self.m3 : 9, self.m4 : 13}
        for j in range(start_numbers[board], start_numbers[board] + 4):
            angles.append(board.readAngle(j))
        return angles

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
        print('Sending values \n{0}'.format(angles))
        #self.get_angles_diff(angles)
        j = 1
        for m in [self.m1, self.m2, self.m3, self.m4]:
            for _ in range(4):
                m.moveServoToAngle(j, angles[j-1], rate)
                j += 1
    #@timing
    def send_command_to_servos(self, angles, rate):
        j = 1
        for m in [self.m1, self.m2, self.m3, self.m4]:
            for _ in range(4):
                m.moveServoToAngle(j, angles[j-1], rate)
                j += 1
    #@timing
    def send_command_to_servos_futured(self, angles, rate):
        boards = [self.m1, self.m2, self.m3, self.m4]        
        args = [[board, angles, rate] for board in boards]

        #print(f'Sending Time : {datetime.datetime.now()}')
        with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
            executor.map(lambda p: self.send_angles_to_board(*p), args)

    # sends 4 angles to one board
    def send_angles_to_board(self, board, angles, rate):
        start_numbers = {self.m1 : 1, self.m2 : 5, self.m3 : 9, self.m4 : 13}
        for j in range(start_numbers[board], start_numbers[board] + 4):
            board.moveServoToAngle(j, angles[j-1], rate)


    #@timing
    def set_servo_values_paced(self, angles):
        #print(f'Angles before : {self.get_current_angles()}')
        _, max_angle_diff = self.get_angles_diff(angles)
        rate = round(max(self.speed * max_angle_diff / 45, self.max_speed)) # speed is normalized
        #avg_wait = self.calculate_wait_time(max_angle_diff, rate)
        #print(f'Max angle diff : {max_angle_diff}. Rate : {rate}. Avg_wait : {avg_wait}')
        #print(f'Max angle diff : {max_angle_diff}. Rate : {rate}.')
        
        """
        j = 1
        for m in [self.m1, self.m2, self.m3, self.m4]:
            for _ in range(4):
                m.moveServoToAngle(j, angles[j-1], rate)
                j += 1
        """
        self.send_command_to_servos(angles, rate)
        #self.send_command_to_servos_futured(angles, rate)        
        time.sleep(0.05)
        #time.sleep(avg_wait)

        prev_angles = self.get_current_angles()
        for _ in range(40):
            time.sleep(0.03)
            current_angles = self.get_current_angles()
            # if diff from prev angles or target angles is small - continue
            diff_from_target = self.get_angles_diff(angles, current_angles)
            diff_from_prev = self.get_angles_diff(current_angles, prev_angles)
            #print(f'Diff from target : {diff_from_target}')
            #print(f'Diff from prev   : {diff_from_prev}')
            #print(f'Time : {datetime.datetime.now()}')
            
            if diff_from_target[1] < self.diff_from_target_limit or diff_from_prev[1] < self.diff_from_prev_limit:
                if diff_from_target[1] > self.diff_from_target_limit + 2:
                    print('-----------ALARM-----------')
                    print(f'Diff from target : {diff_from_target}')
                    print(f'Diff from prev   : {diff_from_prev}')
                #print('Ready to move further')
                break
            prev_angles = current_angles[:]
        
        #print(f'Angles after : {self.get_current_angles()}')
        #time.sleep(0.5)
        #print(f'After sleep : {self.get_current_angles()}\n')
        

    def get_angles_diff(self, target_angles, test_angles=None):
        if test_angles is None:
            test_angles = self.get_current_angles()

        angles_diff = []
        for current, target in zip(test_angles, target_angles):
            angles_diff.append(round(current - target, 2))
        #print('Angles diff : {0}'.format(angles_diff))
        max_angle_diff = max([abs(x) for x in angles_diff])
        #print('Max angle diff : {0}'.format(max_angle_diff))
        return angles_diff, max_angle_diff

    
    @staticmethod
    def calculate_wait_time(degrees, speed):
        #return round(abs(degrees / 40) * (speed / 1000), 2)
        #return round((0.75 * speed / 1000), 2)
        return round((0.7*speed / 1000), 2)

    @staticmethod
    def calculate_speed(degrees, wait_time):
        if abs(degrees) < 5:
            return 500
        speed = round(1.0 * wait_time * 1000 / abs(degrees / 40))
        return max(min(speed, 10000), 500)


if __name__ == '__main__':
    fnx = Fenix()
    
    """
    for i in range(100):
        print(fnx.get_current_angles())
        print(fnx.get_current_angles_futures())
        time.sleep(0.1)
        
    
    fnx.set_speed(1500)
    sequence = [
        [0.0, 33.77, 107.89, -15.88, 0.0, 33.77, 107.89, -15.88, 0.0, 33.77, 107.89, -15.88, 0.0, 33.77, 107.89, -15.88],
        [40.08, 31.62, 98.84, -22.78, 40.08, 31.62, 98.84, -22.78, 40.08, 31.62, 98.84, -22.78, 40.08, 31.62, 98.84, -22.78]
    ]
    
    
    for angles in sequence:     
        fnx.set_servo_values_paced(angles)
    """