import smbus
import time

class as5600:
    address = None
    bus = None

    ZMCO = 0x00
    ZPOS_HI = 0x01
    ZPOS_LO = 0x02
    MPOS_HI = 0x03
    MPOS_LO = 0x04
    MANG_HI = 0x05
    MANG_LO = 0x06
    CONF_HI = 0x07
    CONF_LO = 0x08
    RAW_ANG_HI = 0x0c
    RAW_ANG_LO = 0x0d
    ANG_HI = 0x0e
    ANG_LO = 0x0f
    STAT = 0x0b
    AGC = 0x1a
    MAG_HI = 0x1b
    MAG_LO = 0x1c
    BURN = 0xff

    def __init__(self, address=0x36, bus=1):
        self.address = address
        self.bus = smbus.SMBus(bus)

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

    def get_raw_angle(self):
        return self.read_i2c_word(self.RAW_ANG_HI)

    """
    def detect_magnet(self):
        mag_status = self.bus.read_byte_data(self.address, STAT)

        if mag_status & 0x20:
            return 1

        return 0
    """
    def get_magnet_strength(self):
        """
        0 if no magnet is detected
        1 if magnet is to weak
        2 if magnet is just right
        3 if magnet is to strong
        """
        mag_status = self.bus.read_byte_data(self.address, self.STAT)
        #if self.detect_magnet():         
        if mag_status & 0x20:   
            if mag_status & 0x10:
                return 1
            elif mag_status & 0x08:
                return 3
            else:
                return 2
        else:
            return 0

    def get_magnitude(self):
        return self.read_i2c_word(self.MAG_HI)

    def get_real_angle(self):
        # Raw data reports 0 - 4095 segments, which is 0.087 of a degree
        return round(self.get_raw_angle() * 0.087, 2)


"""
AS = as5600()
while True:
    try:
        print('Strength : {0}'.format(AS.get_magnet_strength()))
        #print('AngleRaw : {0}'.format(AS.get_raw_angle()))
        #print('Magnitude : {0}'.format(AS.get_magnitude()))
        print('Angle_real : {0}'.format(AS.get_real_angle()))
    except Exception as e:
        print(str(e))
    time.sleep(0.1)
"""