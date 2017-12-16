#!/usr/bin/env  python3

import CHIP_IO.GPIO as gpio
import CHIP_IO.Utilities
from animate import Updater, Animator
import threading
import time

class Sensor:
    class Cooldown(threading.Thread):
        def __init__(self, sensor, cooldown_time):
            threading.Thread.__init__(self)
            self.daemon = True
            
            self.sensor = sensor
            
            self.unblock = threading.Event()
            self.unblock.clear()

            self.wakeuptime = time.time()
            self.cooldowntime = cooldown_time
            self.going = False

        def run(self):
            while True:
                self.going = False
                if not self.going:
                    self.unblock.wait()
                    self.unblock.clear()

                self.sensor.high()

                while self.wakeuptime > time.time():
                    time.sleep(self.wakeuptime - time.time())

                self.sensor.low()

        def go(self):
            self.wakeuptime = time.time() + self.cooldowntime
            if not self.going:
                self.going = True
                self.unblock.set()

    def __init__(self, sensor_ctl, pud=gpio.PUD_UP, cooldown=None):
        self.callbacks_high = []
        self.callbacks_low = []
        self.sensor = sensor_ctl
       
        gpio.cleanup(sensor_ctl)
        gpio.setup(sensor_ctl, gpio.IN, pull_up_down=pud)

        self.state = None
        self.enabled = True

        try:
            tcool = float(cooldown)
        except:
            tcool = -1

        if tcool > 0:
            self.cooldown = Sensor.Cooldown(self, tcool)
            self.cooldown.start()
        else:
            self.cooldown = None

    def register_callback(self, callback, high):
        if not callable(callback):
            print("WARNING: callback must be callable, not registering {}".format(callback))
            return
        if high:
            self.callbacks_high.append(callback)
        else:
            self.callbacks_low.append(callback)

    def register_callbacks(self, callback_high, callback_low):
        self.register_callback(callback_high, True)
        self.register_callback(callback_low, False)

    def perform(self, high):
        if self.enabled:
            if self.cooldown is None:
                if high:
                    self.high()
                else:
                    self.low()
            elif high:
                self.cooldown.go()

    def high(self):
        for cb in self.callbacks_high:
            cb()

    def low(self):
        for cb in self.callbacks_low:
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

class IntDispatcher:
    sensors = {}
    __instance = None
    
    class __IntDispatcher(Updater):

        def __init__(self):
            Updater.__init__(self, 0.5)

        def cycle(self):
            for s in IntDispatcher.sensors.values():
                s.read()

        def clear(self):
            return

    def __init__(self):
        if IntDispatcher.__instance is None:
            IntDispatcher.__instance = IntDispatcher.__IntDispatcher()
            animator = Animator()
            animator.post_updater(IntDispatcher.__instance)

def get_sensor(channel, pud=gpio.PUD_UP, cooldown=None):
    disp = IntDispatcher()
    if channel not in disp.sensors.keys():
        disp.sensors[channel] = Sensor(channel, pud, cooldown)
    return disp.sensors[channel]

def register_callback(channel, callback, high, pud=gpio.PUD_UP):
    get_sensor(channel, pud).register_callback(callback, high)

def register_callbacks(channel, callback_high, callback_low, pud=gpio.PUD_UP):
    get_sensor(channel, pud).register_callbacks(callback_high, callback_low)

def replay_action(channel):
    get_sensor(channel).replay_action()

def replay_actions():
    for s in disp.sensors.values():
        s.replay_action()

if __name__ == "__main__":
    import sys
    import time

    if len(sys.argv) > 1:
        pin = sys.argv[1]
    else:
        pin = "CSID1"

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

    sensor = get_sensor(pin, pud, 15)
    sensor.register_callbacks(cb_h, cb_l)

    while True:
        time.sleep(100)
