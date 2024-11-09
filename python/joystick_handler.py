from config import *
from tools import *

import pygame

class JoystickItem:
    def __init__(self, name, enabled = True):
        self.name = name
        self.enabled = enabled

    def disable(self):
        self.enabled = False

    def enable(self):
        self.enable = True

class Button(JoystickItem):
    def __init__(self, name):
        super().__init__(name)
        self.pressed = False
        self.rising_edge = False
        self.falling_edge = False

    def press(self):
        if self.pressed: self.rising_edge = False
        else: self.rising_edge = True
        self.pressed = True
        self.falling_edge = False

    def release(self):
        if not self.pressed: self.falling_edge = False
        else: self.falling_edge = True
        self.pressed = False
        self.rising_edge = False

class Hat(JoystickItem):
    def __init__(self, name):
        super().__init__(name)
        self.position = (0, 0)

class Axis(JoystickItem):
    def __init__(self, name):
        super().__init__(name)
        self.position = 0

class JoystickState:
    def __init__(self, joystick):
        self.joystick = joystick

        self.types = {
            'buttons': [BUTTONS, Button],
            'axes': [AXES, Axis],
            'hats': [HATS, Hat]
        }

        # Get numbers at the beginning to avoid overhead
        self.numbers = {
            'axes': joystick.get_numaxes(),
            'buttons': joystick.get_numbuttons(),
            'hats': joystick.get_numhats()
        }

        self.buttons = self.init_items('buttons')
        self.axes = self.init_items('axes')
        self.hats = self.init_items('hats')

    def init_items(self, item_type):
        items = {}

        for num in range(self.numbers[item_type]):
            item_dict = self.types[item_type][0]
            item_class = self.types[item_type][1]
            if num not in item_dict: continue
            items[num] = item_class(item_dict[num])

        return items

    async def get_item_values(self):
        # This is necessary to smooth things up
        pygame.event.pump()

        if self.joystick is not None:

            for axe in self.axes.keys():
                self.axes[axe].position = round(self.joystick.get_axis(axe), 1) * -1

            for button in self.buttons.keys():
                if self.joystick.get_button(button):
                    self.buttons[button].press()
                else:
                    self.buttons[button].release()

            for hat in self.hats.keys():
                self.hats[hat].position = self.joystick.get_hat(hat)

        return self.status()

    def status(self):
        # Representation of current joystick in a dict with names
        d = {}

        for axe in self.axes.values():
            d[axe.name] = axe.position

        for button in self.buttons.values():
            d[button.name] = button.rising_edge

        for hat in self.hats.values():
            d[hat.name] = hat.position

        return d

