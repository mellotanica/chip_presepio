#!/usr/bin/env  python3

import CHIP_IO.SOFTPWM as pwm
import CHIP_IO.GPIO as GPIO
import CHIP_IO.Utilities
import math
from animate import Updater

class Star (Updater):
    def __init__(self, led_ctl, update_delay=0.01):
        Updater.__init__(self, update_delay)

        ### SETUP ###
        self.freq = 100
        self.update_delay = update_delay

        self.led = led_ctl

        self.min_value = 30
        self.max_value = 100
        self.sweep_time = 4 #sec

        self.initialized = False

    def setup(self):
        if not self.initialized:
            # reset gpio
            GPIO.cleanup(self.led)

             # init gpio
            pwm.start(self.led, 0, self.freq)
            self.currenta_angle = 0

            self.delta = self.max_value - self.min_value
            self.angle_increment = (self.update_delay * 180) / (self.sweep_time * 60)

            self.initialized = True

    def cycle(self):
        self.setup()

        dc = self.min_value + abs(math.sin(self.currenta_angle) * self.delta)
        self.currenta_angle = (self.currenta_angle + self.angle_increment) % 360
        pwm.set_duty_cycle(self.led, dc)

    def clear(self):
        pwm.set_duty_cycle(self.led, 0)

if __name__ == "__main__":
    from animate import Animator
    import time

    s = Star("CSID7")

    animator = Animator()
    animator.post_updater(s)

    while True:
        time.sleep(100)
