import asyncio
from capture import Capture
from tools import std_out
import json
from command import Command, AudioCommand, DogState
from config import *

class CommandHandler:
    def __init__(self, dog):
        self.dog = dog
        self.capture = None
        self.enabled = True

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
                if source.value in INCOMING_TOPICS:
                    
                    if source.value == RESUME_TOPIC:
                        std_out ('Resume')
                        self.enabled = True

                    if INCOMING_TOPICS[source.value] == 'async':
                        await self.handle_async_command(_payload)
                    elif INCOMING_TOPICS[source.value] == 'sync':
                        self.handle_command(_payload)
                    elif INCOMING_TOPICS[source.value] == 'capture':
                        self.handle_capture_command(_payload)
                    elif INCOMING_TOPICS[source.value] == 'audio':
                        await self.handle_audio_command(_payload)
                    else:
                        std_out(f'Unknown handler command')
                    
                    if source.value == STOP_TOPIC:
                        std_out ('Disabled')
                        self.enabled = False
                else:
                    std_out(f'Unknown source {source.value}')

    async def handle_async_command(self, payload):
        # Sport = Async
        if self.enabled:
            std_out(f"Command Payload: {payload}")
            std_out(f"DogState: {self.dog.mode}")
            command = Command(payload)

            if self.capture is not None:
                self.capture.add(command, SPORT_TOPIC)

            # Avoid sending async commands if we can mess up
            # Take into account that in handstand mode we have the same as in moving...
            if (self.dog.mode == DogState.MOVING and self.dog.motion_switcher == "normal") or self.dog.mode == DogState.STANDING or self.dog.mode == DogState.BUSY:
                std_out("Ignoring command")

            else:
                # TODO - Try this?
                # try:
                #     # Add timeout to async tasks
                #     await asyncio.wait_for(self.dog.send_async_command(command), timeout = 6)
                # except:
                #     std_out("Timed out command, releasing")
                #     pass
                await self.dog.send_async_command(command)


    async def handle_audio_command(self, payload):
        # Audio
        if self.enabled:
            std_out(f"Audio Payload: {payload}")
            command = AudioCommand(payload)

            if self.capture is not None:
                self.capture.add(command, AUDIO_TOPIC)

            await self.dog.send_audio_command(command)

    def handle_command(self, payload):
        # Movement = direct displacement on the space
        if self.enabled:
            std_out(f"Movement Payload: {payload}")
            command = Command(payload)

            if self.capture is not None:
                self.capture.add(command, MOVE_TOPIC)

            # Avoid sending async commands if we can mess up
            if self.dog.mode == DogState.PRONE or self.dog.mode == DogState.LOCKED or self.dog.mode == DogState.SAVE or self.dog.mode == DogState.BUSY:
                std_out("Ignoring command")
            else:
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