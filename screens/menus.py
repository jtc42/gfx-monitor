from .screens import Screen, width, height

from gfxhat import backlight

class MenuOption:
    def __init__(self, name, action, options=()):
        self.name = name
        self.action = action
        self.options = options

    def trigger(self):
        self.action(*self.options)

class Menu(Screen):
    def __init__(self, menu_options=[]):
        Screen.__init__(self)

        self.menu_options = menu_options
        self.trigger_action = False

    @property
    def current_line(self):
        """
        Line offset for scrolling.
        For menus, this corresponds to the selected menu item
        """
        return self._current_line
    
    @current_line.setter
    def current_line(self, n):
        self._current_line = n % len(self.menu_options)

    def draw_decoration(self):
        global height

        w, h = self.font.getsize('>')
        self.image_draw.text((0, (height - h) / 2), '>', 1, self.font)
    
    def trigger(self):
        """
        Action to perform when the trigger button is pressed.
        Triggers the active menu item function by default.
        """
        self.trigger_action = True

    def update(self):
        # Trigger the menu items action if it's been pressed since the last frame
        if self.trigger_action:
            self.menu_options[self.current_line].trigger()
            self.trigger_action = False

    def draw_content(self):
        """
        Draw the main content.
        By default, renders the menu items with formatting
        """
        offset_top = 0

        for index, menu_item in enumerate(self.menu_options):
            if index == self.current_line:
                break
            offset_top += 11

        for index, menu_item in enumerate(self.menu_options):
            x = 10
            y = (index * 11) + (height / 2) - 4 - offset_top
            option = menu_item
            if index == self.current_line:
                self.image_draw.rectangle(((x-2, y-1), (width, y+10)), 1)
            self.image_draw.text(
                (x, y), 
                option.name, 
                0 if index == self.current_line else 1, 
                self.font
            )


class BacklightMenu(Menu):
    def __init__(self):
        Menu.__init__(self)

        self.brightness = 0.4

        self.menu_options = [
            MenuOption('Set BL Default', self.set_backlight, (10, 20, 225)),
            MenuOption('Set BL Blue', self.set_backlight, (0, 0, 255)),
            MenuOption('Set BL Red', self.set_backlight, (255, 0, 0)),
            MenuOption('Set BL Green', self.set_backlight, (0, 255, 0)),
            MenuOption('Set BL Purple', self.set_backlight, (255, 0, 255)),
            MenuOption('Set BL White', self.set_backlight, (255, 255, 255)),
            MenuOption('BL off', self.set_backlight, (0, 0, 0))
        ]

        # Immediately set the backlight
        self.menu_options[self.current_line].trigger()
    
    def set_backlight(self, r, g, b):
        r, g, b = (int(c*self.brightness) for c in (r, g, b))
        backlight.set_all(r, g, b)
        backlight.show()

    def wake_handler(self):
        self.menu_options[self.current_line].trigger()

    def timeout_handler(self):
        self.timed_out = True
        self.set_backlight(0, 0, 0)
