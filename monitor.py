#!/usr/bin/python3

import time
import sys
import atexit

from screens.screens import HomeScreen, HelloScreen, NetworkScreen, StatScreen
from screens.menus import BacklightMenu

from gfxhat import touch, lcd, backlight, fonts

class ScreenCollection:
    # TODO: Screens can send out a "bad thing happened" signal, causing the Collection to turn the backlight red

    def __init__(self, timeout=30):
        self.homescreen = HomeScreen()
        self._screens = []  # Array of additionally added screens
        self._active = 0

        self.timeout = timeout  # Timeout time in seconds
        self.timed_out = False  # Are we currently timed out?
        self.last_interaction_time = time.time()  # Time of last user interaction

        for x in range(6):
            touch.set_led(x, 0)
            touch.on(x, self.touch_handler)

    @property
    def screens(self):
        return [self.homescreen] + self._screens
    
    @screens.setter
    def screens(self, val):
        self._screens = val

    @property
    def active(self):
        return self._active
    
    @active.setter
    def active(self, n):
        self._active = n % len(self.screens)

    def update(self):
        """
        Logic not related to drawing screen content
        """
        # Handle timeout
        now = time.time()
        time_since_interaction = now - self.last_interaction_time
        if (time_since_interaction >= self.timeout) and not self.timed_out:
            self.timed_out = True
            for screen_i in self.screens:
                screen_i.timeout_handler()
        elif (time_since_interaction <= self.timeout) and self.timed_out:
            self.timed_out = False
            for screen_i in self.screens:
                screen_i.wake_handler()

    def draw(self):
        self.update()
        self.screens[self.active].show()

    def add(self, screen):
        self.homescreen.bind(screen)  # Bind any potential added functionality to the homescreen
        self._screens.append(screen)

    def touch_handler(self, ch, event):
        # Update timeout
        self.last_interaction_time = time.time()

        # Event logic
        if event != 'press':
            return
        if ch == 5:
            self.active -= 1
        if ch == 4:
            self.active = 0
        if ch == 3:
            self.active += 1
    
        if ch == 2:
            self.screens[self.active].trigger()
        if ch == 1:
            self.screens[self.active].current_line -= 1
        if ch == 0:
            self.screens[self.active].current_line += 1

def cleanup():
    backlight.set_all(0, 0, 0)
    backlight.show()
    lcd.clear()
    lcd.show()

atexit.register(cleanup)

lcd.contrast(40)
lcd.rotation(180)

screen_collection = ScreenCollection()

# Create a stat screen
screen_collection.add(StatScreen())

# Create a network screen
screen_collection.add(NetworkScreen(
    ["eth0", "wg0", "wlan0", "test0", "test1", "test2", "test3", "test4", "test5", "test6"], 
    refresh_ticks=30
))

# Create a settings screen
screen_collection.add(BacklightMenu())

# Create a hello screen
screen_collection.add(HelloScreen())

try:
    while True:
        screen_collection.draw()
        time.sleep(1.0 / 15)

except KeyboardInterrupt:
    cleanup()

cleanup()