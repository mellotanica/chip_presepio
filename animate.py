#!/usr/bin/env python3

import threading
import time

class Updater:
    def __init__(self, update_time):
        self.ud = update_time

        self.nextud = time.time() + update_time

        self.active = True

    def update(self, now):
        if now >= self.nextud and self.active:
            self.cycle()
            self.nextud = now + self.ud

    def go(self):
        self.active = True

    def stop(self):
        self.active = False
        self.clear()

class Animator:
    class __Animator(threading.Thread):
        def __init__(self, update_delay = 0.02):
            threading.Thread.__init__(self)
            self.daemon = True

            self.update_time = update_delay

            self.unlock = threading.Event()

            self.updaters = []

            self.active = True

        def run(self):
            while True:
                if not self.active:
                    self.unlock.wait()

                now = time.time()

                for u in self.updaters:
                    u.update(now)

                time.sleep(self.update_time)

    __instance = None

    def __init__(self, update_delay=0.01):
        if Animator.__instance is None:
            Animator.__instance = Animator.__Animator(update_delay)
            Animator.__instance.start()

    def go(self):
        self.__instance.active = True
        self.__instance.unlock.set()

    def stop(self):
        self.__instance.unlock.clear()
        self.__instance.active = False

    def post_updater(self, updater):
        self.__instance.updaters.append(updater)
