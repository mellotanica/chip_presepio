#!/usr/bin/env python3

import CHIP_IO.GPIO as gpio
import sensor
import threading
import time

class Cooldown(threading.Thread):
    def __init__(self, pir):
        threading.Thread.__init__(self)
        self.daemon = True
        
        self.pir = pir
        
        self.unblock = threading.Event()
        self.unblock.clear()

        self.wakeuptime = time.time()
        self.going = False

        self.start()

    def run(self):
        while True:
            self.going = False

            self.unblock.wait()
            self.going = True
            self.unblock.clear()

            self.pir.high()

            while self.wakeuptime > time.time():
                time.sleep(self.wakeuptime - time.time())

            self.pir.low()


    def go(self, cooldown):
        self.wakeuptime = time.time() + cooldown
        if not self.going:
            self.unblock.set()


class Pir(sensor.Sensor):
    def __init__(self, pir_ctl, pud=gpio.PUD_UP):
        sensor.Sensor.__init__(self, pir_ctl, pud)

        self.cooldown_time = 12
        self.cooldown = Cooldown(self)


    def perform(self, high=False):
        if self.enabled and high:
                self.cooldown.go(self.cooldown_time)

    def high(self):
        sensor.Sensor.perform(self, True)

    def low(self):
        sensor.Sensor.perform(self, False)


def get_pir(channel, pud=gpio.PUD_UP):
    if channel not in sensor.IntDispatcher.sensors.keys():
        sensor.IntDispatcher.sensors[channel] = Pir(channel, pud)
    return sensor.IntDispatcher.sensors[channel]

