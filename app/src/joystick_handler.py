from config import *
from tools import *
from command import *
import pygame

# ---------------------------------------------------
# JOYSTICK
# 8bitDo SN30Pro+ buttons and commands
BUTTONS = {
    0: {"name": "B", "command": StandUp},
    1: {"name": "A", "command": StandDown},
    2: {"name": "X", "command": BalanceStand},
    3: {"name": "Y", "command": Pose},
    4: {"name": "STAR", "command": None},
    5: {"name": "L1", "command": None},
    6: {"name": "R1", "command": None},
    7: {"name": "L2", "command": None},
    8: {"name": "R2", "command": None},
    9: {"name": "SELECT", "command": None},
    10: {"name": "START", "command": StopMove},
    11: {"name": "HEART", "command": RecoveryStand},
    12: {"name": "LBALL", "command": None},
    13: {"name": "RBALL", "command": None},
}

AXES = {
    0: {"name": "Axis 0"}, # Left Axis right (-1)/left (1)
    1: {"name": "Axis 1"}, # Left Axis up (1)/down (-1)
    2: {"name": "Axis 2"}, # Right Axis right (-1)/left (1)
    3: {"name": "Axis 3"}  # Right Axis up (1)/down (-1)
}

HATS = {
    0: {"name": "Hat 0"}
    # First is left (-1) or right (1)
    # Second is up (1) or down (-1)
}

BALLS = {
}

JOYSTICK_DEFAULTS = {
    "sensitivity": {
        "vxy": 0.6,
        "vyaw": 1.2,
        "roll": 0.75,
        "yaw": 0.6,
        "pitch": 0.75
    },
    "sensitivity_limits": {
        "speed": [0, 1],
        "roll": [0, 0.75],
        "yaw": [0, 0.6],
        "pitch": [0, 0.75],
    },
    "hardstops": {
        "axes": 0.06
    }
}
# ---------------------------------------------------

class JoystickItem:
    def __init__(self, name, index, enabled = True):
        self.name = name
        self.index = index
        self.enabled = enabled

    def disable(self):
        self.enabled = False

    def enable(self):
        self.enable = True

class Button(JoystickItem):
    def __init__(self, name, index=None, command=None):
        super().__init__(name, index)
        self.command = command
        self._pressed = False
        self._rising_edge = False
        self._falling_edge = False

    def press(self):
        if self._pressed: self._rising_edge = False
        else: self._rising_edge = True
        self._pressed = True
        self._falling_edge = False

    def release(self):
        if not self._pressed: self._falling_edge = False
        else: self._falling_edge = True
        self._pressed = False
        self._rising_edge = False
    
    @property
    def pressed(self):
        return self._pressed
    
    @property
    def rising_edge(self):
        return self._rising_edge

    @property
    def falling_edge(self):
        return self._falling_edge

class Hat(JoystickItem):
    def __init__(self, name, index):
        super().__init__(name, index)
        self.items = [
            Button('up'), 
            Button('down'), 
            Button('left'), 
            Button('right') 
        ]

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
    def __init__(self, name, index):
        super().__init__(name, index)
        self.position = 0

class JoystickHandler:
    def __init__(self, joystick):
        self.joystick = joystick

        self.buttons = {
            BUTTONS[num_item]["name"]: Button(BUTTONS[num_item]["name"], num_item, BUTTONS[num_item]["command"])
            for num_item in range(self.joystick.get_numbuttons())
        }
        self.axes = {
            AXES[num_item]["name"]: Axis(AXES[num_item]["name"], num_item)
            for num_item in range(self.joystick.get_numaxes())
        }
        self.hats = {
            HATS[num_item]["name"]: Hat(HATS[num_item]["name"], num_item)
            for num_item in range(self.joystick.get_numhats())
        }

        self._status = {}
        self._sensitivity = JOYSTICK_DEFAULTS["sensitivity"]
        self._sens_limits = JOYSTICK_DEFAULTS["sensitivity_limits"]
        self._hardstops = JOYSTICK_DEFAULTS["hardstops"]

    async def get_item_status(self):
        # This is necessary to smooth things up
        pygame.event.pump()
        # for item in range(self.joystick.get_numbuttons()):
        #     print (item, self.joystick.get_button(item))
        # print ('--')

        if self.joystick is not None:

            for axe in self.axes.values():
                value = round(self.joystick.get_axis(axe.index), 3) * -1
                # Remove noise from axes
                if value < self._hardstops["axes"] and value > -self._hardstops["axes"]: 
                    value = 0
                self.axes[axe.name].position = value

            for button in self.buttons.values():
                if self.joystick.get_button(button.index):
                    self.buttons[button.name].press()
                else:
                    self.buttons[button.name].release()

            for hat in self.hats.values():
                self.hats[hat.name].position = self.joystick.get_hat(hat.index)

                if self.hats[hat.name].position[0] == 1:
                    self.hats[hat.name].items[0].press()
                elif self.hats[hat.name].position[0] == -1:
                    self.hats[hat.name].items[1].press()
                elif self.hats[hat.name].position[0] == 0:
                    self.hats[hat.name].items[0].release()
                    self.hats[hat.name].items[1].release()

                if self.hats[hat.name].position[1] == 1:
                    self.hats[hat.name].items[2].press()
                elif self.hats[hat.name].position[1] == -1:
                    self.hats[hat.name].items[3].press()
                elif self.hats[hat.name].position[1] == 0:
                    self.hats[hat.name].items[2].release()
                    self.hats[hat.name].items[3].release()

        self.update_status()
        self.update_sensitivity()
        return self.status

    def update_sensitivity(self):
        # We are moving the hat

        for item in self.status:
            if 'Hat' not in item:
                continue

            if any(self.status[item]):

                # Handles the hat // Changes joystick sensitivity
                if self.status[item][0]:
                    self._sensitivity["vxy"] = round(min(self._sens_limits["speed"][1], 
                        self._sensitivity["vxy"] + 0.1), 3)
                    self._sensitivity["vyaw"] = round(min(self._sens_limits["speed"][1], 
                        self._sensitivity["vyaw"] + 0.1), 3)
                elif self.status[item][1]:
                    self._sensitivity["vxy"] = round(max(self._sens_limits["speed"][0], 
                        self._sensitivity["vxy"] - 0.1), 3)
                    self._sensitivity["vyaw"] = round(max(self._sens_limits["speed"][0], 
                        self._sensitivity["vyaw"] - 0.1), 3)

                if self.status[item][2]:
                    self._sensitivity["roll"] = round(min(self._sens_limits["roll"][1], 
                        self._sensitivity["roll"] + 0.1), 3)
                    self._sensitivity["pitch"] = round(min(self._sens_limits["pitch"][1], 
                        self._sensitivity["pitch"] + 0.1), 3)
                    self._sensitivity["yaw"] = round(min(self._sens_limits["yaw"][1], 
                        self._sensitivity["yaw"] + 0.1), 3)
                elif self.status[item][3]:
                    self._sensitivity["roll"] = round(max(self._sens_limits["roll"][0], 
                        self._sensitivity["roll"] - 0.1), 3)
                    self._sensitivity["pitch"] = round(max(self._sens_limits["pitch"][0], 
                        self._sensitivity["pitch"] - 0.1), 3)
                    self._sensitivity["yaw"] = round(max(self._sens_limits["yaw"][0], 
                        self._sensitivity["yaw"] - 0.1), 3)

                std_out (f'New joysense speed: {self.sensitivity}', True)

    def update_status(self):
        # Representation of current joystick in a dict with names

        for axe in self.axes.values():
            self._status[axe.name] = axe.position

        for button in self.buttons.values():
            self._status[button.name] = button.rising_edge
            # self._status[button.name] = button.pressed

        for hat in self.hats.values():
            self._status[hat.name] = hat.rising_edge

        return self._status

    @property
    def status(self):
        return self._status

    @property
    def sensitivity(self):
        return self._sensitivity

