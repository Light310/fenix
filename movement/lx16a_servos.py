#!/usr/bin/python3
from time import sleep
from serial import Serial
import struct


neutral = {
   1 : 470,
   2 : 483,
   3 : 465,
   4 : 480,
   5 : 475,
   6 : 490,
   7 : 480,
   8 : 500,
   9 : 500,
   10 : 506,
   11 : 507,
   12 : 521,
   13 : 520,
   14 : 517,
   15 : 513,
   16 : 497
}

class LX16A:

  LED_OFF = 1
  LED_ON = 0

  LED_ERROR_NONE = 0
  LED_ERROR_OVER_TEMPERATURE=1
  LED_ERROR_OVER_VOLTAGE    =2
  LED_ERROR_OVER_TEMPERATURE_AND_VOLTAGE=3
  LED_ERROR_LOCK_ROTOR      =4
  LED_ERROR_OVER_TEMPERATE_AND_STALLED=5
  LED_ERROR_OVER_VOLTAGE_AND_STALLED=6
  LED_ERROR_OVER_ALL        = 7

  SERVO_FRAME_HEADER        =0x55
  SERVO_MOVE_TIME_WRITE     =1
  SERVO_MOVE_TIME_READ      =2
  SERVO_MOVE_TIME_WAIT_WRITE=7
  SERVO_MOVE_TIME_WAIT_READ =8
  SERVO_MOVE_START          =11
  SERVO_MOVE_STOP           =12
  SERVO_ID_WRITE            =13
  SERVO_ID_READ             =14
  SERVO_ANGLE_OFFSET_ADJUST =17
  SERVO_ANGLE_OFFSET_WRITE  =18
  SERVO_ANGLE_OFFSET_READ   =19
  SERVO_ANGLE_LIMIT_WRITE   =20
  SERVO_ANGLE_LIMIT_READ    =21
  SERVO_VIN_LIMIT_WRITE     =22
  SERVO_VIN_LIMIT_READ      =23
  SERVO_TEMP_MAX_LIMIT_WRITE=24
  SERVO_TEMP_MAX_LIMIT_READ =25
  SERVO_TEMP_READ           =26
  SERVO_VIN_READ            =27
  SERVO_POS_READ            =28
  SERVO_OR_MOTOR_MODE_WRITE =29
  SERVO_OR_MOTOR_MODE_READ  =30
  SERVO_LOAD_OR_UNLOAD_WRITE=31
  SERVO_LOAD_OR_UNLOAD_READ =32
  SERVO_LED_CTRL_WRITE      =33
  SERVO_LED_CTRL_READ       =34
  SERVO_LED_ERROR_WRITE     =35
  SERVO_LED_ERROR_READ      =36


  # declaration de l'objet connection au port serie

  def __init__(self,Port="/dev/ttyUSB0",Baudrate=115200, Timeout= 0.001):
     self.serial = Serial(Port,baudrate=Baudrate,timeout=Timeout)
     self.serial.setDTR(1)
     self.TX_DELAY_TIME = 0.00002 
     self.Header = struct.pack("<BB",0x55,0x55)


  # envoi du packet  ajout du header et du checksum
  def sendPacket(self,packet):
     sum = 0
     for item in packet:
        sum = sum + item
     fullPacket = bytearray(self.Header + packet + struct.pack("<B",(~sum) & 0xff))
     self.serial.write(fullPacket)

     sleep(self.TX_DELAY_TIME)

  #besoin d'ajouter exception et réessaie au cas si le checksum n'est pas bon
  # aussi verifier bon ID et commande dans retour
  def sendReceivePacket(self,packet,receiveSize):
      num_attempts = 3
      for i in range(num_attempts):
         t_id = packet[0]     
         t_command = packet[2]
         self.serial.flushInput()
         self.serial.timeout=0.1
         self.sendPacket(packet)
         r_packet = self.serial.read(receiveSize+3)
         #print('r_packet : {0}. Length : {1}'.format(r_packet, len(r_packet)))
         if len(r_packet) > 0: 
            return r_packet
         print('Attempt {0} failed.'.format(i))
      raise Exception('Got empty response in {0} attempts'.format(num_attempts))
        

  # Bouger le servo entre 0 et 1000 soit 0.24 degree resolution
  # rate est en ms  de 0(fast) a 30000(slow)
  def moveServo(self,id,position,rate=1000):
     packet = struct.pack("<BBBHH",id,7,
                          self.SERVO_MOVE_TIME_WRITE,
                          position,rate)
     self.sendPacket(packet)

  def moveServoToAngle(self, id, angle, rate=0):
      position = neutral[id] + int(angle/0.24)
      #print('For id {0} angle {1} converted to position {2}'.format(id, angle, position))
      for i in range(10):
         try:
            packet = struct.pack("<BBBHH",id,7,
                                 self.SERVO_MOVE_TIME_WRITE,
                                 position,rate)
            self.sendPacket(packet)
            #try:
            target = self.readServoTarget(id)[0]
            #print('Target required : {0}. Target real : {1}'.format(position, target))
            if target != position:
               print('Target required : {0}. Target real : {1}'.format(position, target))
               print('============ALARM=============')
               continue
            #print('{0} attempt succeded'.format(i))
            break
         except:
            print('{0} attempt failed for servo {1}'.format(i, id))
      #except:
      #   print('Error reading servo target')

  # Lire l'angle et le rate envoyer par moveServo
  # angle est entre 0 et 1000 siot 0.24 degree de resolution
  # rate est en ms  de 0(fast) a 30000(slow)
  def readServoTarget(self,id):
     packet = struct.pack("<BBB",id,3,self.SERVO_MOVE_TIME_READ)
     rpacket = self.sendReceivePacket(packet,7)
     s = struct.unpack("<BBBBBHHB",rpacket)
     #print(s)
     return s[5:7]

  # Bouger le servo entre 0 et 1000 soit 0.24 degree resolution
  # rate est en ms  de 0(fast) a 30000(slow)
  # **** Attendre pour la commande SERVO_MOVE_STOP
  def moveServoWait(self,id,position,rate=1000):
     packet = struct.pack("<BBBHH",id,7,
                          self.SERVO_MOVE_TIME_WAIT_WRITE,
                          position,rate)
     self.sendPacket(packet)

  # Lire l'angle et le rate envoyer par moveServoWait
  # angle est entre 0 et 1000 siot 0.24 degree de resolution
  # rate est en ms  de 0(fast) a 30000(slow)
  def readServoTargetWait(self,id):
     packet = struct.pack("<BBB",id,3,self.SERVO_MOVE_TIME_WAIT_READ)
     rpacket = self.sendReceivePacket(packet,7)
     s = struct.unpack("<BBBBBHHB",rpacket)
#     print(s)
     return s[5:7]

  #Partir une commande provenant de moveServoWait
  def moveServoStart(self,id):
     packet = struct.pack("<BBB",id,3,self.SERVO_MOVE_START)
     rpacket = self.sendPacket(packet)

  #Arreter une commande provenant de moveServoWait
  def moveServoStop(self,id):
     packet = struct.pack("<BBB",id,3,self.SERVO_MOVE_STOP)
     rpacket = self.sendPacket(packet)

  # change le ID du servo
  def setID(self,id,newid):
     packet = struct.pack("<BBBB",id,4,
                          self.SERVO_ID_WRITE,newid)
     self.sendPacket(packet)

  #Lire ID du servo
  # valeur 254 retourne l'ID du servo mais il faut un servo de branché.
  def readID(self,id):
     packet = struct.pack("<BBB",id,3,self.SERVO_ID_READ)
     rpacket = self.sendReceivePacket(packet,4)
     s = struct.unpack("<BBBBBBB",rpacket)
#     print(s)
     return s[5]

  #Change l'offset de l'angle sans la sauver lors du prochain  power ON
  # Angle entre -125 et 125 
  def setAngleOffsetAdjust(self,id,angle):
     packet = struct.pack("<BBBb",id,4,
                          self.SERVO_ANGLE_OFFSET_ADJUST,angle)
     self.sendPacket(packet)

  #Change l'offset de l'angle d'une facon permanente
  # Angle entre -125 et 125 
  def setAngleOffset(self,id,angle):
     packet = struct.pack("<BBBb",id,4,
                          self.SERVO_ANGLE_OFFSET_WRITE,angle)
     self.sendPacket(packet)

  #lire l'offset de l'angle
  #angle entre -125 et 125
  def readAngleOffset(self,id):
     packet = struct.pack("<BBB",id,3,self.SERVO_ANGLE_OFFSET_READ)
     rpacket = self.sendReceivePacket(packet,4)
     s = struct.unpack("<BBBBBbB",rpacket)
#     print(s)
     return s[5]

  #Definir l'angle minimum et maximum du servo
  # Angle  est entre 0 et 1000 Resolution de 0.24 degree
  def setAngleLimit(self,id,angleMin,angleMax):
     packet = struct.pack("<BBBHH",id,7,
                          self.SERVO_ANGLE_LIMIT_WRITE,angleMin,angleMax)
     self.sendPacket(packet)

  #Lire la limite minimum et maximum de l'angle permise
  def readAngleLimit(self,id):
     packet = struct.pack("<BBB",id,3,self.SERVO_ANGLE_LIMIT_READ)
     rpacket = self.sendReceivePacket(packet,7)
     s = struct.unpack("<BBBBBHHB",rpacket)
#     print(s)
     return s[5:7]

  #definir la tension minnimum et maximum d'operation du servo 
  # les valeurs sont en mv  min=6500 max=10000
  def setVoltageLimit(self,id,voltageMin,voltageMax):
     packet = struct.pack("<BBBHH",id,7,self.SERVO_VIN_LIMIT_WRITE,
                          voltageMin,voltageMax)
     rpacket = self.sendPacket(packet)

  #Lire la tension minnimum et maximum d'operation du servo 
  # les valeurs sont en mv  min=6500 max=10000
  def readVoltageLimit(self,id):
     packet = struct.pack("<BBB",id,3,self.SERVO_VIN_LIMIT_READ)
     rpacket = self.sendReceivePacket(packet,7)
     s = struct.unpack("<BBBBBHHB",rpacket)
#     print(s)
     return s[5:7]

  #definir la temperature maximale d'operation en celsius
  #defaux est  85 celsius   entre 50 et 100 celsius
  def setTemperatureLimit(self,id,temperatureMax):
     packet = struct.pack("<BBBB",id,4,self.SERVO_TEMP_MAX_LIMIT_WRITE,
                          temperatureMax)
     rpacket = self.sendPacket(packet)


  #Lire la limite de temperature maximale en celsius
  def readTemperatureLimit(self,id):
     packet = struct.pack("<BBB",id,3,self.SERVO_TEMP_MAX_LIMIT_READ)
     rpacket = self.sendReceivePacket(packet,4)
#     print(rpacket)
     s = struct.unpack("<BBBBBBB",rpacket)
#     print(s)
#     print("temp Limit is ",s[5])
     return s[5]

  #Lire la temperature en celsius
  def readTemperature(self,id):
     packet = struct.pack("<BBB",id,3,self.SERVO_TEMP_READ)
     rpacket = self.sendReceivePacket(packet,4)
#     print(rpacket)
     s = struct.unpack("<BBBBBBB",rpacket)
#     print(s)
#     print("temp is ",s[5])
     return s[5]

  #lire la tension d'alimentation du servo
  # La valeur est en mv
  def readVoltage(self,id):
     packet = struct.pack("<BBB",id,3,self.SERVO_VIN_READ)
     rpacket = self.sendReceivePacket(packet,5)
     s = struct.unpack("<BBBBBHB",rpacket)
     return s[5]

  #lire la position du servo
  #la valeur peut etre negative alors c'est  signed short
  def readPosition(self,id):     
       try:
         packet = struct.pack("<BBB",id,3,self.SERVO_POS_READ)
         rpacket = self.sendReceivePacket(packet,5)
         s = struct.unpack("<BBBBBhB",rpacket)
         return s[5]
       except:
         raise Exception('Can not read values from servo {0}'.format(id))

  def readAngle(self, id):
      return round((self.readPosition(id) - neutral[id]) * 0.24 , 2)

  # Bouge moteur avec vitesse   motorMode=1 MotorSpeed=rate
  # sinon set  servo mode =>   motorMode=0 
  def motorOrServo(self,id,motorMode,MotorSpeed):
     packet = struct.pack("<BBBBBh",id,7,
                          self.SERVO_OR_MOTOR_MODE_WRITE,
                          motorMode,0,MotorSpeed)
     self.sendPacket(packet)

  #lire le mode du serv0
  def readMotorOrServo(self,id):
     packet = struct.pack("<BBB",id,3,self.SERVO_OR_MOTOR_MODE_READ)
     rpacket = self.sendReceivePacket(packet,7)
     s = struct.unpack("<BBBBBBBhB",rpacket)
 #    print(s)
     return [s[5],s[7]]

  #Activer ou deactiver le moteur
  # 0 = motor OFF 1 = motor actif
  def LoadUnload(self,id,mode):
     packet = struct.pack("<BBBB",id,4,
                          self.SERVO_LOAD_OR_UNLOAD_WRITE,mode)
     self.sendPacket(packet)

  #Lire le status de l'activation du servo
  def readLoadUnload(self,id):
     packet = struct.pack("<BBB",id,3,
                          self.SERVO_LOAD_OR_UNLOAD_READ)
     rpacket = self.sendReceivePacket(packet,4)
     s = struct.unpack("<BBBBBBB",rpacket)
 #    print(s)
     return s[5]


  #Activer ou fermer la LED
  # 0 = on  => self.LED_ON
  # 1 = OFF => self.LED_OFF
  def setLed(self,id,ledState):
     packet = struct.pack("<BBBB",id,4,
                          self.SERVO_LED_CTRL_WRITE,ledState)
     self.sendPacket(packet)

  #Lire le status de l'activation de la led
  # 0 = LED active
  # 1 = LED OFF
  def readLed(self,id):
     packet = struct.pack("<BBB",id,3,self.SERVO_LED_CTRL_READ)
     rpacket = self.sendReceivePacket(packet,4)
     s = struct.unpack("<BBBBBBB",rpacket)
 #    print(s)
     return s[5]

  #Activer une erreur sur la led d'alarme
  def setLedError(self,id,ledError):
     packet = struct.pack("<BBBB",id,4,
                          self.SERVO_LED_ERROR_WRITE,ledError)
     self.sendPacket(packet)


  def readLedError(self,id):
     packet = struct.pack("<BBB",id,3,self.SERVO_LED_ERROR_READ)
     rpacket = self.sendReceivePacket(packet,4)
     s = struct.unpack("<BBBBBBB",rpacket)
 #    print(s)
     return s[5]


def get_position(servo, id):
   pos = servo.readPosition(id)
   target = servo.readServoTarget(id)
   return 'Angle: {0:5.2f}. Pos: {1:3d}. Target: {2:3d}'.format(convert_position_to_angle(neutral[id], pos), pos, target[0])


def get_state(servo, id):
   pos = servo.readPosition(id)
   temp = servo.readTemperature(id)
   volt = servo.readVoltage(id)
   target = servo.readServoTarget(id)
   return 'Pos: {0:5d}. Angle: {5:5.2f}. Target: {1:5d}, {2:5d}. Temp: {3:5d}. Volt: {4:5d}'.format(pos, target[0], target[1], temp, volt, convert_position_to_angle(neutral[id], pos))

def convert_position_to_angle(start, value):
   return round((value - start) * 0.24 , 2)

def read_values(m0, servo):
   try:
      pos = m0.readPosition(servo)
      temp = m0.readTemperature(servo)
      volt = m0.readVoltage(servo)
      target = m0.readServoTarget(servo)
      print('{5:2d}. Pos: {0:5d}. Target: {1:5d}, {2:5d}. Temp: {3:5d}. Volt: {4:5d}'
              .format(pos, target[0], target[1], temp, volt, servo))
   except:
      print('Could not read values from servo {0}'.format(servo))


if __name__ == '__main__':      
   m1 = LX16A(Port='/dev/ttyAMA0') # 5-8   # 1-4
   m2 = LX16A(Port='/dev/ttyAMA2') # 9-12  # 5-8
   m3 = LX16A(Port='/dev/ttyAMA3') # 13-16 # 9-12
   m4 = LX16A(Port='/dev/ttyAMA1') # 1-4   # 13-16
   #m2.moveServoToAngle(7, 45)
   
   
   for m in range(1):
      j = 1
      for m in [m1, m2, m3, m4]:
         for _ in range(4):
            read_values(m, j)
            j += 1
   """

   import datetime
   m1.moveServoToAngle(4, 0, 1000)
   sleep(2.0)
   m1.moveServoToAngle(4, -15, 1000)
   for i in range(20):
      print(datetime.datetime.now())
      read_values(m1, 4)
      sleep(0.1)
   
   # 90 degrees 16:01:33.297644 -> 16:01:34.496840 = 1.2 sec
   # 45 degrees 16:02:37.979423 -> 16:02:39.177309 = 1.2 sec
   # 15 degrees 16:03:28.401272 -> 16:03:29.600157 = 1.2 sec
   m1.moveServoToAngle(4, 0, 1000)
   sleep(2.0)
   """