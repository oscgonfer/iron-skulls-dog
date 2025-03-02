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
        empty_cmd = Command(payload)
        self.add(payload, None)
        self.start_time = datetime.datetime.now()
        self.status = CaptureStatus.running

    def add(self, command, topic):
        if self.status != CaptureStatus.running: return
        timedelta = datetime.datetime.now()-self.start_time

        self.commands.append(
            {
                'timestamp': {
                    'seconds': timedelta.seconds,
                    'microseconds': timedelta.microseconds
                    },
                'command': command.to_json(),
                'mqtt_topic': topic
            }
        )

    def pause(self):
        self.status = CaptureStatus.paused

    def stop(self):
        self.status = CaptureStatus.stopped
        self.end_time = datetime.datetime.now()

    def store(self):
        if self.status != CaptureStatus.stopped: 
            std_out('Need to stop capture first')
            return
        with open (self.file, 'w') as file:
            json.dump(self.commands, file)

        self.status = CaptureStatus.stored

    @property
    def duration(self):
        return self.end_time - self.start_time

