#!/usr/bin/env  python3

import CHIP_IO.SOFTPWM as pwm
import CHIP_IO.GPIO as GPIO
import CHIP_IO.Utilities
import numpy
from animate import Updater

class Fire (Updater):
    def __init__(self, red_ctl, yellow_ctl, update_delay=0.02):
        Updater.__init__(self, update_delay)

        ### SETUP ###
        self.red_ud_percent = 40
        self.red_mean = 50
        self.red_sigma = 15

        self.red_sweep_mean = 6
        self.red_sweep_sigma = 1

        self.yellow_mean = 50
        self.yellow_sigma = 10
        self.yellow_mult = 0.8

        self.yellow_on_mean = 0.1
        self.yellow_on_sigma = 0.1
        self.yellow_percent_increment = 0.05

        self.freq = 100
        self.fire_update_delay = update_delay

        self.red = red_ctl
        self.yellow = yellow_ctl

        self.initialized = False

    def setup(self):
        if not self.initialized:
            # reset gpio
            GPIO.cleanup(self.red)
            GPIO.cleanup(self.yellow)

             # init gpio
            pwm.start(self.red, 0, self.freq)
            pwm.start(self.yellow, 0, self.freq)

            self.initialized = True

            # init variables
            self.red_sweeping = False
            self.red_sweep_increment = 0
            self.red_duty = 0
            self.red_target = 0

            self.yellow_ud_percent = 0
            self.yellow_cooldown = 0

    def cycle(self):
        self.setup()

        ## handle red
        if self.red_sweeping:
            if self.red_duty < self.red_target:
                self.red_duty += self.red_sweep_increment
                if self.red_duty >= self.red_target:
                    self.red_sweeping = False
            else:
                self.red_duty -= self.red_sweep_increment
                if self.red_duty <= self.red_target:
                    self.red_sweeping = False
            self.red_duty = max(min(self.red_duty, 100), 0)
            pwm.set_duty_cycle(self.red, self.red_duty)
        elif numpy.random.randint(0, 100) < self.red_ud_percent:
            self.red_sweeping = True
            self.red_target = max(min(numpy.random.normal(self.red_mean, self.red_sigma), 100), 0)
            self.red_sweep_increment = abs(self.red_duty - self.red_target) / max(self.red_sweep_sigma, numpy.random.normal(self.red_sweep_mean, self.red_sweep_sigma))

        ## handle yellow
        if self.yellow_cooldown <= 0: # yellow off
            if numpy.random.randint(0, 100) < self.yellow_ud_percent:
                self.yellow_cooldown = numpy.random.normal(self.yellow_on_mean, self.yellow_on_sigma)
                self.yellow_ud_percent = 0
            else:
                self.yellow_ud_percent += self.yellow_percent_increment
        else:
            self.yellow_cooldown -= self.fire_update_delay
            if self.yellow_cooldown <= 0:
                pwm.set_duty_cycle(self.yellow, 0)
            else:
                pwm.set_duty_cycle(self.yellow, max(min((abs(self.yellow_mean - numpy.random.normal(self.yellow_mean, self.yellow_sigma)) * self.yellow_mult), 100), 0))

    def clear(self):
        pwm.set_duty_cycle(self.red, 0)
        pwm.set_duty_cycle(self.yellow, 0)

if __name__ == "__main__":
    from animate import Animator
    import time

    f = Fire("XIO-P2", "XIO-P0")

    animator = Animator()
    animator.post_updater(f)

    while True:
        time.sleep(100)
