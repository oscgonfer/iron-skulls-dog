from enum import Enum
from config import *
from command import *
from apc_mk2_map import pad_commands
from apc_mk2_items import *
from capture import CaptureCommand, CaptureAction
from os import listdir
from os.path import isfile, join, dirname, realpath, splitext

APC_PORT_NAME = 'APC mini mk2:APC mini mk2 APC mini mk2 Contr 20:0'
APC_MK2_NUM_PADS = 64
APC_MK2_FADER_LIMITS = [0, 127]

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
            "VOLUME": APCMK2Action(command=SetMotionSwitcherNormal, topic=SWITCHER_TOPIC, atype=APCMK2ActionType.dog_mode_toggle),
            "PAN": APCMK2Action(command=SetMotionSwitcherAdvanced, topic=SWITCHER_TOPIC, atype=APCMK2ActionType.dog_mode_toggle),
            "SEND": APCMK2Action(command=SetMotionSwitcherAI, topic=SWITCHER_TOPIC, atype=APCMK2ActionType.dog_mode_toggle),
            "SHIFT": APCMK2Action(command=None, payload=APCMK2Mode.preview, atype=APCMK2ActionType.apc_mode_toggle),
            "REC_ARM": APCMK2Action(command=None, payload=APCMK2Mode.record, atype=APCMK2ActionType.apc_mode_change),
            "UP": APCMK2Action(command=SpeedLevelHigh, topic=SPORT_TOPIC, atype=APCMK2ActionType.command),
            "DOWN": APCMK2Action(command=SpeedLevelLow, topic=SPORT_TOPIC, atype=APCMK2ActionType.command),
            "STOP_ALL": APCMK2Action(command=StopMove, topic=SPORT_TOPIC, atype=APCMK2ActionType.command)
        },
        "pads": {
        },
        "faders": {
            "FADER_1": APCMK2Action(command=SetVolume, topic=VUI_TOPIC, atype=APCMK2ActionType.command),
            "FADER_2": APCMK2Action(command=SetBrightness, topic=VUI_TOPIC, atype=APCMK2ActionType.command),
            "FADER_3": APCMK2Action(command=BodyHeight, topic=MOVE_TOPIC, atype=APCMK2ActionType.command),
            "FADER_4": APCMK2Action(command=FootRaiseHeight, topic=MOVE_TOPIC, atype=APCMK2ActionType.command),
            # Sensitivity for joystick
            "FADER_5": APCMK2Action(command=None, topic=None, atype=APCMK2ActionType.unassigned),
            "FADER_6": APCMK2Action(command=None, topic=None, atype=APCMK2ActionType.unassigned),
            "FADER_7": APCMK2Action(command=None, topic=None, atype=APCMK2ActionType.unassigned)

        }
    },
    "preview": {
        "buttons": {
            "VOLUME": APCMK2Action(command=SetMotionSwitcherNormal, topic=SWITCHER_TOPIC, atype=APCMK2ActionType.dog_mode_toggle),
            "PAN": APCMK2Action(command=SetMotionSwitcherAdvanced, topic=SWITCHER_TOPIC, atype=APCMK2ActionType.dog_mode_toggle),
            "SEND": APCMK2Action(command=SetMotionSwitcherAI, topic=SWITCHER_TOPIC, atype=APCMK2ActionType.dog_mode_toggle),
            "SHIFT": APCMK2Action(command=None, payload=APCMK2Mode.preview, atype=APCMK2ActionType.apc_mode_toggle),
            "UP": APCMK2Action(command=SpeedLevelHigh, topic=SPORT_TOPIC, atype=APCMK2ActionType.command),
            "DOWN": APCMK2Action(command=SpeedLevelLow, topic=SPORT_TOPIC, atype=APCMK2ActionType.command),
            "STOP_ALL": APCMK2Action(command=StopMove, topic=SPORT_TOPIC, atype=APCMK2ActionType.command)
        },
        "pads": {
        },
        "faders": {
            "FADER_1": APCMK2Action(command=SetVolume, topic=VUI_TOPIC, atype=APCMK2ActionType.command),
            "FADER_2": APCMK2Action(command=SetBrightness, topic=VUI_TOPIC, atype=APCMK2ActionType.command),
            "FADER_3": APCMK2Action(command=BodyHeight, topic=MOVE_TOPIC, atype=APCMK2ActionType.command),
            "FADER_4": APCMK2Action(command=FootRaiseHeight, topic=MOVE_TOPIC, atype=APCMK2ActionType.command),
            # Sensitivity for joystick
            "FADER_5": APCMK2Action(command=None, topic=None, atype=APCMK2ActionType.unassigned),
            "FADER_6": APCMK2Action(command=None, topic=None, atype=APCMK2ActionType.unassigned),
            "FADER_7": APCMK2Action(command=None, topic=None, atype=APCMK2ActionType.unassigned)

        }
    },
    "record": {
        "buttons": {
            "VOLUME": APCMK2Action(command=SetMotionSwitcherNormal, topic=SWITCHER_TOPIC, atype=APCMK2ActionType.dog_mode_toggle),
            "PAN": APCMK2Action(command=SetMotionSwitcherAdvanced, topic=SWITCHER_TOPIC, atype=APCMK2ActionType.dog_mode_toggle),
            "SEND": APCMK2Action(command=SetMotionSwitcherAI, topic=SWITCHER_TOPIC, atype=APCMK2ActionType.dog_mode_toggle),
            "SHIFT": APCMK2Action(command=None, payload=APCMK2Mode.preview, atype=APCMK2ActionType.apc_mode_toggle),
            "REC_ARM": APCMK2Action(command=None, payload=APCMK2Mode.normal, atype=APCMK2ActionType.apc_mode_change),
            "UP": APCMK2Action(command=SpeedLevelHigh, topic=SPORT_TOPIC, atype=APCMK2ActionType.command),
            "DOWN": APCMK2Action(command=SpeedLevelLow, topic=SPORT_TOPIC, atype=APCMK2ActionType.command),
            "STOP_ALL": APCMK2Action(command=StopMove, topic=SPORT_TOPIC, atype=APCMK2ActionType.command)
        },
        "pads": {
        },
        "faders": {
            "FADER_1": APCMK2Action(command=SetVolume, topic=VUI_TOPIC, atype=APCMK2ActionType.command),
            "FADER_2": APCMK2Action(command=SetBrightness, topic=VUI_TOPIC, atype=APCMK2ActionType.command),
            "FADER_3": APCMK2Action(command=BodyHeight, topic=MOVE_TOPIC, atype=APCMK2ActionType.command),
            "FADER_4": APCMK2Action(command=FootRaiseHeight, topic=MOVE_TOPIC, atype=APCMK2ActionType.command),
            # Sensitivity for joystick
            "FADER_5": APCMK2Action(command=None, topic=None, atype=APCMK2ActionType.unassigned),
            "FADER_6": APCMK2Action(command=None, topic=None, atype=APCMK2ActionType.unassigned),
            "FADER_7": APCMK2Action(command=None, topic=None, atype=APCMK2ActionType.unassigned)

        }
    },
    "recording": {
        "buttons": {
            "VOLUME": APCMK2Action(command=SetMotionSwitcherNormal, topic=SWITCHER_TOPIC, atype=APCMK2ActionType.dog_mode_toggle),
            "PAN": APCMK2Action(command=SetMotionSwitcherAdvanced, topic=SWITCHER_TOPIC, atype=APCMK2ActionType.dog_mode_toggle),
            "SEND": APCMK2Action(command=SetMotionSwitcherAI, topic=SWITCHER_TOPIC, atype=APCMK2ActionType.dog_mode_toggle),
            "SHIFT": APCMK2Action(command=None, payload=APCMK2Mode.preview, atype=APCMK2ActionType.apc_mode_toggle),
            "UP": APCMK2Action(command=SpeedLevelHigh, topic=SPORT_TOPIC, atype=APCMK2ActionType.command),
            "DOWN": APCMK2Action(command=SpeedLevelLow, topic=SPORT_TOPIC, atype=APCMK2ActionType.command),
            "STOP_ALL": APCMK2Action(command=StopMove, topic=SPORT_TOPIC, atype=APCMK2ActionType.command)
            # TODO Make something to discard recordings?
            # "CLIP_STOP": APCMK2Action(command=CaptureCommand(action=CaptureAction.DISCARD, name=item), topic=CAPTURE_TOPIC, atype=APCMK2ActionType.capture)
        },
        "pads": {
        },
        "faders": {
            "FADER_1": APCMK2Action(command=SetVolume, topic=VUI_TOPIC, atype=APCMK2ActionType.command),
            "FADER_2": APCMK2Action(command=SetBrightness, topic=VUI_TOPIC, atype=APCMK2ActionType.command),
            "FADER_3": APCMK2Action(command=BodyHeight, topic=MOVE_TOPIC, atype=APCMK2ActionType.command),
            "FADER_4": APCMK2Action(command=FootRaiseHeight, topic=MOVE_TOPIC, atype=APCMK2ActionType.command),
            # Sensitivity for joystick
            "FADER_5": APCMK2Action(command=None, topic=None, atype=APCMK2ActionType.unassigned),
            "FADER_6": APCMK2Action(command=None, topic=None, atype=APCMK2ActionType.unassigned),
            "FADER_7": APCMK2Action(command=None, topic=None, atype=APCMK2ActionType.unassigned)

        }
    }
}

cap_files = get_cap_files()

for item in range(APC_MK2_NUM_PADS):
    command = None
    topic = None
    payload = None
    atype = APCMK2ActionType.null

    if item in pad_commands:
        command = pad_commands[item]["command"]
        topic = pad_commands[item]["topic"]
        if "payload" in pad_commands[item]:
            payload = pad_commands[item]["payload"]
        else:
            payload = None
        atype = APCMK2ActionType.command

    if item <APC_MK2_NUM_PADS/2:

        # Commands
        ACTION_MAP["normal"]["pads"][item] = APCMK2Action(command=command, topic=topic, 
            payload=payload, atype=atype)

        ACTION_MAP["preview"]["pads"][item] = APCMK2Action(command=command, topic=topic, 
            payload=payload, atype=atype)

        ACTION_MAP["record"]["pads"][item] = APCMK2Action(command=command, topic=topic, 
            payload=payload, atype=atype)

        ACTION_MAP["recording"]["pads"][item] = APCMK2Action(command=command, topic=topic, 
            payload=payload, atype=atype)

    else:
        # Captures
        if item in cap_files:
            ACTION_MAP["normal"]["pads"][item] = APCMK2Action(command='play', payload=item, atype=APCMK2ActionType.subprocess)

            ACTION_MAP["preview"]["pads"][item] = APCMK2Action(command='preview', payload=item, atype=APCMK2ActionType.subprocess)

            ACTION_MAP["record"]["pads"][item] = APCMK2Action(command=None, atype=APCMK2ActionType.subprocess)

            ACTION_MAP["recording"]["pads"][item] = APCMK2Action(command=None, atype=APCMK2ActionType.subprocess)
            
        else: 
            ACTION_MAP["normal"]["pads"][item] = APCMK2Action(command=None, atype=APCMK2ActionType.unassigned)

            ACTION_MAP["preview"]["pads"][item] = APCMK2Action(command=None, atype=APCMK2ActionType.unassigned)

            ACTION_MAP["record"]["pads"][item] = APCMK2Action(command=CaptureCommand(action=CaptureAction.START, name=item), topic=CAPTURE_TOPIC, atype=APCMK2ActionType.capture)

            ACTION_MAP["recording"]["pads"][item] = APCMK2Action(command=CaptureCommand(action=CaptureAction.STOP, name=item), topic=CAPTURE_TOPIC, atype=APCMK2ActionType.capture)


