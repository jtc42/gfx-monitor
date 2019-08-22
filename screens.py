from datetime import datetime

from PIL import Image, ImageFont, ImageDraw
from gfxhat import touch, lcd, backlight, fonts

from utilities.interfaces import IfaceScanner
from utilities.stats import StatScanner

width, height = lcd.dimensions()

class Screen:
    max_lines = 6

    def __init__(self):
        self._lines = []

        self.font = ImageFont.truetype(fonts.BitbuntuFull, 10)
        self.image = Image.new('P', (width, height))
        self.image_draw = ImageDraw.Draw(self.image)

        self._line_offset = 0

    @property
    def line_offset(self):
        return self._line_offset
    
    @line_offset.setter
    def line_offset(self, n):
        max_offset = len(self._lines) - Screen.max_lines + 2
        if len(self._lines) > Screen.max_lines:
            if n < 0:
                self._line_offset = max_offset
            elif n <= max_offset:
                self._line_offset = n
            else:
                self._line_offset = 0
        else:
            self._line_offset = 0

    def set_line(self, n, text, align="left"):
        while len(self._lines) < n+1:
            self._lines.append(["", ""])

        if align not in ["left", "right"]:
            print("Property 'align' must be either left or right")
            return
        
        self._lines[n][1 if align=="right" else 0] = str(text)

    def update(self):
        pass

    def draw_decoration(self):
        pass

    def draw_lines(self):
        for index, line in enumerate(self._lines[self.line_offset:self.line_offset+Screen.max_lines]):
            # Left
            x = 0
            y = (index * 11)
            self.image_draw.text((x, y), line[0], fill=1, font=self.font, align="left")

            # Right
            x = width
            y = (index * 11)
            w, h = self.image_draw.textsize(line[1])
            self.image_draw.text((x-w, y), line[1], fill=1, font=self.font, align="right")

    def draw(self):
        self.update()
        self.image.paste(0, (0, 0, width, height))
        self.draw_lines()
        self.draw_decoration()

    def show(self):
        self.draw()
        for x in range(width):
            for y in range(height):
                pixel = self.image.getpixel((x, y))
                lcd.set_pixel(x, y, pixel)
        lcd.show()

class HomeScreen(Screen):

    def __init__(self):
        Screen.__init__(self)
        self.network_screen = None
        self.stat_screen = None
    
    def bind(self, screen_object):
        if isinstance(screen_object, NetworkScreen):
            self.network_screen = screen_object
        if isinstance(screen_object, StatScreen):
            self.stat_screen = screen_object

    def update(self):
        now = datetime.now() # current date and time
        date = now.strftime("%m/%d/%Y")
        time = now.strftime("%H:%M")

        self.set_line(0, date, align="left")
        self.set_line(0, time, align="right")

        if self.network_screen:
            self.network_screen.update()

            # Use the first 2 lines of networks
            for index, line in enumerate(self.network_screen.lines[:2]):
                # Add network info to line 2, 3
                self.set_line(2 + index, line, align="left")

        if self.stat_screen:
            self.stat_screen.update()

            # Use the first line of stats
            self.set_line(5, self.stat_screen._lines[0][0], align="left")
            self.set_line(5, self.stat_screen._lines[0][1], align="right")

class HelloScreen(Screen):
    def __init__(self):
        Screen.__init__(self)
        self.set_line(0, "Hello", align="left")
        self.set_line(1, "World", align="left")

class NetworkScreen(Screen):
    def __init__(self, interfaces, refresh_ticks=30):
        Screen.__init__(self)
        self.scanner = IfaceScanner(interfaces)  # List of interfaces to scan
        self.refresh_ticks = refresh_ticks  # Number of frame ticks per network refresh
        self.tick = 0  # Current frame tick

        self.lines = []

    def update(self):
        # Refresh all interface strings every some ticks
        if self.tick == 0:
            ifaces = self.scanner.simple
            self.lines = ["{0: <5}:{1}".format(key, val) for key, val in ifaces.items()]
        
            for index, line in enumerate(self.lines):
                self.set_line(index, line, align="left")

        # Cycle through ticks
        if self.tick < self.refresh_ticks:
            self.tick += 1
        else:
            self.tick = 0


class StatScreen(Screen):
    def __init__(self, refresh_ticks=30):
        Screen.__init__(self)
        self.scanner = StatScanner() 
        self.refresh_ticks = refresh_ticks  # Number of frame ticks per network refresh
        self.tick = 0  # Current frame tick

        self.lines = []

    def update(self):
        # Refresh all interface strings every some ticks
        if self.tick == 0:
            stats = self.scanner.simple
            
            # CPU
            self.set_line(0, "CPU  :{}".format(stats['cpu_temp']))
            self.set_line(0, stats['cpu_load'], align="right")
            self.set_line(1, "     {}".format(stats['cpu_freq']))
        
            # MEM
            self.set_line(2, "MEM  :{}".format(stats['mem_info']), align="left")
            self.set_line(2, stats['mem_perc'], align="right")

            # DSK
            self.set_line(3, "DSK  :{}".format(stats['dsk_info']), align="left")
            self.set_line(3, stats['dsk_perc'], align="right")

        # Cycle through ticks
        if self.tick < self.refresh_ticks:
            self.tick += 1
        else:
            self.tick = 0
            