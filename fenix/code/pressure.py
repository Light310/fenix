import smbus
import time

#init bus
bus = smbus.SMBus(1)

for i in range (100):
  # power up LPS331AP pressure sensor and 12.5Hz mode
  bus.write_byte_data(0x5c, 0x20, 0b11100000)

  #write value 0b1 to register 0x21 on device at address 0x5d
  #bus.write_byte_data(0x5c,0x21, 0b1)

  Temp_LSB = bus.read_byte_data(0x5c, 0x2b)
  Temp_MSB = bus.read_byte_data(0x5c, 0x2c)

  #combine LSB & MSB
  count = (Temp_MSB << 8) | Temp_LSB

  # As value is negative convert 2's complement to decimal
  comp = count - (1 << 16)

  #calc temp according to data sheet
  Temp = 42.5 + (comp/480.0)

  str = 'Temp. Raw: {0}. Converted: {1}.'.format(count, Temp)

  Pressure_LSB = bus.read_byte_data(0x5c, 0x29)
  Pressure_MSB = bus.read_byte_data(0x5c, 0x2a)
  Pressure_XLB = bus.read_byte_data(0x5c, 0x28)

  count = (Pressure_MSB << 16) | ( Pressure_LSB << 8 ) | Pressure_XLB
  #comp = count - (1 << 24)
  #Pressure value is positive so just use value as decimal 
  Pressure = count/4096.0 
  height = (1 - pow(Pressure / 1013.25, 0.190263)) * 44330.8

  str += ' Pressure. Raw: {0}. Pressure: {1}. Height : {2}'.format(count, Pressure, height)
  print(str)

  time.sleep(0.1)
