from modules.pwm_led import PWM_LED
import time

led = PWM_LED(10)
time.sleep(1)
led.blink(2, 0.007)
time.sleep(1)
led.set_duty_cycle(100, instant=True)
time.sleep(3)


#led_back = LED(10)
#led_back.on()

#led_front.off()
#led_back.off()
