#!/usr/bin/env  python3

import CHIP_IO.GPIO as gpio
import CHIP_IO.Utilities
import threading
import time

class Sensor:
    def __init__(self, sensor_ctl, pud=gpio.PUD_UP):
        self.callbacks_high = []
        self.callbacks_low = []
        self.sensor = sensor_ctl
       
        gpio.cleanup(sensor_ctl)
        gpio.setup(sensor_ctl, gpio.IN, pull_up_down=pud)

        self.state = gpio.input(sensor_ctl)

    def register_callback(self, callback, high):
        if not callable(callback):
            print("WARNING: callback must be callable, not registering {}".format(callback))
            return
        if high:
            self.callbacks_high.append(callback)
        else:
            self.callbacks_low.append(callback)

    def read(self):
        val = gpio.input(self.sensor)
        if val != self.state:
            self.state = val
            cblist = None
            if val:
                cblist = self.callbacks_high
            else:
                cblist = self.callbacks_low
            for cb in cblist:
                cb()

class IntDispatcher(threading.Thread):
    sensors = {}

    def __init__(self):
        threading.Thread.__init__(self)
        self.daemon = True
        self.resolution_msec = 100
    
    def run(self):
        step = self.resolution_msec / 1000
        while True:
            next_wakeup = time.monotonic() + step
            for s in IntDispatcher.sensors.values():
                s.read()
            st = next_wakeup - time.monotonic()
            if st > 0:
                time.sleep(st)

dispatcher = IntDispatcher()
dispatcher.start()

def register_callback(channel, callback, high, pud=gpio.PUD_UP):
    if channel not in IntDispatcher.sensors.keys():
        IntDispatcher.sensors[channel] = Sensor(channel, pud)
    IntDispatcher.sensors[channel].register_callback(callback, high)

def register_callbacks(channel, callback_high, callback_low, pud=gpio.PUD_UP):
    register_callback(channel, callback_high, True, pud)
    register_callback(channel, callback_low, False)

if __name__ == "__main__":
    pin = "CSID0"

    def cb_h():
        print("high")
    def cb_l():
        print("low")

    register_callbacks(pin, cb_h, cb_l)

    while True:
        time.sleep(10)
