#!/usr/bin/env  python3

import CHIP_IO.SOFTPWM as pwm
import CHIP_IO.GPIO as GPIO
import CHIP_IO.Utilities
import time
import numpy
import threading

class Fire (threading.Thread):
    def __init__(self, red_ctl, yellow_ctl):
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
        self.yellow_percent_increment = 0.01

        self.freq = 100
        self.fire_update_delay = 0.005

        self.red = red_ctl
        self.yellow = yellow_ctl

        self.running = True
        self.unlock = threading.Event()

    def setup(self):
        # reset gpio
        GPIO.cleanup(self.red)
        GPIO.cleanup(self.yellow)
        CHIP_IO.Utilities.unexport_all()

         # init gpio
        pwm.start(self.red, 0, self.freq)
        pwm.start(self.yellow, 0, self.freq)

    def run(self):
        # init variables
        noise = numpy.random.normal
        random = numpy.random.randint

        red_sweeping = False
        red_sweep_increment = 0
        red_duty = 0
        red_target = 0

        yellow_ud_percent = 0
        yellow_cooldown = 0

        # main loop
        while True:
            if not self.running:
                self.unlock.wait()
            ## handle red
            if red_sweeping:
                if red_duty < red_target:
                    red_duty += red_sweep_increment
                    if red_duty >= red_target:
                        red_sweeping = False
                else:
                    red_duty -= red_sweep_increment
                    if red_duty <= red_target:
                        red_sweeping = False
                red_duty = max(min(red_duty, 100), 0)
                pwm.set_duty_cycle(self.red, red_duty)
            elif random(0, 100) < self.red_ud_percent:
                red_sweeping = True
                red_target = max(min(noise(self.red_mean, self.red_sigma), 100), 0)
                red_sweep_increment = abs(red_duty - red_target) / max(self.red_sweep_sigma, noise(self.red_sweep_mean, self.red_sweep_sigma))

            ## handle yellow
            if yellow_cooldown <= 0: # yellow off
                if random(0, 100) < yellow_ud_percent:
                    yellow_cooldown = noise(self.yellow_on_mean, self.yellow_on_sigma)
                    yellow_ud_percent = 0
                else:
                    yellow_ud_percent += self.yellow_percent_increment
            else:
                yellow_cooldown -= self.fire_update_delay
                if yellow_cooldown <= 0:
                    pwm.set_duty_cycle(self.yellow, 0)
                else:
                    pwm.set_duty_cycle(self.yellow, max(min((abs(self.yellow_mean - noise(self.yellow_mean, self.yellow_sigma)) * self.yellow_mult), 100), 0))

            ## wait some time
            time.sleep(self.fire_update_delay)

    def go(self):
        self.running = True
        self.unlock.set()

    def stop(self):
        self.running = False

if __name__ == "__main__":
    f = Fire("XIO-P1", "XIO-P0")
    f.setup()
    f.run()
