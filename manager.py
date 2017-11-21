#!/usr/bin/env python3

import time

import sensor
from fire import Fire
from relay import Relay

relay_ctl = "CSID0"
sensor_ctl = "CSID1"
# each fire is identified by a touple (red, yellow)
fires_ctl = [
        ("XIO-P0", "XIO-P1"), 
        ("XIO-P2", "XIO-P3")
]

relay = Relay(relay_ctl)

sensor.register_callback(sensor_ctl, relay.a, False)

fires = []
for f in fires_ctl:
    fire = Fire(f[0], f[1])
    fire.stop()
    fire.start()
    fires.append(fire)
    sensor.register_callbacks(sensor_ctl, fire.go, fire.stop)

sensor.register_callback(sensor_ctl, relay.nb, True)

while True:
    time.sleep(100)

