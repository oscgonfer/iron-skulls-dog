import json
from go2_webrtc_driver.constants import *
from tools import map_range

class Command:
    def __init__(self, payload):
        self.topic = payload["topic"]
        self.options = payload["options"]
        self.expect_reply = payload["expect_reply"] if "expect_reply" in payload else False
        self.update_switcher_mode = payload["update_switcher_mode"] if "update_switcher_mode" in payload else False
        self.post_hook = payload["post_hook"] if "post_hook" in payload else None
        self.additional_wait = payload["additional_wait"] if "additional_wait" in payload else 0

    def as_dict(self):
        return {
            'topic': self.topic,
            'options': self.options,
            'expect_reply': self.expect_reply,
            'update_switcher_mode': self.update_switcher_mode,
            'post_hook': self.post_hook.as_dict() if self.post_hook is not None else None,
            'additional_wait': self.additional_wait,
        }

    def to_json(self):
        return json.dumps(self.as_dict())

# 1001
class Damp(Command):
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
        super().__init__(payload)

# 1003
class StopMove(Command):
    def __init__(self):
        payload = {
            "topic": RTC_TOPIC["SPORT_MOD"],
            "options": {
                "parameter": "",
                "api_id": 1003
            },
            "expect_reply": False,
            "update_switcher_mode": False,
            "post_hook": None,
            "additional_wait": 0
        }
        super().__init__(payload)

# 1004
class StandUp(Command):
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
        super().__init__(payload)

# 1005
class StandDown(Command):
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
        super().__init__(payload)

# 1006
class RecoveryStand(Command):
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
        super().__init__(payload)

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
class SwitchGait(Command):
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
    def __init__(self, level: float):
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
        super().__init__(payload)

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
        super().__init__(payload)

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
        super().__init__(payload)

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
        super().__init__(payload)

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
        super().__init__(payload)

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
        super().__init__(payload)

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
    def __init__(self, flag: bool):
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
        super().__init__(payload)

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
        super().__init__(payload)

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
        super().__init__(payload)

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
        super().__init__(payload)

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
        super().__init__(payload)

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
        super().__init__(payload)

# 1039
# Handstand
class StandOut(Command):
    def __init__(self, flag):
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
        super().__init__(payload)

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
    def __init__(self, flag: bool):
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
        super().__init__(payload)

# 1046
# TODO Same as 1304?
class FreeBound(Command):
    def __init__(self, flag: bool):
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
        super().__init__(payload)

# 1047
class FreeJump(Command):
    def __init__(self, flag: bool):
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
        super().__init__(payload)

# 1048
class FreeAvoid(Command):
    def __init__(self, flag: bool):
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
        super().__init__(payload)

# 1049
class WalkStair(Command):
    def __init__(self, flag: bool):
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
        super().__init__(payload)

# 1050 - Standup
class WalkUpright(Command):
    def __init__(self, flag: bool):
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
        super().__init__(payload)

# 1051
# TODO - 1302 by legion
# TODO - CrossWalk
class CrossStep(Command):
    def __init__(self, flag: bool):
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
        super().__init__(payload)

# 1301
# TODO - Handstand - same as 1039?
# TODO - Data needed?
class Handstand(Command):
    def __init__(self, flag: bool):
        payload = {
            "topic": RTC_TOPIC["SPORT_MOD"],
            "options": {
                "parameter": {"data": flag},
                "api_id": 1301
            },
            "expect_reply": False,
            "update_switcher_mode": False,
            "post_hook": None,
            "additional_wait": 0
        }
        super().__init__(payload)

# 1302
# TODO - Same as 1051?
# TODO - Data needed?
class CrossStep(Command):
    def __init__(self, flag: bool):
        payload = {
            "topic": RTC_TOPIC["SPORT_MOD"],
            "options": {
                "parameter": {"data": flag},
                "api_id": 1302
            },
            "expect_reply": False,
            "update_switcher_mode": False,
            "post_hook": None,
            "additional_wait": 0
        }
        super().__init__(payload)

# 1303
# TODO - Data needed?
class OneSidedStep(Command):
    def __init__(self, flag: bool):
        payload = {
            "topic": RTC_TOPIC["SPORT_MOD"],
            "options": {
                "parameter": {"data": flag},
                "api_id": 1303
            },
            "expect_reply": False,
            "update_switcher_mode": False,
            "post_hook": None,
            "additional_wait": 0
        }
        super().__init__(payload)

# 1304 # Same as 1046?
# TODO - Data needed?
class Bound(Command):
    def __init__(self, flag: bool):
        payload = {
            "topic": RTC_TOPIC["SPORT_MOD"],
            "options": {
                "parameter": {"data": flag},
                "api_id": 1304
            },
            "expect_reply": False,
            "update_switcher_mode": False,
            "post_hook": None,
            "additional_wait": 0
        }
        super().__init__(payload)

# 1305
# TODO - Data needed?
class MoonWalk(Command):
    def __init__(self, flag: bool):
        payload = {
            "topic": RTC_TOPIC["SPORT_MOD"],
            "options": {
                "parameter": {"data": flag},
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
            "post_hook": GetBrightness(),
            "additional_wait": 0.5
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
            "post_hook": GetVolume(),
            "additional_wait": 0.5
        }
        super().__init__(payload)