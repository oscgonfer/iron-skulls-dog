from config import *
from tools import *
import asyncio
import datetime
from command import *
from enum import Enum
import os
import json
import shutil
from media_track import Track

class CaptureStatus(Enum):
    null = 0
    running = 1
    paused = 2
    stopped = 3
    stored = 4

class CaptureAction(Enum):
    START = 0
    PAUSE = 1
    STOP = 2
    STORE = 3
    DISCARD = 4 # TODO Add something to discard the recording?

class Capture:
    def __init__(self, name, short_name = '', description = '', start_at = None, end_at = None, track: Track = Track()):
        self.name = name
        self.short_name = short_name
        self.description = description
        self.filename = f'{name}.cap'
        self.start_time = None # In ms
        self.end_time = None # In ms
        self.start_at = start_at
        self.end_at = end_at
        self.status: CaptureStatus = CaptureStatus.null

        self.commands = []
        file_path = os.path.dirname(os.path.realpath(__file__))
        self.file = os.path.abspath(os.path.join(file_path, CAPTURE_PATH, self.filename))
        self.track = track

        self.metadata = {
            'short_name': self.short_name,
            'filename': self.filename,
            'description': self.description,
            'track': self.track.as_dict()
        }

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
        timedelta = datetime.datetime.now() - self.start_time

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
        self.store()
    
    def cancel(self):
        self.status = CaptureStatus.stopped

    def store(self):
        if self.status != CaptureStatus.stopped: 
            std_out('Need to stop capture first')
            return
        
        # TODO Make backup in case it exists
        if os.path.exists(self.file):
            std_out('File exists, moving to _backup/')
            shutil.move(self.file, self.file.replace(self.filename, os.path.join('_backup',  self.filename.replace('.cap', '.cap.bak'))))
        with open (self.file, 'w') as file:
            json.dump({'metadata': self.metadata, 'commands': self.commands}, file)

        self.status = CaptureStatus.stored

    @property
    def duration(self):
        return self.end_time - self.start_time

class CaptureCommand():
    def __init__(self, action: CaptureAction, name: str = None):
        self.action = action
        self.name = name

    def as_dict(self):
        return {
            "action": self.action.name,
            "name": self.name
        }

    def to_json(self):
        return json.dumps(self.as_dict())