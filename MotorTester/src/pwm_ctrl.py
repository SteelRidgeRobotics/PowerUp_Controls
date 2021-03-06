from pyb import Pin, Timer, ADC

PWM_FREQ = 400  # 400 Hz -> 2500 us period
PIN_CH1 = 'X9'
PIN_CH2 = 'X10'
PIN_ADC = 'X19'
EVENT_TIMER = 1
MOTOR_TIMER = 4

STOP_PW = 1500              # 1500 ms for stop
BACKWARD_PW = 1000     # 1000 ms for full backward speed
FORWARD_PW = 2000       # 2000 ms for full forward speed

class motorController(object):
    
    def __init__(self, pin_name, timer_obj, ch_num, freq=PWM_FREQ):
        self.pin = Pin(pin_name)
        self.timer = timer_obj
        self.ch = self.timer.channel(ch_num, Timer.PWM, pin=self.pin)
        self.stop()
        
    def _set_pw(self, pulse_width):
        period_count = self.timer.period()
        period_time = 1000000 // self.timer.freq()
        width = (period_count + 1) * pulse_width // period_time
        self.ch.pulse_width(width)
    
    def stop(self):
        self._set_pw(STOP_PW)

def loop(adc, ch1, ch2):
    while True:
        raw = adc.read()
        pw = (FORWARD_PW - BACKWARD_PW) * raw // 4096 + BACKWARD_PW
        print(raw, pw)
        ch1._set_pw(pw)
        ch2._set_pw(pw)
        yield

def main():
    pwm_timer = Timer(MOTOR_TIMER, freq=PWM_FREQ)
    
    ch1 = motorController(PIN_CH1, pwm_timer, 1)
    ch2 = motorController(PIN_CH2, pwm_timer, 2)
    
    adc = ADC(PIN_ADC)
    main_loop = loop(adc, ch1, ch2)
    
    event_timer = Timer(EVENT_TIMER, freq=1000)
    event_timer.freq(10)
    event_timer.callback(lambda t: next(main_loop))
    
main()
