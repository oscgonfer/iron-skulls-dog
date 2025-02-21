from config import *
from tools import *
import asyncio
import datetime
from command import *
from enum import Enum
import os

class CaptureStatus(Enum):
    null = 0
    running = 1
    paused = 2
    stopped = 3
    stored = 4

class Capture:
    def __init__(self, name):
        self.name = name
        self.start_time = None
        self.end_time = None
        self.status = CaptureStatus.null
        self.commands = []
        self.file = os.path.join(CAPTURE_PATH, f'{name}.cap')

    def start(self):
        payload = {
            "topic": None,
            "options": None
        }
        self.add(payload, None)
        self.start_time = datetime.datetime.now()
        self.status = CaptureStatus.running

    def add(self, command, osc_topic):
        if self.status != CaptureStatus.running: return
        timedelta = datetime.datetime.now()-self.start_time
        self.commands.append(
            {
                'timestamp': {
                    'seconds': timedelta.seconds,
                    'microseconds': timedelta.microseconds
                    },
                'command': command.to_json(),
                'osc_topic': osc_topic
            }
        )

    def pause(self):
        self.status = CaptureStatus.paused

    def stop(self):
        self.status = CaptureStatus.stopped
        self.end_time = datetime.datetime.now()

    def store(self):
        if self.status != CaptureStatus.stopped: return
        with open (self.file, 'w') as file:
            json.dump(self.commands, file)

        self.status = CaptureStatus.stored

    @property
    def duration(self):
        return self.end_time - self.start_time

class OscHandler:
    def __init__(self, dog):
        self.dog = dog
        self.capture = None

    def start_capture(self, name):
        self.capture = Capture(name)
        self.capture.start()

    def stop_capture(self):
        self.capture.stop()

    def pause_capture(self):
        self.capture.pause()

    def store_capture(self):
        self.capture.store()

    async def handle_sport_command(self, address, *args):
        # Sport = Async
        payload = json.loads(args[0])
        std_out(f"{address}: {args}")
        std_out(f"Command Payload: {payload}")
        std_out(f"Waiting for lock...")

        command = Command(payload)

        if self.capture is not None:
            self.capture.add(command, SPORT_TOPIC)

        await self.dog.send_async_command(command)

    def handle_movement_command(self, address, *args):
        # Movement = direct displacement on the space
        payload = json.loads(args[0])

        std_out(f"{address}: {args}")
        std_out(f"Movement Payload: {payload}")

        command = Command(payload)

        if self.capture is not None:
            self.capture.add(command, MOVE_TOPIC)

        self.dog.send_command(command)

    def handle_capture_command(self, address, *args):
        payload = json.loads(args[0])

        std_out(f"{address}: {args}")
        std_out(f"Capture Payload: {payload}")

        if payload["action"] == 'START':
            self.start_capture(payload["name"])
        elif payload["action"] == "PAUSE":
            self.pause_capture()
        elif payload["action"] == 'STOP':
            self.stop_capture()
        elif payload["action"] == "STORE":
            self.store_capture()
