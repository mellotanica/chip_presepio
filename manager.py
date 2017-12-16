#!/usr/bin/env python3

import time
import CHIP_IO.GPIO as gpio
import CHIP_IO.Utilities

import sensor
from fire import Fire
from relay import Relay
from star import Star
from animate import Animator

sensor_ctl = "CSID1"
relay_ctl = "CSID2"
star_ctl = "CSID7"

# each fire is identified by a touple (red, yellow)
fires_ctl = [
        ("XIO-P3", "XIO-P1"), 
        ("XIO-P2", "XIO-P0")
]

CHIP_IO.Utilities.unexport_all()

animator = Animator()

relay = Relay(relay_ctl, False, False)
relay.c()

sensor = sensor.get_sensor(sensor_ctl, gpio.PUD_UP, 180)

sensor.register_callback(relay.c, False)

for f in fires_ctl:
    fire = Fire(f[0], f[1])
    animator.post_updater(fire)
    sensor.register_callbacks(fire.go, fire.stop)

s = Star(star_ctl)
animator.post_updater(s)
sensor.register_callbacks(s.go, s.stop)

sensor.register_callback(relay.o, True)

sensor.replay_action()

while True:
    time.sleep(100)

