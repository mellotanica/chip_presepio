#!/usr/bin/env python3

import star
s = star.Star("CSID7")

import fire
f = fire.Fire("XIO-P1", "XIO-P3")

import animate
animator = animate.Animator()

animator.post_updater(f)
animator.post_updater(s)


import time
while True:
    time.sleep(100)
