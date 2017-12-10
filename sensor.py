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

        self.state = None
        self.enabled = True

    def register_callback(self, callback, high):
        if not callable(callback):
            print("WARNING: callback must be callable, not registering {}".format(callback))
            return
        if high:
            self.callbacks_high.append(callback)
        else:
            self.callbacks_low.append(callback)

    def register_callbacks(self, callbacks_high, callbacks_low):
        self.register_callback(callbacks_high, True)
        self.register_callback(callbacks_low, True)

    def perform(self, high):
        if self.enabled:
            cblist = None
            if high:
                cblist = self.callbacks_high
            else:
                cblist = self.callbacks_low
            for cb in cblist:
                cb()

    def read(self):
        val = gpio.input(self.sensor)
        if val != self.state:
            self.state = val
            self.perform(val)
        return val

    def enable(self):
        self.enabled = True

    def disable(self):
        self.enabled = False

    def replay_action(self):
        self.perform(self.state)

class IntDispatcher(threading.Thread):
    sensors = {}

    def __init__(self):
        threading.Thread.__init__(self)
        self.daemon = True
        self.resolution_msec = 500
    
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

def get_sensor(channel, pud=gpio.PUD_UP):
    if channel not in IntDispatcher.sensors.keys():
        IntDispatcher.sensors[channel] = Sensor(channel, pud)
    return IntDispatcher.sensors[channel]

def register_callback(channel, callback, high, pud=gpio.PUD_UP):
    get_sensor(channel, pud).register_callback(callback, high)

def register_callbacks(channel, callback_high, callback_low, pud=gpio.PUD_UP):
    get_sensor(channel, pud).register_callbacks(callback_high, callback_low)

def replay_action(channel):
    get_sensor(channel).replay_action()

def replay_actions():
    for s in IntDispatcher.sensors.values():
        s.replay_action()

if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        pin = sys.argv[1]
    else:
        pin = "CSID0"

    pud = gpio.PUD_UP
    if len(sys.argv) > 2:
        if sys.argv[2].lower() == "up":
            pud = gpio.PUD_UP
        elif sys.argv[2].lower() == "down":
            pud = gpio.PUD_DOWN

    def cb_h():
        print("high")
    def cb_l():
        print("low")

    register_callbacks(pin, cb_h, cb_l, pud)

    while True:
        time.sleep(10)
