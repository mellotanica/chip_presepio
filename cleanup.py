#!/usr/bin/env  python3

import CHIP_IO.GPIO as GPIO
import CHIP_IO.Utilities

red = "XIO-P1"
yellow = "XIO-P0"

GPIO.cleanup(red)
GPIO.cleanup(yellow)
CHIP_IO.Utilities.unexport_all()

GPIO.setup(red, GPIO.OUT)
GPIO.setup(yellow, GPIO.OUT)

GPIO.output(red, GPIO.LOW)
GPIO.output(yellow, GPIO.LOW)

GPIO.cleanup(red)
GPIO.cleanup(yellow)
CHIP_IO.Utilities.unexport_all()

