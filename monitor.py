#!/usr/bin/python3

import time
import sys
import atexit

from screens import HomeScreen, HelloScreen, NetworkScreen, StatScreen

from gfxhat import touch, lcd, backlight, fonts

class ScreenCollection:
    BACKLIGHT_COLOURS = [
        (0, 0, 100),
        (100, 0, 0),
        (0, 100, 0),
        (0, 50, 50),
        (75, 25, 0),
        (50, 0, 50),
        (0, 0, 0)
    ]

    # TODO: Screens can send out a "bad thing happened" signal, causing the Collection to turn the backlight red

    def __init__(self):
        self.homescreen = HomeScreen()
        self._screens = []  # Array of additionally added screens
        self._active = 0

        for x in range(6):
            touch.set_led(x, 0)
            touch.on(x, self.touch_handler)

        self.backlight_colour_index = 0

        backlight.show()

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

    def draw(self):
        self.set_backlight(*ScreenCollection.BACKLIGHT_COLOURS[self.backlight_colour_index])

        self.screens[self.active].show()

    def add(self, screen):
        self.homescreen.bind(screen)  # Bind any potential added functionality to the homescreen
        self._screens.append(screen)

    def touch_handler(self, ch, event):
        if event != 'press':
            return
        if ch == 5:
            self.active -= 1
        if ch == 4:
            if self.active != 0:
                self.active = 0
            else:
                self.backlight_colour_index += 1
                self.backlight_colour_index = self.backlight_colour_index % len(ScreenCollection.BACKLIGHT_COLOURS)
        if ch == 3:
            self.active += 1
    
        if ch == 2:
            self.screens[self.active].line_offset = 0
        if ch == 1:
            self.screens[self.active].line_offset -= 1
        if ch == 0:
            self.screens[self.active].line_offset += 1

    def set_backlight(self, r, g, b):
        backlight.set_all(r, g, b)
        backlight.show()

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

# Create a hello screen
screen_collection.add(HelloScreen())

try:
    while True:
        screen_collection.draw()
        time.sleep(1.0 / 15)

except KeyboardInterrupt:
    cleanup()

