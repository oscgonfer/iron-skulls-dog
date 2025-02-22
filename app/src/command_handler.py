import asyncio
from capture import Capture
from tools import std_out
import json
from command import Command
from config import *

class CommandHandler:
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

    async def dispatch_commands(self, queue):
        while True:
            source, payload = await queue.get()

            try:
                _payload = json.loads(payload)
            except json.decoder.JSONDecodeError:
                pass
            finally:
                if source == SPORT_TOPIC or source == SWITCHER_TOPIC:
                    await self.handle_async_command(_payload)
                elif source == MOVE_TOPIC:
                    self.handle_command(_payload)
                elif source == CAPTURE_TOPIC:
                    self.handle_capture_command(_payload)
                else:
                    std_out(f'Unknown source {source}')

    async def handle_async_command(self, payload):
        # Sport = Async
        std_out(f"Command Payload: {payload}")
        command = Command(payload)

        if self.capture is not None:
            self.capture.add(command, SPORT_TOPIC)

        await self.dog.send_async_command(command)

    def handle_command(self, payload):
        # Movement = direct displacement on the space
        std_out(f"Movement Payload: {payload}")
        command = Command(payload)

        if self.capture is not None:
            self.capture.add(command, MOVE_TOPIC)

        self.dog.send_command(command)

    def handle_capture_command(self, payload):

        std_out(f"Capture Payload: {payload}")

        if payload["action"] == 'START':
            self.start_capture(payload["name"])
        elif payload["action"] == "PAUSE":
            self.pause_capture()
        elif payload["action"] == 'STOP':
            self.stop_capture()
        elif payload["action"] == "STORE":
            self.store_capture()