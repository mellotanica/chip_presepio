#!/usr/bin/env python3

import CHIP_IO.SOFTPWM as SPWM
import CHIP_IO.Utilities
import time

p0 = "XIO-P0"
p1 = "XIO-P1"
freq = 50
sweep_freq = 0.0005

duty = 0

CHIP_IO.Utilities.unexport_all()

SPWM.start(p0, duty, freq)

while duty < 100:
    time.sleep(sweep_freq)
    SPWM.set_duty_cycle(p0, min(duty, 100))
    duty += 0.1

duty = 100

SPWM.start(p1, 0, freq)

while duty > 0:
    time.sleep(sweep_freq)
    SPWM.set_duty_cycle(p0, max(duty, 0))
    SPWM.set_duty_cycle(p1, max(100-duty, 0))
    duty -= 0.1

SPWM.cleanup(p0)

duty = 100

while duty > 0:
    time.sleep(sweep_freq)
    SPWM.set_duty_cycle(p1, max(duty, 0))
    duty -= 0.1

SPWM.cleanup(p1)
