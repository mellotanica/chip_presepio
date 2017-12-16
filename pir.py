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

    def run(self):
        print("starting cooldown")
        while True:
            self.going = False
            if not self.going:
                print("cooldown waiting for start")
                self.unblock.wait()
                self.unblock.clear()

            print("cooldown starting")
            self.pir.high()

            while self.wakeuptime > time.time():
                time.sleep(self.wakeuptime - time.time())

            self.pir.low()


    def go(self, cooldown):
        self.wakeuptime = time.time() + cooldown
        if not self.going:
            self.going = True
            self.unblock.set()


class Pir(sensor.Sensor):
    def __init__(self, pir_ctl, pud=gpio.PUD_UP):
        sensor.Sensor.__init__(self, pir_ctl, pud)

        self.cooldown_time = 12
        self.cooldown = Cooldown(self)
        self.cooldown.start()

    def perform(self, high=False):
        print("pir perform {}".format(high))
        if self.enabled and high:
                self.cooldown.go(self.cooldown_time)

    def high(self):
        sensor.Sensor.perform(self, True)

    def low(self):
        sensor.Sensor.perform(self, False)


def get_pir(channel, pud=gpio.PUD_UP):
    disp = sensor.IntDispatcher
    if channel not in disp.sensors.keys():
        disp.sensors[channel] = Pir(channel, pud)
    return disp.sensors[channel]

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

    p = get_pir(pin, pud)
    p.register_callbacks(cb_h, cb_l)

    while True:
        time.sleep(100)
