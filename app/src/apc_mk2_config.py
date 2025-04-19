from enum import Enum
from config import *
from command import *
from rtmidi.midiconstants import NOTE_OFF, NOTE_ON, CONTROLLER_CHANGE
from apc_mk2_map import pad_commands
from capture import CaptureCommand, CaptureAction
from os import listdir
from os.path import isfile, join, dirname, realpath, splitext

APC_PORT_NAME = 'APC mini mk2:APC mini mk2 APC mini mk2 Contr 20:0'
APC_MK2_NUM_PADS = 64
APC_MK2_FADER_LIMITS = [0, 127]

class APCMK2ButtonName(Enum):
    VOLUME = 0x64
    PAN = 0x65
    SEND = 0x66
    DEVICE = 0x67
    UP = 0x68
    DOWN = 0x69
    LEFT = 0x6A
    RIGHT = 0x6B
    CLIP_STOP = 0x70
    SOLO = 0x71
    MUTE = 0x72
    REC_ARM = 0x73
    SELECT = 0x74
    DRUM = 0x75
    NOTE = 0x76
    STOP_ALL = 0x77
    SHIFT = 0x7A

class APCMK2FaderName(Enum):
    FADER_1 = 0x30
    FADER_2 = 0x31
    FADER_3 = 0x32
    FADER_4 = 0x33
    FADER_5 = 0x34
    FADER_6 = 0x35
    FADER_7 = 0x36
    FADER_8 = 0x37
    FADER_9 = 0x38

class APCMK2ButtonEffect(Enum):
    OFF = 0x00
    ON = 0x01
    BLINK = 0x02

class APCMK2PadEffect(Enum):
    ON_10 = 0x90
    ON_25 = 0x91
    ON_50 = 0x92
    ON_65 = 0x93
    ON_75 = 0x94
    ON_90 = 0x95
    ON_100 = 0x96
    PULSE_1_16 = 0x97
    PULSE_1_8 = 0x98
    PULSE_1_4 = 0x99
    PULSE_1_2 = 0x9A
    BLINK_1_24 = 0x9B
    BLINK_1_16 = 0x9C
    BLINK_1_8 = 0x9D
    BLINK_1_4 = 0x9E
    BLINK_1_2 = 0x9F

class APCMK2PadColor(Enum):
    BLACK = 0        #000000
    WHITE =  3       #FFFFFF
    RED =  5         #FF0000
    ORANGE =  9      #FF5400
    YELLOW = 13      #FFFF00
    GREEN = 17       #00FF00
    AQUA_GREEN = 29  #00FF55
    SKY_BLUE = 36    #4CC3FF
    BLUE = 45        #0000FF
    PURPLE = 53      #FF00FF
    LAVENDER = 57    #FF0054

class APCMK2Mode(Enum):
    # Normal Mode
    # Trigger: Default. Record key when in recording
    # Trigger commands or recordings, use faders, or enter record mode
    normal = 0 
    # Record mode
    # Trigger: Record key (REC ARM)
    # Only can select where to put a recording, if selects on one that exists, overwrites. 
    # It starts recording when selects the button
    record = 2 
    # Recording mode
    # Trigger: Selected recording destination key
    # Waits until record key is pressed and goes back to normal.
    # Commands or faders are also allowed
    recording = 3
    # Preview mode
    # Trigger: SHIFT (stays pressed)
    # Shows what they pad contains
    preview = 4

class APCMK2ActionType(Enum):
    null = 0
    command = 1 # Dog command
    dog_mode_toggle = 2 # Dog command with toggle group
    apc_mode_change = 4 # Change mode
    apc_mode_toggle = 5 # Toggle mode on NOTE_ON / NOTE_OFF
    subprocess = 6 # External subprocess (for instance, play_capture.py)
    capture = 7
    unassigned = 8 # Unassigned


class APCMK2ActionStatus(Enum):
    idle = 0
    running = 1
    disabled = 2

class APCMK2Action():
    def __init__(self, command, payload, atype, on = NOTE_ON):
        self.command = command
        self.payload = payload # message payload, command payload
        self.type: APCMK2ActionType = atype
        self.status: APCMK2ActionStatus = APCMK2ActionStatus.idle
        self.on = on

class APCMK2Input():
    def __init__(self, channel: int, name: str, action: APCMK2Action = None):
        self.channel = channel
        self.name = name
        self.input_state: int = 0
        self.trigger: bool = False
        self.action = action

class APCMK2Pad(APCMK2Input):
    def __init__(self, channel, name, action: APCMK2Action = None, map: {} = None):
        self.map = map
        super().__init__(channel, name, action)
        self.release()
    
    def press(self):
        self.action.status = APCMK2ActionStatus.running
        self.color = self.map["running"]["color"]
        self.effect = self.map["running"]["effect"]

    def release(self):
        self.action.status = APCMK2ActionStatus.idle
        self.color = self.map["idle"]["color"]
        self.effect = self.map["idle"]["effect"]

    def to_dict(self):
        return {
            'effect': self.effect.name,
            'color': self.color.name,
            'channel': self.channel,
            'name': self.name,
            'action': self.action,
            'input_state': self.input_state,
            'trigger': self.trigger
        }
    
class APCMK2Button(APCMK2Input):
    def __init__(self, channel, name, action: APCMK2Action = None, map: {} = None):
        self.map = map
        
        super().__init__(channel, name, action)
        self.release()
    
    def press(self):
        self.action.status = APCMK2ActionStatus.running
        self.effect = self.map["running"]["effect"]

    def release(self):
        self.action.status = APCMK2ActionStatus.idle
        self.effect = self.map["idle"]["effect"]

    def to_dict(self):
        return {
            'effect': self.effect.name,
            'channel': self.channel,
            'name': self.name,
            'action': self.action,
            'input_state': self.input_state,
            'trigger': self.trigger
        }

class APCMK2Fader(APCMK2Input):
    def __init__(self, channel, name, action: APCMK2Action = None):
        super().__init__(channel, name, action)

    def to_dict(self):
        return {
            'channel': self.channel,
            'name': self.name,
            'action': self.action,
            'input_state': self.input_state,
            'trigger': self.trigger
        }

def get_cap_files():
    file_path = dirname(realpath(__file__))
    capture_path = join(file_path, CAPTURE_PATH)

    cap_files = [int(splitext(f)[0]) for f in listdir(capture_path) if isfile(join(capture_path, f)) and splitext(f)[1] == '.cap' and splitext(f)[0].isdigit()]

    return cap_files

COLOR_EFFECT_MAP = {
    "pads": {
        "normal": {
            "null": {
                "idle": {"color": APCMK2PadColor.LAVENDER, "effect": APCMK2PadEffect.ON_10},
                "running": {"color": APCMK2PadColor.LAVENDER, "effect": APCMK2PadEffect.ON_100},
                "disabled": {"color": APCMK2PadColor.RED, "effect": APCMK2PadEffect.ON_10}
            },
            "subprocess": {
                "idle": {"color": APCMK2PadColor.GREEN, "effect": APCMK2PadEffect.ON_50},
                "running": {"color": APCMK2PadColor.AQUA_GREEN, "effect": APCMK2PadEffect.PULSE_1_2},
                "disabled": {"color": APCMK2PadColor.RED, "effect": APCMK2PadEffect.ON_10}
            },
            "unassigned": {
                "idle": {"color": APCMK2PadColor.RED, "effect": APCMK2PadEffect.ON_10},
                "running": {"color": APCMK2PadColor.RED, "effect": APCMK2PadEffect.BLINK_1_2},
                "disabled": {"color": APCMK2PadColor.RED, "effect": APCMK2PadEffect.ON_10}
            },
            "command": {
                "idle": {"color": APCMK2PadColor.YELLOW, "effect": APCMK2PadEffect.ON_50},
                "running": {"color": APCMK2PadColor.BLUE, "effect": APCMK2PadEffect.ON_100},
                "disabled": {"color": APCMK2PadColor.RED, "effect": APCMK2PadEffect.ON_10}
            },
        },
        "record": {
            "null": {
                "idle": {"color": APCMK2PadColor.BLACK, "effect": APCMK2PadEffect.PULSE_1_2},
                "running": {"color": APCMK2PadColor.BLACK, "effect": APCMK2PadEffect.ON_100},
                "disabled": {"color": APCMK2PadColor.RED, "effect": APCMK2PadEffect.ON_10}
            },
            "subprocess": {
                "idle": {"color": APCMK2PadColor.SKY_BLUE, "effect": APCMK2PadEffect.ON_50},
                "running": {"color": APCMK2PadColor.BLUE, "effect": APCMK2PadEffect.ON_100},
                "disabled": {"color": APCMK2PadColor.RED, "effect": APCMK2PadEffect.ON_10}
            },
            "capture": {
                "idle": {"color": APCMK2PadColor.RED, "effect": APCMK2PadEffect.PULSE_1_2},
                "running": {"color": APCMK2PadColor.RED, "effect": APCMK2PadEffect.BLINK_1_16},
                "disabled": {"color": APCMK2PadColor.RED, "effect": APCMK2PadEffect.ON_10}
            },
            "command": {
                "idle": {"color": APCMK2PadColor.YELLOW, "effect": APCMK2PadEffect.ON_50},
                "running": {"color": APCMK2PadColor.BLUE, "effect": APCMK2PadEffect.ON_100},
                "disabled": {"color": APCMK2PadColor.RED, "effect": APCMK2PadEffect.ON_10}
            },
        },
        "recording": {
            "null": {
                "idle": {"color": APCMK2PadColor.BLACK, "effect": APCMK2PadEffect.PULSE_1_2},
                "running": {"color": APCMK2PadColor.BLACK, "effect": APCMK2PadEffect.ON_100},
                "disabled": {"color": APCMK2PadColor.RED, "effect": APCMK2PadEffect.ON_10}
            },
            "subprocess": {
                "idle": {"color": APCMK2PadColor.SKY_BLUE, "effect": APCMK2PadEffect.ON_50},
                "running": {"color": APCMK2PadColor.BLUE, "effect": APCMK2PadEffect.ON_100},
                "disabled": {"color": APCMK2PadColor.RED, "effect": APCMK2PadEffect.ON_10}
            },
            "capture": {
                "idle": {"color": APCMK2PadColor.RED, "effect": APCMK2PadEffect.PULSE_1_2},
                "running": {"color": APCMK2PadColor.RED, "effect": APCMK2PadEffect.BLINK_1_16},
                "disabled": {"color": APCMK2PadColor.RED, "effect": APCMK2PadEffect.ON_10}
            },
            "unassigned": {
                "idle": {"color": APCMK2PadColor.RED, "effect": APCMK2PadEffect.ON_10},
                "running": {"color": APCMK2PadColor.RED, "effect": APCMK2PadEffect.ON_50},
                "disabled": {"color": APCMK2PadColor.RED, "effect": APCMK2PadEffect.ON_10}
            },
            "command": {
                "idle": {"color": APCMK2PadColor.YELLOW, "effect": APCMK2PadEffect.ON_50},
                "running": {"color": APCMK2PadColor.BLUE, "effect": APCMK2PadEffect.ON_100},
                "disabled": {"color": APCMK2PadColor.RED, "effect": APCMK2PadEffect.ON_10}
            },
        },
        "preview": {
            "null": {
                "idle": {"color": APCMK2PadColor.BLACK, "effect": APCMK2PadEffect.ON_100},
                "running": {"color": APCMK2PadColor.BLACK, "effect": APCMK2PadEffect.ON_100},
                "disabled": {"color": APCMK2PadColor.RED, "effect": APCMK2PadEffect.ON_10}
            },
            "subprocess": {
                "idle": {"color": APCMK2PadColor.ORANGE, "effect": APCMK2PadEffect.PULSE_1_2},
                "running": {"color": APCMK2PadColor.AQUA_GREEN, "effect": APCMK2PadEffect.ON_100},
                "disabled": {"color": APCMK2PadColor.RED, "effect": APCMK2PadEffect.ON_10}
            },
            "unassigned": {
                "idle": {"color": APCMK2PadColor.RED, "effect": APCMK2PadEffect.ON_10},
                "running": {"color": APCMK2PadColor.RED, "effect": APCMK2PadEffect.BLINK_1_16},
                "disabled": {"color": APCMK2PadColor.RED, "effect": APCMK2PadEffect.ON_10}
            },
            "command": {
                "idle": {"color": APCMK2PadColor.YELLOW, "effect": APCMK2PadEffect.PULSE_1_2},
                "running": {"color": APCMK2PadColor.BLUE, "effect": APCMK2PadEffect.PULSE_1_2},
                "disabled": {"color": APCMK2PadColor.RED, "effect": APCMK2PadEffect.ON_10}
            }
        }
    }, 
    "buttons": {
        "normal": {
            "null": {
                "idle": {"effect": APCMK2ButtonEffect.OFF},
                "running": {"effect": APCMK2ButtonEffect.ON},
            },
            "subprocess": {
                "idle": {"effect": APCMK2ButtonEffect.OFF},
                "running": {"effect": APCMK2ButtonEffect.ON},
            },
            "command": {
                "idle": {"effect": APCMK2ButtonEffect.OFF},
                "running": {"effect": APCMK2ButtonEffect.ON},
            },
            "dog_mode_toggle": {
                "idle": {"effect": APCMK2ButtonEffect.OFF},
                "running": {"effect": APCMK2ButtonEffect.ON},
            },
            "apc_mode_change": {
                "idle": {"effect": APCMK2ButtonEffect.OFF},
                "running": {"effect": APCMK2ButtonEffect.ON},
            },
            "apc_mode_toggle": {
                "idle": {"effect": APCMK2ButtonEffect.OFF},
                "running": {"effect": APCMK2ButtonEffect.ON},
            }
        },
        "record": {
            "null": {
                "idle": {"effect": APCMK2ButtonEffect.OFF},
                "running": {"effect": APCMK2ButtonEffect.ON},
            },
            "subprocess": {
                "idle": {"effect": APCMK2ButtonEffect.OFF},
                "running": {"effect": APCMK2ButtonEffect.ON},
            },
            "command": {
                "idle": {"effect": APCMK2ButtonEffect.OFF},
                "running": {"effect": APCMK2ButtonEffect.ON},
            },
            "dog_mode_toggle": {
                "idle": {"effect": APCMK2ButtonEffect.OFF},
                "running": {"effect": APCMK2ButtonEffect.ON},
            },
            "apc_mode_change": {
                "idle": {"effect": APCMK2ButtonEffect.OFF},
                "running": {"effect": APCMK2ButtonEffect.ON},
            },
            "apc_mode_toggle": {
                "idle": {"effect": APCMK2ButtonEffect.OFF},
                "running": {"effect": APCMK2ButtonEffect.ON},
            },
        },
        "recording": {
            "null": {
                "idle": {"effect": APCMK2ButtonEffect.OFF},
                "running": {"effect": APCMK2ButtonEffect.ON},
            },
            "subprocess": {
                "idle": {"effect": APCMK2ButtonEffect.OFF},
                "running": {"effect": APCMK2ButtonEffect.ON},
            },
            "command": {
                "idle": {"effect": APCMK2ButtonEffect.OFF},
                "running": {"effect": APCMK2ButtonEffect.ON},
            },
            "dog_mode_toggle": {
                "idle": {"effect": APCMK2ButtonEffect.OFF},
                "running": {"effect": APCMK2ButtonEffect.BLINK},
            },
            "apc_mode_change": {
                "idle": {"effect": APCMK2ButtonEffect.OFF},
                "running": {"effect": APCMK2ButtonEffect.ON},
            },
            "apc_mode_toggle": {
                "idle": {"effect": APCMK2ButtonEffect.OFF},
                "running": {"effect": APCMK2ButtonEffect.ON},
            },
        },
        "preview": {
            "null": {
                "idle": {"effect": APCMK2ButtonEffect.OFF},
                "running": {"effect": APCMK2ButtonEffect.ON},
            },
            "subprocess": {
                "idle": {"effect": APCMK2ButtonEffect.OFF},
                "running": {"effect": APCMK2ButtonEffect.ON},
            },
            "command": {
                "idle": {"effect": APCMK2ButtonEffect.OFF},
                "running": {"effect": APCMK2ButtonEffect.ON},
            },
            "dog_mode_toggle": {
                "idle": {"effect": APCMK2ButtonEffect.OFF},
                "running": {"effect": APCMK2ButtonEffect.BLINK},
            },
            "apc_mode_change": {
                "idle": {"effect": APCMK2ButtonEffect.OFF},
                "running": {"effect": APCMK2ButtonEffect.ON},
            },
            "apc_mode_toggle": {
                "idle": {"effect": APCMK2ButtonEffect.OFF},
                "running": {"effect": APCMK2ButtonEffect.ON},
            },
        }
    }
}

ACTION_MAP = {
    "normal": {
        "buttons": {
            "VOLUME": APCMK2Action(command=SetMotionSwitcherNormal, payload=SWITCHER_TOPIC, atype=APCMK2ActionType.dog_mode_toggle),
            "PAN": APCMK2Action(command=SetMotionSwitcherAdvanced, payload=SWITCHER_TOPIC, atype=APCMK2ActionType.dog_mode_toggle),
            "SEND": APCMK2Action(command=SetMotionSwitcherAI, payload=SWITCHER_TOPIC, atype=APCMK2ActionType.dog_mode_toggle),
            "SHIFT": APCMK2Action(command=None, payload=APCMK2Mode.preview, atype=APCMK2ActionType.apc_mode_toggle),
            "REC_ARM": APCMK2Action(command=None, payload=APCMK2Mode.record, atype=APCMK2ActionType.apc_mode_change),
            "UP": APCMK2Action(command=SpeedLevelHigh, payload=SPORT_TOPIC, atype=APCMK2ActionType.command),
            "DOWN": APCMK2Action(command=SpeedLevelLow, payload=SPORT_TOPIC, atype=APCMK2ActionType.command),
            "STOP_ALL": APCMK2Action(command=StopMove, payload=SPORT_TOPIC, atype=APCMK2ActionType.command)
        },
        "pads": {
        },
        "faders": {
            "FADER_1": APCMK2Action(command=SetVolume, payload=VUI_TOPIC, atype=APCMK2ActionType.command),
            "FADER_2": APCMK2Action(command=SetBrightness, payload=VUI_TOPIC, atype=APCMK2ActionType.command),
            "FADER_3": APCMK2Action(command=BodyHeight, payload=MOVE_TOPIC, atype=APCMK2ActionType.command),
            "FADER_4": APCMK2Action(command=FootRaiseHeight, payload=MOVE_TOPIC, atype=APCMK2ActionType.command),
            
        }
    },
    "preview": {
        "buttons": {
            "VOLUME": APCMK2Action(command=SetMotionSwitcherNormal, payload=SWITCHER_TOPIC, atype=APCMK2ActionType.dog_mode_toggle),
            "PAN": APCMK2Action(command=SetMotionSwitcherAdvanced, payload=SWITCHER_TOPIC, atype=APCMK2ActionType.dog_mode_toggle),
            "SEND": APCMK2Action(command=SetMotionSwitcherAI, payload=SWITCHER_TOPIC, atype=APCMK2ActionType.dog_mode_toggle),
            "SHIFT": APCMK2Action(command=None, payload=APCMK2Mode.preview, atype=APCMK2ActionType.apc_mode_toggle),
            "UP": APCMK2Action(command=SpeedLevelHigh, payload=SPORT_TOPIC, atype=APCMK2ActionType.command),
            "DOWN": APCMK2Action(command=SpeedLevelLow, payload=SPORT_TOPIC, atype=APCMK2ActionType.command),
            "STOP_ALL": APCMK2Action(command=StopMove, payload=SPORT_TOPIC, atype=APCMK2ActionType.command)
        },
        "pads": {
        },
        "faders": {
            "FADER_1": APCMK2Action(command=SetVolume, payload=VUI_TOPIC, atype=APCMK2ActionType.command),
            "FADER_2": APCMK2Action(command=SetBrightness, payload=VUI_TOPIC, atype=APCMK2ActionType.command),
            "FADER_3": APCMK2Action(command=BodyHeight, payload=MOVE_TOPIC, atype=APCMK2ActionType.command),
            "FADER_4": APCMK2Action(command=FootRaiseHeight, payload=MOVE_TOPIC, atype=APCMK2ActionType.command),
        }
    },
    "record": {
        "buttons": {
            "VOLUME": APCMK2Action(command=SetMotionSwitcherNormal, payload=SWITCHER_TOPIC, atype=APCMK2ActionType.dog_mode_toggle),
            "PAN": APCMK2Action(command=SetMotionSwitcherAdvanced, payload=SWITCHER_TOPIC, atype=APCMK2ActionType.dog_mode_toggle),
            "SEND": APCMK2Action(command=SetMotionSwitcherAI, payload=SWITCHER_TOPIC, atype=APCMK2ActionType.dog_mode_toggle),
            "SHIFT": APCMK2Action(command=None, payload=APCMK2Mode.preview, atype=APCMK2ActionType.apc_mode_toggle),
            "REC_ARM": APCMK2Action(command=None, payload=APCMK2Mode.normal, atype=APCMK2ActionType.apc_mode_change),
            "UP": APCMK2Action(command=SpeedLevelHigh, payload=SPORT_TOPIC, atype=APCMK2ActionType.command),
            "DOWN": APCMK2Action(command=SpeedLevelLow, payload=SPORT_TOPIC, atype=APCMK2ActionType.command),
            "STOP_ALL": APCMK2Action(command=StopMove, payload=SPORT_TOPIC, atype=APCMK2ActionType.command)
        },
        "pads": {
        },
        "faders": {
            "FADER_1": APCMK2Action(command=SetVolume, payload=VUI_TOPIC, atype=APCMK2ActionType.command),
            "FADER_2": APCMK2Action(command=SetBrightness, payload=VUI_TOPIC, atype=APCMK2ActionType.command),
            "FADER_3": APCMK2Action(command=BodyHeight, payload=MOVE_TOPIC, atype=APCMK2ActionType.command),
            "FADER_4": APCMK2Action(command=FootRaiseHeight, payload=MOVE_TOPIC, atype=APCMK2ActionType.command),
        }
    },
    "recording": {
        "buttons": {
            "VOLUME": APCMK2Action(command=SetMotionSwitcherNormal, payload=SWITCHER_TOPIC, atype=APCMK2ActionType.dog_mode_toggle),
            "PAN": APCMK2Action(command=SetMotionSwitcherAdvanced, payload=SWITCHER_TOPIC, atype=APCMK2ActionType.dog_mode_toggle),
            "SEND": APCMK2Action(command=SetMotionSwitcherAI, payload=SWITCHER_TOPIC, atype=APCMK2ActionType.dog_mode_toggle),
            "SHIFT": APCMK2Action(command=None, payload=APCMK2Mode.preview, atype=APCMK2ActionType.apc_mode_toggle),
            "UP": APCMK2Action(command=SpeedLevelHigh, payload=SPORT_TOPIC, atype=APCMK2ActionType.command),
            "DOWN": APCMK2Action(command=SpeedLevelLow, payload=SPORT_TOPIC, atype=APCMK2ActionType.command),
            "STOP_ALL": APCMK2Action(command=StopMove, payload=SPORT_TOPIC, atype=APCMK2ActionType.command)
            # TODO Make something to discard recordings?
            # "CLIP_STOP": APCMK2Action(command=CaptureCommand(action=CaptureAction.DISCARD, name=item), payload=CAPTURE_TOPIC, atype=APCMK2ActionType.capture)
        },
        "pads": {
        },
        "faders": {
            "FADER_1": APCMK2Action(command=SetVolume, payload=VUI_TOPIC, atype=APCMK2ActionType.command),
            "FADER_2": APCMK2Action(command=SetBrightness, payload=VUI_TOPIC, atype=APCMK2ActionType.command),
            "FADER_3": APCMK2Action(command=BodyHeight, payload=MOVE_TOPIC, atype=APCMK2ActionType.command),
            "FADER_4": APCMK2Action(command=FootRaiseHeight, payload=MOVE_TOPIC, atype=APCMK2ActionType.command),
        }
    }
}

cap_files = get_cap_files()

for item in range(APC_MK2_NUM_PADS):
    if item in pad_commands:
        command = pad_commands[item][0]
        payload = pad_commands[item][1]
        atype = APCMK2ActionType.command
    else:
        command = None
        payload = None
        atype = APCMK2ActionType.null

    if item <APC_MK2_NUM_PADS/2:
        # Commands
        ACTION_MAP["normal"]["pads"][item] = APCMK2Action(command=command, payload=payload, atype=atype)

        ACTION_MAP["preview"]["pads"][item] = APCMK2Action(command=command, payload=payload, atype=atype)

        ACTION_MAP["record"]["pads"][item] = APCMK2Action(command=command, payload=payload, atype=atype)

        ACTION_MAP["recording"]["pads"][item] = APCMK2Action(command=command, payload=payload, atype=atype)

    else:
        # Captures
        if item in cap_files:
            ACTION_MAP["normal"]["pads"][item] = APCMK2Action(command='play', payload=item, atype=APCMK2ActionType.subprocess)

            ACTION_MAP["preview"]["pads"][item] = APCMK2Action(command='preview', payload=item, atype=APCMK2ActionType.subprocess)

            ACTION_MAP["record"]["pads"][item] = APCMK2Action(command=None, payload=None, atype=APCMK2ActionType.subprocess)

            ACTION_MAP["recording"]["pads"][item] = APCMK2Action(command=None, payload=None, atype=APCMK2ActionType.subprocess)
            
        else: 
            ACTION_MAP["normal"]["pads"][item] = APCMK2Action(command=None, payload=None, atype=APCMK2ActionType.unassigned)

            ACTION_MAP["preview"]["pads"][item] = APCMK2Action(command=None, payload=None, atype=APCMK2ActionType.unassigned)

            ACTION_MAP["record"]["pads"][item] = APCMK2Action(command=CaptureCommand(action=CaptureAction.START, name=item), payload=CAPTURE_TOPIC, atype=APCMK2ActionType.capture)

            ACTION_MAP["recording"]["pads"][item] = APCMK2Action(command=CaptureCommand(action=CaptureAction.STOP, name=item), payload=CAPTURE_TOPIC, atype=APCMK2ActionType.capture)


