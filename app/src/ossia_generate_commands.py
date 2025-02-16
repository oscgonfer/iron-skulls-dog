from go2_webrtc_driver.constants import *
from config import *
from dog import DogCommand
import argparse
from pythonosc import udp_client

class BaseCommand:
    def __init__(self):
        print (self)

class ParamCommand:
    def __init__(self):
        print (self)

class SpecialCommand(BaseCommand):
    def __init__(self, osc_address, topic = None, name = None, parameter = None):
        if osc_address not in TOPICS:
            std_out("Name not in valid topics")
            return
        self.osc_address = osc_address
        self.topic = topic
        self.name = name
        self.unique_address = self.osc_address + '/' + self.name
        if topic == "SPORT_MOD" or topic == "MOTION_SWITCHER":
            if name not in SPORT_CMD:
                std_out("Name not in valid commands")
                return
            self.api_id = SPORT_CMD[self.name]
            if topic == "MOTION_SWITCHER":
                self.unique_address += parameter["name"]
        elif topic == "VUI":
            if name not in VUI_CMD:
                std_out("Name not in valid commands")
                return
            self.api_id = VUI_CMD[self.name]
        self.parameter = parameter
        self.payload = None

        self.make_payload()

    def to_json(self):
        self.make_payload()
        return json.dumps(self.payload)

    def make_payload(self):
        payload = {
            "topic": "",
            "api_id": self.api_id,
            "parameter": {}
        }

        if self.topic in RTC_TOPIC:
            payload["topic"] = RTC_TOPIC[self.topic]
        else:
            std_out("RTC topic not valid")

        # This is confusing but oh well
        if self.parameter is not None:
            payload["parameter"] = self.parameter #{"name": args.param_name}

        self.payload = payload
        return self.payload

def generate_commands():
    sports_commands = [
        DogCommand(
            osc_address=CMD_TOPIC,
            topic="SPORT_MOD", name=cmd
        ) for cmd in SPORT_CMD if cmd != "Move"
    ]

    motion_switcher_commands = [
        DogCommand(
            osc_address=SWITCHER_TOPIC,
            topic="MOTION_SWITCHER", name="BalanceStand",
            parameter={
                "name": name
            }
        ) for name in ["normal", "ai"]
    ]

    vui_commands = [
        DogCommand(
            osc_address=VUI_TOPIC,
            topic="VUI", name="Brightness",
            parameter={
                "brightness": 5
            }
        ),
        DogCommand(
            osc_address=VUI_TOPIC,
            topic="VUI", name="Color",
            parameter={
                "color": VUI_COLOR.PURPLE,
                "time": 5,
                "flash_cycle": 1000
            }
        ),
        DogCommand(
            osc_address=VUI_TOPIC,
            topic="VUI", name="SetVolume",
            parameter={
                "volume": 5
            }
        )
    ]

    return sports_commands + motion_switcher_commands + vui_commands

if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--dry-run", default=False, dest='dry_run', action='store_true', help="Dry run mode"
    )

    args = parser.parse_args()
    for command in generate_commands():
        print (command.unique_address, command.to_json())

        if not args.dry_run:
            client = udp_client.SimpleUDPClient(SERVER_IP, OSSIA_PORT)
            client.send_message(command.unique_address, command.to_json())
