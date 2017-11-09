#!/usr/bin/env  python3

import CHIP_IO.SOFTPWM as pwm
import CHIP_IO.GPIO as GPIO
import CHIP_IO.Utilities
import time
import numpy


### SETUP ###

red_ud_percent = 40
red_mean = 50
red_sigma = 15

red_sweep_mean = 6
red_sweep_sigma = 1

yellow_mean = 50
yellow_sigma = 10
yellow_mult = 0.8

yellow_on_mean = 0.1
yellow_on_sigma = 0.1
yellow_percent_increment = 0.01

freq = 100
fire_update_delay = 0.005

red = "XIO-P1"
yellow = "XIO-P0"

#### CODE ####

# reset gpio
GPIO.cleanup(red)
GPIO.cleanup(yellow)
CHIP_IO.Utilities.unexport_all()

# init variables
noise = numpy.random.normal
random = numpy.random.randint

red_sweeping = False
red_sweep_increment = 0
red_duty = 0
red_target = 0

yellow_ud_percent = 0
yellow_cooldown = 0

# init gpio
pwm.start(red, 0, freq)
pwm.start(yellow, 0, freq)

# main loop
while True:
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
        pwm.set_duty_cycle(red, red_duty)
    elif random(0, 100) < red_ud_percent:
        red_sweeping = True
        red_target = max(min(noise(red_mean, red_sigma), 100), 0)
        red_sweep_increment = abs(red_duty - red_target) / max(red_sweep_sigma, noise(red_sweep_mean, red_sweep_sigma))

    ## handle yellow
    if yellow_cooldown <= 0: # yellow off
        if random(0, 100) < yellow_ud_percent:
            yellow_cooldown = noise(yellow_on_mean, yellow_on_sigma)
            yellow_ud_percent = 0
        else:
            yellow_ud_percent += yellow_percent_increment
    else:
        yellow_cooldown -= fire_update_delay
        if yellow_cooldown <= 0:
            pwm.set_duty_cycle(yellow, 0)
        else:
            pwm.set_duty_cycle(yellow, max(min((abs(yellow_mean - noise(yellow_mean, yellow_sigma)) * yellow_mult), 100), 0))

    ## wait some time
    time.sleep(fire_update_delay)

