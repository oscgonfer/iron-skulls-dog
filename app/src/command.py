import json
from go2_webrtc_driver.constants import *
from tools import map_range
from enum import IntEnum

# TODO Are there more modes?
class DogState(IntEnum):
    BUSY=0 # Working on something. Maybe dancing, saying hello...
    MOVE=1 # Accepts any move command except Euler. Run, stair 1 and 2, walk, endurance
    STANDING=2 # Accepts Euler
    MOVING=3 # Moving with any of run, stair 1 and 2, walk, endurance
    PRONE=5 # Down
    LOCKED=6 # Posture locked, can only go prone
    SAVE=7 # Seems to enter after a bit into this when prone
    SIT=10 # Seems only in this mode when sitting only
    JUMP=12 # Seems only to be in this mode when jumping only
    POUNCE=13 # Seems only to be in this mode when pouncing only
    AI_AGILE=9 # AI Agile mode
    AI_FREEBOUND=15 # AI FreeBound mode
    AI_FREEJUMP=16 # AI FreeJump mode
    AI_FREEAVOID=17 # AI FreeAvoid mode
    AI_WALKSTAIR=18 # AI WalkStair mode
    AI_WALKUPRIGHT=19 # AI WalkUpRight mode
    AI_CROSSSTEP=20 # AI CrossStep mode
    AI_WTF=21

class DogMode(IntEnum):
    NORMAL=0
    ADVANCED=1
    AI=2

# TODO Add here other commands that shouldn't send async while in normal mode
AVOID_ASYNC = {
    "normal": [
        DogState.MOVING
    ],
    "advanced": [],
    "ai": []
}

CMD_LIMITS = {
    "MOVE": { 
        "vx": {"range": [-2.5, 3.8], "mpc_key": "FADER_5"}, # NOK
        "vy": {"range": [-1, 1], "mpc_key": "FADER_5"}, 
        "vyaw": {"range": [-4, 4], "mpc_key": "FADER_6"}, 
        "roll": {"range": [-0.65, 0.6], "mpc_key": "FADER_7"}, # Limited
        "yaw": {"range": [-0.65, 0.6], "mpc_key": "FADER_7"}, # Limited
        "pitch": {"range": [-0.5, 0.4], "mpc_key": "FADER_7"} # Limited
    },
    "STANDING": {
        "vx": {"range": [0, 0], "mpc_key": "FADER_5"}, # No move range in standing
        "vy": {"range":  [0, 0], "mpc_key": "FADER_5"}, # No move range in standing
        "vyaw": {"range":  [0, 0], "mpc_key": "FADER_6"}, # No move range in standing
        "roll": {"range": [-0.75, 0.75], "mpc_key": "FADER_7"},
        "pitch": {"range": [-0.75, 0.75], "mpc_key": "FADER_7"},
        "yaw": {"range": [-0.6, 0.6], "mpc_key": "FADER_7"}
    },
    "MOVING": {
        "vx": {"range": [-2.5, 3.8], "mpc_key": "FADER_5"}, # NOK
        "vy": {"range": [-1, 1], "mpc_key": "FADER_5"},
        "vyaw": {"range": [-4, 4], "mpc_key": "FADER_6"},
        "roll": {"range": [-0.75, 0.6], "mpc_key": "FADER_7"}, # Limited
        "yaw": {"range": [-0.75, 0.6], "mpc_key": "FADER_7"}, # Limited
        "pitch": {"range": [-0.5, 0.4], "mpc_key": "FADER_7"} # Limited
    },
    "AI_AGILE": {
        "vx": {"range": [-1.6, 1.6], "mpc_key": "FADER_5"}, # Not according to documentation
        "vy": {"range": [-1.4, 1.4], "mpc_key": "FADER_5"},
        "vyaw": {"range": [-2.3, 2.3], "mpc_key": "FADER_6"}, # Out of limit
        "roll": {"range": [0, 0], "mpc_key": "FADER_7"}, # OK it being 0?
        "yaw": {"range": [0, 0], "mpc_key": "FADER_7"}, # OK it being 0?
        "pitch": {"range": [0, 0], "mpc_key": "FADER_7"} # OK it being 0?
    },
    "AI_FREEBOUND": {
        "vx": {"range": [-0.6, 0.6], "mpc_key": "FADER_5"},
        "vy": {"range": [-0.4, 0.4], "mpc_key": "FADER_5"},
        "vyaw": {"range": [-0.8, 0.8], "mpc_key": "FADER_6"},
        "roll": {"range": [0, 0], "mpc_key": "FADER_7"}, # OK it being 0?
        "yaw": {"range": [0, 0], "mpc_key": "FADER_7"}, # OK it being 0?
        "pitch": {"range": [0, 0], "mpc_key": "FADER_7"} # OK it being 0?
    },
    "AI_FREEJUMP": {
        "vx": {"range": [-1.6, 1.6], "mpc_key": "FADER_5"},
        "vy": {"range": [-0.4, 0.4], "mpc_key": "FADER_5"},
        "vyaw": {"range": [-0.8, 0.8], "mpc_key": "FADER_6"},
        "roll": {"range": [0, 0], "mpc_key": "FADER_7"}, # OK it being 0?
        "yaw": {"range": [0, 0], "mpc_key": "FADER_7"}, # OK it being 0?
        "pitch": {"range": [0, 0], "mpc_key": "FADER_7"} # OK it being 0?
    },
    "AI_FREEAVOID": {
        "vx": {"range": [-0.6, 0.6], "mpc_key": "FADER_5"},
        "vy": {"range": [-0.4, 0.4], "mpc_key": "FADER_5"},
        "vyaw": {"range": [-0.8, 0.8], "mpc_key": "FADER_6"},
        "roll": {"range": [0, 0], "mpc_key": "FADER_7"}, # OK it being 0?
        "yaw": {"range": [0, 0], "mpc_key": "FADER_7"}, # OK it being 0?
        "pitch": {"range": [0, 0], "mpc_key": "FADER_7"} # OK it being 0?
    },
    "AI_WALKSTAIR": {
        "vx": {"range": [-1.2, 1.2], "mpc_key": "FADER_5"},
        "vy": {"range": [-0.4, 0.4], "mpc_key": "FADER_5"},
        "vyaw": {"range": [-0.8, 0.8], "mpc_key": "FADER_6"},
        "roll": {"range": [0, 0], "mpc_key": "FADER_7"}, # OK it being 0?
        "yaw": {"range": [0, 0], "mpc_key": "FADER_7"}, # OK it being 0?
        "pitch": {"range": [0, 0], "mpc_key": "FADER_7"} # OK it being 0?
    },
    "AI_WALKUPRIGHT": {
        "vx": {"range": [-0.6, 0.6], "mpc_key": "FADER_5"},
        "vy": {"range": [-0.4, 0.4], "mpc_key": "FADER_5"},
        "vyaw": {"range": [-0.8, 0.8], "mpc_key": "FADER_6"},
        "roll": {"range": [0, 0], "mpc_key": "FADER_7"}, # OK it being 0?
        "yaw": {"range": [0, 0], "mpc_key": "FADER_7"}, # OK it being 0?
        "pitch": {"range": [0, 0], "mpc_key": "FADER_7"} # OK it being 0?
    },
    "AI_CROSSSTEP": {
        "vx": {"range": [-0.6, 0.6], "mpc_key": "FADER_5"},
        "vy": {"range": [-0.4, 0.4], "mpc_key": "FADER_5"},
        "vyaw": {"range": [-0.8, 0.8], "mpc_key": "FADER_6"},
        "roll": {"range": [0, 0], "mpc_key": "FADER_7"}, # OK it being 0?
        "yaw": {"range": [0, 0], "mpc_key": "FADER_7"}, # OK it being 0?
        "pitch": {"range": [0, 0], "mpc_key": "FADER_7"} # OK it being 0?
    }
}

class Command:
    def __init__(self, payload, associated_modes= None, associated_states = None, toggle = False):
        # Exportable
        self.topic = payload["topic"]
        self.options = payload["options"]
        self.expect_reply = payload["expect_reply"] if "expect_reply" in payload else False
        self.update_switcher_mode = payload["update_switcher_mode"] if "update_switcher_mode" in payload else False
        self.post_hook = payload["post_hook"] if "post_hook" in payload else None
        self.additional_wait = payload["additional_wait"] if "additional_wait" in payload else 0
        # Internal only
        self.associated_modes = associated_modes
        self.associated_states = associated_states
        self.toggle = toggle

    def as_dict(self):
        if self.post_hook is None:
            post_hook = None
        elif type(self.post_hook)==dict:
            post_hook = self.post_hook
        else:
            post_hook = self.post_hook.as_dict()

        return {
            'topic': self.topic,
            'options': self.options,
            'expect_reply': self.expect_reply,
            'update_switcher_mode': self.update_switcher_mode,
            'post_hook': post_hook,
            'additional_wait': self.additional_wait,
        }

    def to_json(self):
        return json.dumps(self.as_dict())

class AudioCommand:
    def __init__(self, payload, associated_modes = None, associated_states = None):
        # Exportable
        self.source = payload["source"]
        self.options = payload["options"]
        # Internal only
        self.associated_modes = associated_modes
        self.associated_states = associated_states

    def as_dict(self):
        return {
            'source': self.source,
            'options': self.options,            
        }

    def to_json(self):
        return json.dumps(self.as_dict())

class PlayDogAudioFile(AudioCommand):
    """
    Play an audio file previously uploaded to the dog
    """
    def __init__(self, audio_file: str = ''):
        payload = {
            "source": "dog_file",
            "options": {
                "audio_file": audio_file
            }
        }
        super().__init__(payload)

class PlayClientAudioFile(AudioCommand):
    """
    Play an audio file locally in the client
    """
    def __init__(self, audio_file: str = ''):
        payload = {
            "source": "client_file",
            "options": {
                "audio_file": audio_file
            }
        }
        super().__init__(payload)

class StreamAudioFile(AudioCommand):
    """
    Play an audio file locally in the client
    """
    def __init__(self, audio_stream: str = ''):
        payload = {
            "source": "stream_file",
            "options": {
                "audio_stream": audio_stream
            }
        }
        super().__init__(payload)

# 1001
class Damp(Command):
    """
    Enter damping state
    All motor joints stop moving and enter a damping state.
    This mode has the highest priority and is used for emergency 
    stops in unexpected situations
    """
    def __init__(self):
        payload = {
            "topic": RTC_TOPIC["SPORT_MOD"],
            "options": {
                "parameter": "",
                "api_id": 1001
            },
            "expect_reply": False,
            "update_switcher_mode": False,
            "post_hook": None,
            "additional_wait": 0
        }
        super().__init__(payload)

# 1002
class BalanceStand(Command):
    """
    Unlock
    Release the joint motor lock and switch from normal standing, 
    crouching, continuous stepping state to balanced standing mode.
    In this mode, push the remote control stick and the robot will move
    """
    def __init__(self):
        payload = {
            "topic": RTC_TOPIC["SPORT_MOD"],
            "options": {
                "parameter": "",
                "api_id": 1002
            },
            "expect_reply": False,
            "update_switcher_mode": False,
            "post_hook": None,
            "additional_wait": 0
        }
        super().__init__(payload, associated_states=[DogState.MOVE])

# 1003
class StopMove(Command):
    """
    Stop the current action and restore most instructions to their default values.
    """
    def __init__(self):
        payload = {
            "topic": RTC_TOPIC["SPORT_MOD"],
            "options": {
                "parameter": "",
                "api_id": 1003
            },
            "expect_reply": False,
            "update_switcher_mode": False,
            "post_hook": StandUp(),
            "additional_wait": 1
        }
        super().__init__(payload)

# 1004
class StandUp(Command):
    """
    Joint locking, standing high
    The robot dog stands normally tall and the motor joints remain locked.
    Compared to the balanced standing mode, the posture of the robot
    dog in this mode will not always be balanced. 
    The default standing height is 0.32m
    """
    def __init__(self):
        payload = {
            "topic": RTC_TOPIC["SPORT_MOD"],
            "options": {
                "parameter": "",
                "api_id": 1004
            },
            "expect_reply": False,
            "update_switcher_mode": False,
            "post_hook": None,
            "additional_wait": 0
        }
        super().__init__(payload, associated_states=[DogState.LOCKED])

# 1005
class StandDown(Command):
    """
    Joint locking, standing low
    The robotic dog lies down and the motor joint remains locked
    """
    def __init__(self):
        payload = {
            "topic": RTC_TOPIC["SPORT_MOD"],
            "options": {
                "parameter": "",
                "api_id": 1005
            },
            "expect_reply": False,
            "update_switcher_mode": False,
            "post_hook": None,
            "additional_wait": 0
        }
        super().__init__(payload, associated_states=[DogState.PRONE, DogState.SAVE])

# 1006
class RecoveryStand(Command):
    """
    Recovery standing
    Return from overturned to balanced standing. 
    For safety, the response will only return to standing in the overturned state
    """
    def __init__(self):
        payload = {
            "topic": RTC_TOPIC["SPORT_MOD"],
            "options": {
                "parameter": "",
                "api_id": 1006
            },
            "expect_reply": False,
            "update_switcher_mode": False,
            "post_hook": None,
            "additional_wait": 0
        }
        super().__init__(payload)

# 1007
class Euler(Command):
    def __init__(self, roll: float, pitch: float, yaw: float):
        payload = {
            "topic": RTC_TOPIC["SPORT_MOD"],
            "options": {
                "parameter": json.dumps({"x": roll, "y": pitch, "z": yaw}),
                "api_id": 1007
            },
            "expect_reply": False,
            "update_switcher_mode": False,
            "post_hook": None,
            "additional_wait": 0
        }
        super().__init__(payload)

# 1008
class Move(Command):
    """
    Move at the specified speed
    Control the moving speed, the set speed is the speed 
    of the body coordinate system. It is recommended that you call
    BalanceStand once before you call Move to ensure that you unlock 
    and enter a removable state.
    Value range (Normal):
        Vx: [-0.6~0.6 ] (m/s)
        Vy: Value range [-0.4~0.4 ] (m/s) 
        Vyaw: Value range [-0.8~0.8 ] (rad/s)
    Value range (AI):
        Vx: [-0.6~0.6 ] (m/s)
        Vy: Value range [-0.4~0.4 ] (m/s) 
        Vyaw: Value range [-0.8~0.8 ] (rad/s)
    """
    def __init__(self, x: float, y: float, z: float):
        payload = {
            "topic": RTC_TOPIC["SPORT_MOD"],
            "options": {
                "parameter": json.dumps({"x": x, "y": y, "z": z}),
                "api_id": 1008
            },
            "expect_reply": False,
            "update_switcher_mode": False,
            "post_hook": None,
            "additional_wait": 0
        }
        super().__init__(payload)

# 1008
class MoveToPos(Command):
    """
    Move to certain position
    Control the moving speed, the set speed is the speed 
    of the body coordinate system. It is recommended that you call
    BalanceStand once before you call Move to ensure that you unlock 
    and enter a removable state.
    """
    def __init__(self, x: float, y: float, z: float):
        payload = {
            "topic": RTC_TOPIC["SPORT_MOD"],
            "options": {
                "parameter": json.dumps({"x": x, "y": y, "z": z}),
                "api_id": 1008
            },
            "expect_reply": False,
            "update_switcher_mode": False,
            "post_hook": None,
            "additional_wait": 0
        }
        super().__init__(payload)

# 1009
class Sit(Command):
    def __init__(self):
        payload = {
            "topic": RTC_TOPIC["SPORT_MOD"],
            "options": {
                "parameter": "",
                "api_id": 1009
            },
            "expect_reply": False,
            "update_switcher_mode": False,
            "post_hook": None,
            "additional_wait": 0
        }
        super().__init__(payload, associated_states=[DogState.SIT])

# 1010
class RiseSit(Command):
    def __init__(self):
        payload = {
            "topic": RTC_TOPIC["SPORT_MOD"],
            "options": {
                "parameter": "",
                "api_id": 1010
            },
            "expect_reply": False,
            "update_switcher_mode": False,
            "post_hook": None,
            "additional_wait": 0
        }
        super().__init__(payload)

# 1011
# TODO ASYNC?
class SwitchGait(Command):
    """
 	d: Gait enumeration value, with values ranging from 0 to 4, where 0 is idle, 1 is trot, 2 is trot running, 3 is forward climbing mode, and 4 is reverse climbing mode
    """
    def __init__(self, t: int):
        payload = {
            "topic": RTC_TOPIC["SPORT_MOD"],
            "options": {
                "parameter": {"data": t},
                "api_id": 1011
            },
            "expect_reply": False,
            "update_switcher_mode": False,
            "post_hook": None,
            "additional_wait": 0
        }
        super().__init__(payload)

class SwitchIdle(Command):
    """
 	Gait idle
    """
    def __init__(self):
        payload = {
            "topic": RTC_TOPIC["SPORT_MOD"],
            "options": {
                "parameter": {"data": 0},
                "api_id": 1011
            },
            "expect_reply": False,
            "update_switcher_mode": False,
            "post_hook": None,
            "additional_wait": 0
        }
        super().__init__(payload)

class SwitchTrot(Command):
    """
 	Gait trot
    """
    def __init__(self):
        payload = {
            "topic": RTC_TOPIC["SPORT_MOD"],
            "options": {
                "parameter": {"data": 1},
                "api_id": 1011
            },
            "expect_reply": False,
            "update_switcher_mode": False,
            "post_hook": None,
            "additional_wait": 0
        }
        super().__init__(payload)

class SwitchRunning(Command):
    """
 	Gait trot running
    """
    def __init__(self):
        payload = {
            "topic": RTC_TOPIC["SPORT_MOD"],
            "options": {
                "parameter": {"data": 2},
                "api_id": 1011
            },
            "expect_reply": False,
            "update_switcher_mode": False,
            "post_hook": None,
            "additional_wait": 0
        }
        super().__init__(payload)

class SwitchForwardClimb(Command):
    """
 	Gait forward climbing mode
    """
    def __init__(self):
        payload = {
            "topic": RTC_TOPIC["SPORT_MOD"],
            "options": {
                "parameter": {"data": 3},
                "api_id": 1011
            },
            "expect_reply": False,
            "update_switcher_mode": False,
            "post_hook": None,
            "additional_wait": 0
        }
        super().__init__(payload)

class SwitchBackwardClimb(Command):
    """
 	Gait forward climbing mode
    """
    def __init__(self):
        payload = {
            "topic": RTC_TOPIC["SPORT_MOD"],
            "options": {
                "parameter": {"data": 4},
                "api_id": 1011
            },
            "expect_reply": False,
            "update_switcher_mode": False,
            "post_hook": None,
            "additional_wait": 0
        }
        super().__init__(payload)

# 1012
class Trigger(Command):
    def __init__(self):
        payload = {
            "topic": RTC_TOPIC["SPORT_MOD"],
            "options": {
                "parameter": "",
                "api_id": 1012
            },
            "expect_reply": False,
            "update_switcher_mode": False,
            "post_hook": None,
            "additional_wait": 0
        }
        super().__init__(payload)

# 1013
class BodyHeight(Command):
    def __init__(self, height: float, value_range = None):
        """
        Body height between -0.18 and 0.03
        If value_range is not None, we assume they are
        passing us a range to map values to
        """
        if value_range is not None:
            height = map_range(height, value_range[0], value_range[1], -0.18, 0.03)
        payload = {
            "topic": RTC_TOPIC["SPORT_MOD"],
            "options": {
                "parameter": {"data": height},
                "api_id": 1013
            },
            "expect_reply": False,
            "update_switcher_mode": False,
            "post_hook": None,
            "additional_wait": 0
        }
        super().__init__(payload)

# 1014
class FootRaiseHeight(Command):
    def __init__(self, height: float, value_range = None):
        """
        Foot raise height height between -0.06, 0.03
        If value_range is not None, we assume they are
        passing us a range to map values to
        """
        if value_range is not None:
            height = map_range(height, value_range[0], value_range[1], -0.06, 0.03)
        payload = {
            "topic": RTC_TOPIC["SPORT_MOD"],
            "options": {
                "parameter": {"data": height},
                "api_id": 1014
            },
            "expect_reply": False,
            "update_switcher_mode": False,
            "post_hook": None,
            "additional_wait": 0
        }
        super().__init__(payload)

# 1015
class SpeedLevel(Command):
    """
        Set the speed range
        Speed range enumeration value, 
        with values of -1 for slow speed, and 1 for fast speed
    """
    def __init__(self, level: int):
        payload = {
            "topic": RTC_TOPIC["SPORT_MOD"],
            "options": {
                "parameter": {"data": level},
                "api_id": 1015
            },
            "expect_reply": False,
            "update_switcher_mode": False,
            "post_hook": None,
            "additional_wait": 0
        }
        super().__init__(payload)

# 1015 - High
class SpeedLevelHigh(SpeedLevel):
    """
        Set the speed range to High
    """
    def __init__(self):
        super().__init__(level=1)

# 1015 - Low
class SpeedLevelLow(SpeedLevel):
    """
        Set the speed range to Low
    """
    def __init__(self):
        super().__init__(level=-1)

# 1016
class Hello(Command):
    def __init__(self):
        payload = {
            "topic": RTC_TOPIC["SPORT_MOD"],
            "options": {
                "parameter": "",
                "api_id": 1016
            },
            "expect_reply": False,
            "update_switcher_mode": False,
            "post_hook": None,
            "additional_wait": 0
        }
        super().__init__(payload, associated_states=[DogState.BUSY])

# 1017
class Stretch(Command):
    def __init__(self):
        payload = {
            "topic": RTC_TOPIC["SPORT_MOD"],
            "options": {
                "parameter": "",
                "api_id": 1017
            },
            "expect_reply": False,
            "update_switcher_mode": False,
            "post_hook": None,
            "additional_wait": 0
        }
        super().__init__(payload, associated_states=[DogState.BUSY])

SPORT_PATH_POINT_SIZE = 30
# 1018

class TrajectoryFollow(Command):
    def __init__(self, path: list):
        l = len(path)

        if l != SPORT_PATH_POINT_SIZE:
            std_out(f"Path size NOK ({l})")
            return

        path_p = []
        for i in range(l):
            point = path[i]
            p = {}
            p["t_from_start"] = point.timeFromStart
            p["x"] = point.x
            p["y"] = point.y
            p["yaw"] = point.yaw
            p["vx"] = point.vx
            p["vy"] = point.vy
            p["vyaw"] = point.vyaw
            path_p.append(p)

        payload = {
            "topic": RTC_TOPIC["SPORT_MOD"],
            "options": {
                "parameter": path_p,
                "api_id": 1018
            },
            "expect_reply": False,
            "update_switcher_mode": False,
            "post_hook": None,
            "additional_wait": 0
        }
        super().__init__(payload)

# 1019
class ContinuousGait(Command):
    """
    Continuous walk
    flag: Set true to open continuous walk, and false to close continuous walk
    After starting a continuous walk, the robot dog will keep stepping, 
    even if the current speed is 0
    """
    def __init__(self, flag: int):
        payload = {
            "topic": RTC_TOPIC["SPORT_MOD"],
            "options": {
                "parameter": {"data": flag},
                "api_id": 1019
            },
            "expect_reply": False,
            "update_switcher_mode": False,
            "post_hook": None,
            "additional_wait": 0
        }
        super().__init__(payload)

# 1020
class Content(Command):
    def __init__(self):
        payload = {
            "topic": RTC_TOPIC["SPORT_MOD"],
            "options": {
                "parameter": "",
                "api_id": 1020
            },
            "expect_reply": False,
            "update_switcher_mode": False,
            "post_hook": None,
            "additional_wait": 0
        }
        super().__init__(payload, associated_states=[DogState.BUSY])

# 1021
class Wallow(Command):
    def __init__(self):
        payload = {
            "topic": RTC_TOPIC["SPORT_MOD"],
            "options": {
                "parameter": "",
                "api_id": 1021
            },
            "expect_reply": False,
            "update_switcher_mode": False,
            "post_hook": None,
            "additional_wait": 0
        }
        super().__init__(payload, associated_states=[DogState.BUSY])

# 1022
class Dance1(Command):
    def __init__(self):
        payload = {
            "topic": RTC_TOPIC["SPORT_MOD"],
            "options": {
                "parameter": "",
                "api_id": 1022
            },
            "expect_reply": False,
            "update_switcher_mode": False,
            "post_hook": None,
            "additional_wait": 0
        }
        super().__init__(payload, associated_states=[DogState.BUSY])

# 1023
class Dance2(Command):
    def __init__(self):
        payload = {
            "topic": RTC_TOPIC["SPORT_MOD"],
            "options": {
                "parameter": "",
                "api_id": 1023
            },
            "expect_reply": False,
            "update_switcher_mode": False,
            "post_hook": None,
            "additional_wait": 0
        }
        super().__init__(payload, associated_states=[DogState.BUSY])

# 1024
class GetBodyHeight(Command):
    def __init__(self):
        payload = {
            "topic": RTC_TOPIC["SPORT_MOD"],
            "options": {
                "parameter": "",
                "api_id": 1024
            },
            "expect_reply": True,
            "update_switcher_mode": False,
            "post_hook": None,
            "additional_wait": 0
        }
        super().__init__(payload)

# 1025
class GetFootRaiseHeight(Command):
    def __init__(self):
        payload = {
            "topic": RTC_TOPIC["SPORT_MOD"],
            "options": {
                "parameter": "",
                "api_id": 1025
            },
            "expect_reply": True,
            "update_switcher_mode": False,
            "post_hook": None,
            "additional_wait": 0
        }
        super().__init__(payload)

# 1026
class GetSpeedLevel(Command):
    def __init__(self):
        payload = {
            "topic": RTC_TOPIC["SPORT_MOD"],
            "options": {
                "parameter": "",
                "api_id": 1026
            },
            "expect_reply": True,
            "update_switcher_mode": False,
            "post_hook": None,
            "additional_wait": 0
        }
        super().__init__(payload)

# 1027
class SwitchJoystick(Command):
    def __init__(self):
        payload = {
            "topic": RTC_TOPIC["SPORT_MOD"],
            "options": {
                "parameter": "",
                "api_id": 1027
            },
            "expect_reply": False,
            "update_switcher_mode": False,
            "post_hook": None,
            "additional_wait": 0
        }
        super().__init__(payload)

# 1028
class Pose(Command):
    def __init__(self, flag: bool = True):
        payload = {
            "topic": RTC_TOPIC["SPORT_MOD"],
            "options": {
                "parameter": {"data": flag},
                "api_id": 1028
            },
            "expect_reply": False,
            "update_switcher_mode": False,
            "post_hook": None,
            "additional_wait": 0
        }
        super().__init__(payload, associated_states=[DogState.STANDING], toggle = True)

# 1029
class Scrape(Command):
    def __init__(self):
        payload = {
            "topic": RTC_TOPIC["SPORT_MOD"],
            "options": {
                "parameter": "",
                "api_id": 1029
            },
            "expect_reply": False,
            "update_switcher_mode": False,
            "post_hook": None,
            "additional_wait": 0
        }
        super().__init__(payload, associated_states=[DogState.BUSY])

# 1030
class FrontFlip(Command):
    def __init__(self):
        payload = {
            "topic": RTC_TOPIC["SPORT_MOD"],
            "options": {
                "parameter": "",
                "api_id": 1030
            },
            "expect_reply": False,
            "update_switcher_mode": False,
            "post_hook": None,
            "additional_wait": 0
        }
        super().__init__(payload)

# 1031
class FrontJump(Command):
    def __init__(self):
        payload = {
            "topic": RTC_TOPIC["SPORT_MOD"],
            "options": {
                "parameter": "",
                "api_id": 1031
            },
            "expect_reply": False,
            "update_switcher_mode": False,
            "post_hook": None,
            "additional_wait": 0
        }
        super().__init__(payload, associated_states=[DogState.JUMP])

# 1032
class FrontPounce(Command):
    def __init__(self):
        payload = {
            "topic": RTC_TOPIC["SPORT_MOD"],
            "options": {
                "parameter": "",
                "api_id": 1032
            },
            "expect_reply": False,
            "update_switcher_mode": False,
            "post_hook": None,
            "additional_wait": 0
        }
        super().__init__(payload, associated_states=[DogState.POUNCE])

# 1033
class WiggleHips(Command):
    def __init__(self):
        payload = {
            "topic": RTC_TOPIC["SPORT_MOD"],
            "options": {
                "parameter": "",
                "api_id": 1033
            },
            "expect_reply": False,
            "update_switcher_mode": False,
            "post_hook": None,
            "additional_wait": 0
        }
        super().__init__(payload, associated_states=[DogState.BUSY])

# 1035
class EconomicGait(Command):
    def __init__(self):
        payload = {
            "topic": RTC_TOPIC["SPORT_MOD"],
            "options": {
                "parameter": "",
                "api_id": 1035
            },
            "expect_reply": False,
            "update_switcher_mode": False,
            "post_hook": None,
            "additional_wait": 0
        }
        super().__init__(payload)

# 1036
class Heart(Command):
    def __init__(self):
        payload = {
            "topic": RTC_TOPIC["SPORT_MOD"],
            "options": {
                "parameter": "",
                "api_id": 1036
            },
            "expect_reply": False,
            "update_switcher_mode": False,
            "post_hook": None,
            "additional_wait": 0
        }
        super().__init__(payload, associated_states=[DogState.BUSY])

# 1037
# NOT AVAILABLE
class Dance3(Command):
    def __init__(self):
        payload = {
            "topic": RTC_TOPIC["SPORT_MOD"],
            "options": {
                "parameter": "",
                "api_id": 1037
            },
            "expect_reply": False,
            "update_switcher_mode": False,
            "post_hook": None,
            "additional_wait": 0
        }
        super().__init__(payload)

# 1039
# Handstand
class StandOut(Command):
    def __init__(self, flag: bool = True):
        payload = {
            "topic": RTC_TOPIC["SPORT_MOD"],
            "options": {
                "parameter": {"data": flag},
                "api_id": 1039
            },
            "expect_reply": False,
            "update_switcher_mode": False,
            "post_hook": None,
            "additional_wait": 0
        }
        super().__init__(payload, associated_states = [DogState.MOVING], toggle=True)

# 1042
class LeftFlip(Command):
    def __init__(self):
        payload = {
            "topic": RTC_TOPIC["SPORT_MOD"],
            "options": {
                "parameter": {"data": True},
                "api_id": 1042
            },
            "expect_reply": False,
            "update_switcher_mode": False,
            "post_hook": None,
            "additional_wait": 0
        }
        super().__init__(payload)

# 1043
class RightFlip(Command):
    def __init__(self):
        payload = {
            "topic": RTC_TOPIC["SPORT_MOD"],
            "options": {
                "parameter": {"data": True},
                "api_id": 1043
            },
            "expect_reply": False,
            "update_switcher_mode": False,
            "post_hook": None,
            "additional_wait": 0
        }
        super().__init__(payload)

# 1044
class BackFlip(Command):
    def __init__(self):
        payload = {
            "topic": RTC_TOPIC["SPORT_MOD"],
            "options": {
                "parameter": {"data": True},
                "api_id": 1044
            },
            "expect_reply": False,
            "update_switcher_mode": False,
            "post_hook": None,
            "additional_wait": 0
        }
        super().__init__(payload)

# 1045 - LeadFollow
class FreeWalk(Command):
    def __init__(self, flag: bool = True):
        payload = {
            "topic": RTC_TOPIC["SPORT_MOD"],
            "options": {
                "parameter": {"data": flag},
                "api_id": 1045
            },
            "expect_reply": False,
            "update_switcher_mode": False,
            "post_hook": None,
            "additional_wait": 0
        }
        super().__init__(payload, associated_states=[DogState.AI_AGILE])

# 1046
class FreeBound(Command):
    def __init__(self, flag: bool = True):
        payload = {
            "topic": RTC_TOPIC["SPORT_MOD"],
            "options": {
                "parameter": {"data": flag},
                "api_id": 1046
            },
            "expect_reply": False,
            "update_switcher_mode": False,
            "post_hook": None,
            "additional_wait": 0
        }
        super().__init__(payload, associated_states=[DogState.AI_FREEBOUND], toggle=True)

# 1047
class FreeJump(Command):
    def __init__(self, flag: bool = True):
        payload = {
            "topic": RTC_TOPIC["SPORT_MOD"],
            "options": {
                "parameter": {"data": flag},
                "api_id": 1047
            },
            "expect_reply": False,
            "update_switcher_mode": False,
            "post_hook": None,
            "additional_wait": 0
        }
        super().__init__(payload, associated_states=[DogState.AI_FREEJUMP], toggle=True)

# 1048
class FreeAvoid(Command):
    def __init__(self, flag: bool = True):
        payload = {
            "topic": RTC_TOPIC["SPORT_MOD"],
            "options": {
                "parameter": {"data": flag},
                "api_id": 1048
            },
            "expect_reply": False,
            "update_switcher_mode": False,
            "post_hook": None,
            "additional_wait": 0
        }
        super().__init__(payload, associated_states=[DogState.AI_FREEAVOID], toggle=True)

# 1049
class WalkStair(Command):
    def __init__(self, flag: bool = True):
        payload = {
            "topic": RTC_TOPIC["SPORT_MOD"],
            "options": {
                "parameter": {"data": flag},
                "api_id": 1049
            },
            "expect_reply": False,
            "update_switcher_mode": False,
            "post_hook": None,
            "additional_wait": 0
        }
        super().__init__(payload, associated_states=[DogState.AI_WALKSTAIR], toggle=True)

# 1050 - Standup
class WalkUpright(Command):
    def __init__(self, flag: bool = True):
        payload = {
            "topic": RTC_TOPIC["SPORT_MOD"],
            "options": {
                "parameter": {"data": flag},
                "api_id": 1050
            },
            "expect_reply": False,
            "update_switcher_mode": False,
            "post_hook": None,
            "additional_wait": 0
        }
        super().__init__(payload, associated_states=[DogState.AI_WALKUPRIGHT], toggle=True)

# 1051
# CrossWalk (crosstep before)
class CrossWalk(Command):
    def __init__(self, flag: bool = True):
        payload = {
            "topic": RTC_TOPIC["SPORT_MOD"],
            "options": {
                "parameter": {"data": flag},
                "api_id": 1051
            },
            "expect_reply": False,
            "update_switcher_mode": False,
            "post_hook": None,
            "additional_wait": 0
        }
        super().__init__(payload, associated_states=[DogState.AI_CROSSSTEP], toggle=True)

# 1303
class OneSidedStep(Command):
    def __init__(self, flag: bool = True):
        payload = {
            "topic": RTC_TOPIC["SPORT_MOD"],
            "options": {
                "parameter": {},
                "api_id": 1303
            },
            "expect_reply": False,
            "update_switcher_mode": False,
            "post_hook": None,
            "additional_wait": 0
        }
        super().__init__(payload)

# 1305
# TODO - Data needed?
# Not available?
class MoonWalk(Command):
    def __init__(self, flag: bool=True):
        payload = {
            "topic": RTC_TOPIC["SPORT_MOD"],
            "options": {
                "parameter": {},
                "api_id": 1305
            },
            "expect_reply": False,
            "update_switcher_mode": False,
            "post_hook": None,
            "additional_wait": 0
        }
        super().__init__(payload)

## Motion Switcher
#1002
class GetMotionSwitcherStatus(Command):
    def __init__(self):
        payload = {
            "topic": RTC_TOPIC["MOTION_SWITCHER"],
            "options": {
                "parameter": "",
                "api_id": 1001
            },
            "expect_reply": True,
            "update_switcher_mode": True,
            "post_hook": None,
            "additional_wait": 0
        }
        super().__init__(payload)


# Normal #1002
class SetMotionSwitcherNormal(Command):
    def __init__(self):
        payload = {
            "topic": RTC_TOPIC["MOTION_SWITCHER"],
            "options": {
                "parameter": {"name": "normal"},
                "api_id": 1002
            },
            "expect_reply": False,
            "update_switcher_mode": False,
            "post_hook": GetMotionSwitcherStatus(),
            "additional_wait": 5
        }
        super().__init__(payload)

# AI #1002
class SetMotionSwitcherAI(Command):
    def __init__(self):
        payload = {
            "topic": RTC_TOPIC["MOTION_SWITCHER"],
            "options": {
                "parameter": {"name": "ai"},
                "api_id": 1002
            },
            "expect_reply": False,
            "update_switcher_mode": False,
            "post_hook": GetMotionSwitcherStatus(),
            "additional_wait": 5
        }
        super().__init__(payload)

# AI #1002
class SetMotionSwitcherAdvanced(Command):
    def __init__(self):
        payload = {
            "topic": RTC_TOPIC["MOTION_SWITCHER"],
            "options": {
                "parameter": {"name": "advanced"},
                "api_id": 1002
            },
            "expect_reply": False,
            "update_switcher_mode": False,
            "post_hook": GetMotionSwitcherStatus(),
            "additional_wait": 5
        }
        super().__init__(payload)

## VUI
class GetBrightness(Command):
    def __init__(self):
        payload = {
            "topic": RTC_TOPIC["VUI"],
            "options": {
                "parameter": "",
                "api_id": 1006
            },
            "expect_reply": True,
            "update_switcher_mode": False,
            "post_hook": None,
            "additional_wait": 0
        }
        super().__init__(payload)

class SetBrightness(Command):
    def __init__(self, brightness, value_range: None):
        """
            Brightness from 0 to 10.
            If value_range is not none, we assume they are 
            passing us a scale to map the values on.
        """
        if value_range is not None: 
            brightness = map_range(brightness, value_range[0], value_range[1], 0, 10)
        payload = {
            "topic": RTC_TOPIC["VUI"],
            "options": {
                "parameter": {"brightness": brightness},
                "api_id": 1005
            },
            "expect_reply": False,
            "update_switcher_mode": False,
            "post_hook": None,
            "additional_wait": 0
        }
        super().__init__(payload)

class SetLEDColor(Command):
    def __init__(self, color, time: None, flash_cycle: None):
        """
            VUI_COLOR options:
            - 'white'
            - 'red'
            - 'yellow'
            - 'blue'
            - 'green'
            - 'cyan'
            - 'purple'
            TODO - CHECK TIME parameter
            # flash_cycle is between 499 and time*1000
        """
        parameter = {"color": color}

        if time is not None:
            parameter["time"] = time
        if flash_cycle is not None:
            parameter["flash_cycle"] = flash_cycle

        payload = {
            "topic": RTC_TOPIC["VUI"],
            "options": {
                "parameter": parameter,
                "api_id": 1007
            },
            "expect_reply": False,
            "update_switcher_mode": False,
            "post_hook": None,
            "additional_wait": 0.5
        }
        super().__init__(payload)

class GetVolume(Command):
    def __init__(self):
        payload = {
            "topic": RTC_TOPIC["VUI"],
            "options": {
                "parameter": "",
                "api_id": 1004
            },
            "expect_reply": True,
            "update_switcher_mode": False,
            "post_hook": None,
            "additional_wait": 0
        }
        super().__init__(payload)

class SetVolume(Command):
    def __init__(self, volume, value_range: None):
        """
            Volume from 0 to 10
            If value_range is not none, we assume they are 
            passing us a scale to map the values on.
        """
        if value_range is not None: 
            volume = map_range(volume, value_range[0], value_range[1], 0, 10)
        payload = {
            "topic": RTC_TOPIC["VUI"],
            "options": {
                "parameter": {"volume": volume},
                "api_id": 1003
            },
            "expect_reply": False,
            "update_switcher_mode": False,
            "post_hook": None,
            "additional_wait": 0
        }
        super().__init__(payload)

## Obstacle avoidance
class GetObstacleAvoidance(Command):
    def __init__(self, flag: bool = False):
        payload = {
            "topic": RTC_TOPIC["OBSTACLES_AVOID"],
            "options": {
                "parameter": "",
                "api_id": 1002
            },
            "expect_reply": False,
            "update_switcher_mode": False,
            "post_hook": None,
            "additional_wait": 0
        }
        super().__init__(payload, toggle=True)
        
class SetObstacleAvoidance(Command):
    def __init__(self, flag: bool = False):
        payload = {
            "topic": RTC_TOPIC["OBSTACLES_AVOID"],
            "options": {
                "parameter": {"enable": flag},
                "api_id": 1001
            },
            "expect_reply": False,
            "update_switcher_mode": False,
            "post_hook": GetObstacleAvoidance(),
            "additional_wait": 0
        }
        super().__init__(payload, toggle=True)

CMD_W_DATA = [
    'Pose',
]