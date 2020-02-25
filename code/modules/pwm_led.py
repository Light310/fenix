import RPi.GPIO as GPIO
import time


class PWM_LED:
    def __init__(self, pin=10):
        GPIO.setmode(GPIO.BOARD)         # We are using the BOARD pin numbering
        GPIO.setup(pin, GPIO.OUT)        # Declaring pin as output
        self.pwm = GPIO.PWM(pin, 100)    # Created a PWM object
        self.pwm.start(0)                     # Started PWM at 0% duty cycle
        self.duty_cycle = 0
	
    def blink(self, times=3, sleep_time=0.01):
        for _ in range(times):                    
            for x in range(100):    # This Loop will run 100 times				
                self.pwm.ChangeDutyCycle(x) # Change duty cycle
                time.sleep(sleep_time)         # Delay of 10mS
			
            for x in range(100,0,-1): # Loop will run 100 times; 100 to 0				
                self.pwm.ChangeDutyCycle(x)
                time.sleep(sleep_time)
			
            self.duty_cycle = 0
				
    def set_duty_cycle(self, pct, instant=False):
        if instant:
            self.pwm.ChangeDutyCycle(pct) # Change duty cycle
        else:
            from_range = self.duty_cycle
            if pct > from_range:
                coef = 1
            else:
                coef = -1

            for x in range(from_range, pct, coef):		    
                self.pwm.ChangeDutyCycle(x) # Change duty cycle
                time.sleep(0.01)            # Delay of 10mS
		
        self.duty_cycle = pct
	
		
    def __del__(self):
        self.pwm.stop()