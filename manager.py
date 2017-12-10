#!/usr/bin/env python3

import time
import CHIP_IO.GPIO as gpio
import CHIP_IO.Utilities

import pir
from fire import Fire
from relay import Relay
from star import Star

sensor_ctl = "CSID1"
relay_ctl = "CSID2"
star_ctl = "CSID7"

# each fire is identified by a touple (red, yellow)
fires_ctl = [
        ("XIO-P1", "XIO-P3"), 
        ("XIO-P0", "XIO-P2")
]

CHIP_IO.Utilities.unexport_all()

relay = Relay(relay_ctl, False, False)
relay.c()

sensor = pir.get_pir(sensor_ctl, gpio.PUD_UP)

sensor.register_callback(relay.c, False)

fires = []
for f in fires_ctl:
    fire = Fire(f[0], f[1])
    fire.stop()
    fire.start()
    fires.append(fire)
    sensor.register_callbacks(fire.go, fire.stop)

s = Star(star_ctl)
s.stop()
s.start()
sensor.register_callbacks(s.go, s.stop)

sensor.register_callback(relay.o, True)

sensor.replay_action()

while True:
    time.sleep(100)

