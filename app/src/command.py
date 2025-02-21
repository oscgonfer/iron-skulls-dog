import json
from go2_webrtc_driver.constants import *

class Command:
    def __init__(self, payload):
        self.topic = payload["topic"]
        self.options = payload["options"]

    def as_dict(self):
        return {
            'topic': self.topic,
            'options': self.options
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
            }
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
            }
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
            }
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
            }
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
            }
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
            }
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
            }
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
            }
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
            }
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
            }
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
            }
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
            }
        }
        super().__init__(payload)

# 1013
class BodyHeight(Command):
    def __init__(self, height: float):
        payload = {
            "topic": RTC_TOPIC["SPORT_MOD"],
            "options": {
                "parameter": {"data": height},
                "api_id": 1013
            }
        }
        super().__init__(payload)

# 1014
class FootRaiseHeight(Command):
    def __init__(self, height: float):
        payload = {
            "topic": RTC_TOPIC["SPORT_MOD"],
            "options": {
                "parameter": {"data": height},
                "api_id": 1014
            }
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
            }
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
            }
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
            }
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
            }
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
            }
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
            }
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
            }
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
            }
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
            }
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
            }
        }
        expect_reply = True
        super().__init__(payload)

# 1026
class GetSpeedLevel(Command):
    def __init__(self):
        payload = {
            "topic": RTC_TOPIC["SPORT_MOD"],
            "options": {
                "parameter": "",
                "api_id": 1026
            }
        }
        expect_reply = True
        super().__init__(payload)

# 1027
class SwitchJoystick(Command):
    def __init__(self):
        payload = {
            "topic": RTC_TOPIC["SPORT_MOD"],
            "options": {
                "parameter": "",
                "api_id": 1027
            }
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
            }
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
            }
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
            }
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
            }
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
            }
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
            }
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
            }
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
            }
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
            }
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
            }
        }
        super().__init__(payload)

# 1045
class FreeWalk(Command):
    def __init__(self, flag: bool):
        payload = {
            "topic": RTC_TOPIC["SPORT_MOD"],
            "options": {
                "parameter": {"data": flag},
                "api_id": 1045
            }
        }
        super().__init__(payload)

# 1046
class FreeBound(Command):
    def __init__(self, flag: bool):
        payload = {
            "topic": RTC_TOPIC["SPORT_MOD"],
            "options": {
                "parameter": {"data": flag},
                "api_id": 1046
            }
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
            }
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
            }
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
            }
        }
        super().__init__(payload)

# 1050
class WalkUpright(Command):
    def __init__(self, flag: bool):
        payload = {
            "topic": RTC_TOPIC["SPORT_MOD"],
            "options": {
                "parameter": {"data": flag},
                "api_id": 1050
            }
        }
        super().__init__(payload)

# 1051
class CrossStep(Command):
    def __init__(self, flag: bool):
        payload = {
            "topic": RTC_TOPIC["SPORT_MOD"],
            "options": {
                "parameter": {"data": flag},
                "api_id": 1051
            }
        }
        super().__init__(payload)