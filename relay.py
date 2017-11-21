import CHIP_IO.GPIO as gpio

class Relay:
    def __init__(self, channel, initial_state=False):
        self.chnl = channel

        init_val = 0
        if initial_state:
            init_val = 1

        gpio.cleanup(channel)
        gpio.setup(channel, gpio.OUT, initial=init_val)

    def turn(self, high):
        val = gpio.LOW
        if high:
            val = gpio.HIGH
        gpio.output(self.chnl, val)

    def a(self):
        self.turn(False)

    def nb(self):
        self.turn(True)

