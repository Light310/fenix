import smbus
import time
import math
import sys
import socket


class mpu6050:
    # Global Variables
    GRAVITIY_MS2 = 9.80665
    address = None
    bus = None

    # Scale Modifiers
    ACCEL_SCALE_MODIFIER_2G = 16384.0
    ACCEL_SCALE_MODIFIER_4G = 8192.0
    ACCEL_SCALE_MODIFIER_8G = 4096.0
    ACCEL_SCALE_MODIFIER_16G = 2048.0

    GYRO_SCALE_MODIFIER_250DEG = 131.0
    GYRO_SCALE_MODIFIER_500DEG = 65.5
    GYRO_SCALE_MODIFIER_1000DEG = 32.8
    GYRO_SCALE_MODIFIER_2000DEG = 16.4

    # Pre-defined ranges
    ACCEL_RANGE_2G = 0x00
    ACCEL_RANGE_4G = 0x08
    ACCEL_RANGE_8G = 0x10
    ACCEL_RANGE_16G = 0x18

    GYRO_RANGE_250DEG = 0x00
    GYRO_RANGE_500DEG = 0x08
    GYRO_RANGE_1000DEG = 0x10
    GYRO_RANGE_2000DEG = 0x18

    # MPU-6050 Registers
    PWR_MGMT_1 = 0x6B
    PWR_MGMT_2 = 0x6C

    ACCEL_XOUT0 = 0x3B
    ACCEL_YOUT0 = 0x3D
    ACCEL_ZOUT0 = 0x3F

    TEMP_OUT0 = 0x41

    GYRO_XOUT0 = 0x43
    GYRO_YOUT0 = 0x45
    GYRO_ZOUT0 = 0x47

    ACCEL_CONFIG = 0x1C
    GYRO_CONFIG = 0x1B

    def __init__(self, address, bus=1, calibrate=False):
        self.address = address
        self.bus = smbus.SMBus(bus)
        # Wake up the MPU-6050 since it starts in sleep mode
        self.bus.write_byte_data(self.address, self.PWR_MGMT_1, 0x00)

        # not using accel calibration as it is impossible to put it perfectly horizontal
        self.accel_x_offset = 0
        self.accel_y_offset = 0
        self.accel_z_offset = 0

        if calibrate:
            self.gyro_x_offset = 0
            self.gyro_y_offset = 0
            self.gyro_z_offset = 0

            self.gyro_calibration()
        else:
            self.gyro_x_offset = -1237
            self.gyro_y_offset = -347
            self.gyro_z_offset = -81

    # I2C communication methods

    def read_i2c_word(self, register):
        """Read two i2c registers and combine them.
        register -- the first register to read from.
        Returns the combined read results.
        """
        # Read the data from the registers
        high = self.bus.read_byte_data(self.address, register)
        low = self.bus.read_byte_data(self.address, register + 1)

        value = (high << 8) + low

        if (value >= 0x8000):
            return -((65535 - value) + 1)
        else:
            return value

    # MPU-6050 Methods

    def get_temp(self):
        """Reads the temperature from the onboard temperature sensor of the MPU-6050.
        Returns the temperature in degrees Celcius.
        """
        raw_temp = self.read_i2c_word(self.TEMP_OUT0)

        # Get the actual temperature using the formulae given in the
        # MPU-6050 Register Map and Descriptions revision 4.2, page 30
        actual_temp = (raw_temp / 340.0) + 36.53

        return actual_temp

    def set_accel_range(self, accel_range):
        """Sets the range of the accelerometer to range.
        accel_range -- the range to set the accelerometer to. Using a
        pre-defined range is advised.
        """
        # First change it to 0x00 to make sure we write the correct value later
        self.bus.write_byte_data(self.address, self.ACCEL_CONFIG, 0x00)

        # Write the new range to the ACCEL_CONFIG register
        self.bus.write_byte_data(self.address, self.ACCEL_CONFIG, accel_range)

    def read_accel_range(self, raw=False):
        """Reads the range the accelerometer is set to.
        If raw is True, it will return the raw value from the ACCEL_CONFIG
        register
        If raw is False, it will return an integer: -1, 2, 4, 8 or 16. When it
        returns -1 something went wrong.
        """
        raw_data = self.bus.read_byte_data(self.address, self.ACCEL_CONFIG)

        if raw is True:
            return raw_data
        elif raw is False:
            if raw_data == self.ACCEL_RANGE_2G:
                return 2
            elif raw_data == self.ACCEL_RANGE_4G:
                return 4
            elif raw_data == self.ACCEL_RANGE_8G:
                return 8
            elif raw_data == self.ACCEL_RANGE_16G:
                return 16
            else:
                return -1

    @property
    def accel_scale_modifier(self):
        accel_range = self.read_accel_range(True)

        if accel_range == self.ACCEL_RANGE_2G:
            return self.ACCEL_SCALE_MODIFIER_2G
        elif accel_range == self.ACCEL_RANGE_4G:
            return self.ACCEL_SCALE_MODIFIER_4G
        elif accel_range == self.ACCEL_RANGE_8G:
            return self.ACCEL_SCALE_MODIFIER_8G
        elif accel_range == self.ACCEL_RANGE_16G:
            return self.ACCEL_SCALE_MODIFIER_16G
        else:
            print("Unkown range - accel_scale_modifier set to self.ACCEL_SCALE_MODIFIER_2G")
            return self.ACCEL_SCALE_MODIFIER_2G

    @property
    def gyro_scale_modifier(self):
        gyro_range = self.read_gyro_range(True)

        if gyro_range == self.GYRO_RANGE_250DEG:
            return self.GYRO_SCALE_MODIFIER_250DEG
        elif gyro_range == self.GYRO_RANGE_500DEG:
            return self.GYRO_SCALE_MODIFIER_500DEG
        elif gyro_range == self.GYRO_RANGE_1000DEG:
            return self.GYRO_SCALE_MODIFIER_1000DEG
        elif gyro_range == self.GYRO_RANGE_2000DEG:
            return self.GYRO_SCALE_MODIFIER_2000DEG
        else:
            print("Unkown range - gyro_scale_modifier set to self.GYRO_SCALE_MODIFIER_250DEG")
            return self.GYRO_SCALE_MODIFIER_250DEG

    def get_accel_data(self, g=False, scaled=True):
        """Gets and returns the X, Y and Z values from the accelerometer.
        If g is True, it will return the data in g
        If g is False, it will return the data in m/s^2
        Returns a dictionary with the measurement results.
        """
        x = self.read_i2c_word(self.ACCEL_XOUT0)
        y = self.read_i2c_word(self.ACCEL_YOUT0)
        z = self.read_i2c_word(self.ACCEL_ZOUT0)

        x -= self.accel_x_offset
        y -= self.accel_y_offset
        z -= self.accel_z_offset

        if scaled:
            x /= self.accel_scale_modifier
            y /= self.accel_scale_modifier
            z /= self.accel_scale_modifier

        if g is True:
            return {'x': x, 'y': y, 'z': z}
        elif g is False:
            x *= self.GRAVITIY_MS2
            y *= self.GRAVITIY_MS2
            z *= self.GRAVITIY_MS2
            return {'x': x, 'y': y, 'z': z}

    def set_gyro_range(self, gyro_range):
        """Sets the range of the gyroscope to range.
        gyro_range -- the range to set the gyroscope to. Using a pre-defined
        range is advised.
        """
        # First change it to 0x00 to make sure we write the correct value later
        self.bus.write_byte_data(self.address, self.GYRO_CONFIG, 0x00)

        # Write the new range to the ACCEL_CONFIG register
        self.bus.write_byte_data(self.address, self.GYRO_CONFIG, gyro_range)

    def read_gyro_range(self, raw=False):
        """Reads the range the gyroscope is set to.
        If raw is True, it will return the raw value from the GYRO_CONFIG
        register.
        If raw is False, it will return 250, 500, 1000, 2000 or -1. If the
        returned value is equal to -1 something went wrong.
        """
        raw_data = self.bus.read_byte_data(self.address, self.GYRO_CONFIG)

        if raw is True:
            return raw_data
        elif raw is False:
            if raw_data == self.GYRO_RANGE_250DEG:
                return 250
            elif raw_data == self.GYRO_RANGE_500DEG:
                return 500
            elif raw_data == self.GYRO_RANGE_1000DEG:
                return 1000
            elif raw_data == self.GYRO_RANGE_2000DEG:
                return 2000
            else:
                return -1

    def get_gyro_data(self, scaled=True):
        """Gets and returns the X, Y and Z values from the gyroscope.
        Returns the read values in a dictionary.
        """
        x = self.read_i2c_word(self.GYRO_XOUT0)
        y = self.read_i2c_word(self.GYRO_YOUT0)
        z = self.read_i2c_word(self.GYRO_ZOUT0)

        x -= self.gyro_x_offset
        y -= self.gyro_y_offset
        z -= self.gyro_z_offset

        if scaled:
            x /= self.gyro_scale_modifier
            y /= self.gyro_scale_modifier
            z /= self.gyro_scale_modifier

        return {'x': x, 'y': y, 'z': z}

    def get_all_data(self, scaled=True):
        """Reads and returns all the available data."""
        temp = self.get_temp()
        accel = self.get_accel_data(g=True, scaled=scaled)
        gyro = self.get_gyro_data(scaled=scaled)

        return [accel, gyro, temp]

    def gyro_calibration(self):
        print('Calibration started')
        gyro_mean_x, gyro_mean_y, gyro_mean_z = 0, 0, 0
        attempts = 1000

        for i in range(attempts):
            gyro = self.get_gyro_data(scaled=False)
            gyro_mean_x += gyro['x']
            gyro_mean_y += gyro['y']
            gyro_mean_z += gyro['z']

            time.sleep(0.002)

        self.gyro_x_offset = int(gyro_mean_x / attempts)
        self.gyro_y_offset = int(gyro_mean_y / attempts)
        self.gyro_z_offset = int(gyro_mean_z / attempts)
        print('Calibration finished. X : {0}, Y : {1}, Z : {2}'
              .format(self.gyro_x_offset, self.gyro_y_offset, self.gyro_z_offset))


    @staticmethod
    def get_y_rotation(x, y, z):
        dist = math.sqrt((y*y)+(z*z))
        radians = math.atan2(x, dist)
        return -math.degrees(radians)

    @staticmethod
    def get_x_rotation(x, y, z):
        dist = math.sqrt((x * x) + (z * z))
        radians = math.atan2(y, dist)
        return math.degrees(radians)

    @staticmethod
    def get_z_rotation(x, y, z):
        dist = math.sqrt((x * x) + (y * y))
        radians = math.atan2(z, dist)
        return math.degrees(radians)

    def run_complementary_filter(self):
        alpha = 0.02
        dt = 0.01

        acc_data = self.get_accel_data(scaled=False)
        acc_xrot_angle = self.get_x_rotation(acc_data['x'], acc_data['y'], acc_data['z'])
        acc_yrot_angle = self.get_y_rotation(acc_data['x'], acc_data['y'], acc_data['z'])
        acc_zrot_angle = self.get_z_rotation(acc_data['x'], acc_data['y'], acc_data['z'])

        angle_x = acc_xrot_angle
        angle_y = acc_yrot_angle
        angle_z = acc_zrot_angle
        last_reading_time = time.time()
        time.sleep(dt)

        HOST = '78.46.205.128'
        PORT = 65432       
        i = 0

        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((HOST, PORT))
            while True:
              try:
                acc_data = self.get_accel_data(scaled=False)
                gyro_data = self.get_gyro_data(scaled=True)

                #force_magnitude_approx = abs(acc_data['x']) + abs(acc_data['y']) + abs(acc_data['z'])
                #if force_magnitude_approx < 8192 or force_magnitude_approx > 32768:
                #    print('Bad accel value : {0}'.format(force_magnitude_approx))
                #    continue

                acc_xrot_angle = self.get_x_rotation(acc_data['x'], acc_data['y'], acc_data['z'])
                acc_yrot_angle = self.get_y_rotation(acc_data['x'], acc_data['y'], acc_data['z'])
                acc_zrot_angle = self.get_z_rotation(acc_data['x'], acc_data['y'], acc_data['z'])

                gyro_reading_delta = time.time() - last_reading_time
                last_reading_time = time.time()
                #gyro_reading_delta = dt

                angle_x = (1.0 - alpha) * (angle_x + gyro_data['x'] * gyro_reading_delta) + (alpha * acc_xrot_angle)
                angle_y = (1.0 - alpha) * (angle_y + gyro_data['y'] * gyro_reading_delta) + (alpha * acc_yrot_angle)
                angle_z = (1.0 - alpha) * (angle_z + gyro_data['z'] * gyro_reading_delta) + (alpha * acc_zrot_angle)
                 
                if i%20 == 0:
                    item = '{0},{1},{2}'.format(round(angle_x, 2), round(angle_y, 2), round(angle_z, 2))
                    print('Sending data : ', item)
                    s.sendall(item.encode())

                print('Angles : {0}. Reading delta : {1}'
                      .format([round(angle_x, 2), round(angle_y, 2), round(angle_z, 2)],
                              round(gyro_reading_delta, 5)))

                time.sleep(dt)
                i += 1

              except Exception as e:
                print(str(e))


if __name__ == "__main__":
    mpu = mpu6050(0x68, calibrate=True)
    mpu.run_complementary_filter()
