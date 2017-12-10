#!/usr/bin/env  python3

import CHIP_IO.SOFTPWM as pwm
import CHIP_IO.GPIO as GPIO
import CHIP_IO.Utilities
import time
import math
import threading

class Star (threading.Thread):
    def __init__(self, led_ctl):
        threading.Thread.__init__(self)
        self.daemon = True

        ### SETUP ###
        self.freq = 100
        self.update_delay = 0.02

        self.led = led_ctl

        self.min_value = 50
        self.max_value = 100
        self.sweep_time = 4 #sec

        self.running = True
        self.unlock = threading.Event()

        self.initialized = False
        self.started = False

    def setup(self):
        if not self.initialized:
            # reset gpio
            GPIO.cleanup(self.led)

             # init gpio
            pwm.start(self.led, 0, self.freq)

            self.initialized = True

    def run(self):
        self.started = True

        self.setup()

        currenta_angle = 0
        delta = self.max_value - self.min_value
        angle_increment = (self.update_delay * 180) / (self.sweep_time * 60)

        # main loop
        while True:
            if not self.running:
                self.unlock.wait()

            dc = self.min_value + abs(math.sin(currenta_angle) * delta)
            currenta_angle = (currenta_angle + angle_increment) % 360
            pwm.set_duty_cycle(self.led, dc)

            ## wait some time
            time.sleep(self.update_delay)

    def go(self):
        self.running = True
        self.unlock.set()
        if not self.started:
            self.start()

    def stop(self):
        self.setup()
        self.unlock.clear()
        self.running = False
        pwm.set_duty_cycle(self.led, 0)

if __name__ == "__main__":
    s = Star("CSID7")
    s.start()

    while True:
        time.sleep(10)
