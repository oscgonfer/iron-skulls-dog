from config import *
from tools import *
import pygame

BUTTONS = {
    0: "A",
    1: "B",
    2: "S",
    3: "X",
    4: "Y",
    6: "L1",
    7: "R1",
    8: "L2",
    9: "R2",
    10: "SELECT",
    11: "START",
    13: "LBALL",
    14: "RBALL"
}

AXES = {
    0: "Axis 0", # Left Axis right (-1)/left (1)
    1: "Axis 1", # Left Axis up (1)/down (-1)
    2: "Axis 2", # Right Axis right (-1)/left (1)
    3: "Axis 3"  # Right Axis up (1)/down (-1)
}

HATS = {
    0: "Hat 0"
    # First is left (-1) or right (1)
    # Second is up (1) or down (-1)
}

BALLS = {
}

JOY_SENSE = {
    "speed": 0.6,
    "roll": 0.75,
    "yaw": 0.6,
    "pitch": 0.75
}

VAL_LIMITS = {
    "speed": [0, 1],
    "roll": [0, 0.75],
    "yaw": [0, 0.6],
    "pitch": [0, 0.75]
}

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
        self.items = [Button('up'), Button('down'), Button('left'), Button('right') ]

    @property
    def pressed(self):
        return [item.pressed for item in self.items]

    @property
    def rising_edge(self):
        return [item.rising_edge for item in self.items]

    @property
    def falling_edge(self):
        return [item.falling_edge for item in self.items]

class Axis(JoystickItem):
    def __init__(self, name):
        super().__init__(name)
        self.position = 0

class JoystickHandler:
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

        self._status = {}
        self._sensitivity = JOY_SENSE

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

                if self.hats[hat].position[0] == 1:
                    self.hats[hat].items[0].press()
                elif self.hats[hat].position[0] == -1:
                    self.hats[hat].items[1].press()
                elif self.hats[hat].position[0] == 0:
                    self.hats[hat].items[0].release()
                    self.hats[hat].items[1].release()

                if self.hats[hat].position[1] == 1:
                    self.hats[hat].items[2].press()
                elif self.hats[hat].position[1] == -1:
                    self.hats[hat].items[3].press()
                elif self.hats[hat].position[1] == 0:
                    self.hats[hat].items[2].release()
                    self.hats[hat].items[3].release()

        self.update_status()
        self.update_sensitivity() # Move to akai
        return self.status

    def update_sensitivity(self):
        # We are moving the hat

        for item in self.status:
            if 'Hat' not in item:
                continue

            if any(self.status[item]):

                # Handles the hat // Changes joystick sensitivity
                if self.status[item][0]:
                    self._sensitivity["speed"] = round(min(VAL_LIMITS["speed"][1], self._sensitivity["speed"] + 0.1), 3)
                elif self.status[item][1]:
                    self._sensitivity["speed"] = round(max(VAL_LIMITS["speed"][0], self._sensitivity["speed"] - 0.1), 3)

                if self.status[item][2]:
                    self._sensitivity["roll"] = round(min(VAL_LIMITS["roll"][1], self._sensitivity["roll"] + 0.1), 3)
                    self._sensitivity["pitch"] = round(min(VAL_LIMITS["pitch"][1], self._sensitivity["pitch"] + 0.1), 3)
                    self._sensitivity["yaw"] = round(min(VAL_LIMITS["yaw"][1], self._sensitivity["yaw"] + 0.1), 3)
                elif self.status[item][3]:
                    self._sensitivity["roll"] = round(max(VAL_LIMITS["roll"][0], self._sensitivity["roll"] - 0.1), 3)
                    self._sensitivity["pitch"] = round(max(VAL_LIMITS["pitch"][0], self._sensitivity["pitch"] - 0.1), 3)
                    self._sensitivity["yaw"] = round(max(VAL_LIMITS["yaw"][0], self._sensitivity["yaw"] - 0.1), 3)

                std_out (f'New joysense speed: {self.sensitivity}', True)

    def update_status(self):
        # Representation of current joystick in a dict with names

        for axe in self.axes.values():
            self._status[axe.name] = axe.position

        for button in self.buttons.values():
            self._status[button.name] = button.rising_edge

        for hat in self.hats.values():
            self._status[hat.name] = hat.rising_edge

        return self._status

    @property
    def status(self):
        return self._status

    @property
    def sensitivity(self):
        return self._sensitivity

