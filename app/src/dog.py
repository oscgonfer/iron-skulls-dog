import asyncio
import websockets
import json

from command import *
from config import *
from tools import *

from go2_webrtc_driver.constants import *

from enum import IntEnum

class DogMode(IntEnum):
    MOVE=1 # Accepts any move command except Euler. Run, stair 1 and 2, walk, endurance
    STANDING=2 # Accepts Euler
    MOVING=3 # Moving with any of run, stair 1 and 2, walk, endurance
    PRONE=5 # Down
    LOCKED=6 # Posture locked, can only go prone
    SAVE=7 # Seems to enter after a bit into this

# TODO Make this stateful
class Dog:
    def __init__(self, conn=None, dry_run=False, broadcast=False, mqtt_handler=None):
        # State
        self.state = {
            'LOW_STATE': None,
            'LF_SPORT_MOD_STATE': None,
            'MULTIPLE_STATE': None
        }
        self._mode = None
        self._motion_switcher = None
        self.conn = conn
        self.lock = asyncio.Lock()
        self.dry_run = dry_run
        self.broadcast = broadcast
        self.mqtt_handler = mqtt_handler

    async def connect(self):
        return await self.conn.connect()

    async def send_async_command(self, command):
        # Reply command, to acquire lock
        std_out(f"Command topic: {command.topic}")
        std_out(f"Command options: {command.options}")
        std_out(f"Command extras: {command.expect_reply, command.update_switcher_mode, command.additional_wait, command.post_hook}")

        std_out(f"Waiting for lock...")
        # TODO this sometimes gets locked??? Why?
        # Check mode to avoid locking??
        # Check state?
        await self.lock.acquire()

        if self.dry_run:
            std_out(f"Sleeping 3s...")
            await asyncio.sleep(3)
        else:
            response = await self.conn.datachannel.pub_sub.publish_request_new(
                topic = command.topic, options = command.options)

            std_out(f"Command Response: {response}")

            if command.expect_reply:
                std_out('Command expects reply')
                if response['data']['header']['status']['code'] == 0:
                    data = json.loads(response['data']['data'])
                    if command.update_switcher_mode:
                        self._motion_switcher = data['name']
                    await self.publish_response(command.topic, response=data)
                else:
                    data = json.dumps({"ERROR": response['data']})
                    await self.publish_response(command.topic, response=data)

        if command.additional_wait:
            std_out('Waiting additional timer')
            await asyncio.sleep(command.additional_wait)

        self.lock.release()

        if command.post_hook:
            std_out('Sending command post_hook')
            cmd = Command(command.post_hook)
            await self.send_async_command(cmd)
        std_out('Done')

    def send_command(self, command):
        # No reply command
        std_out(f"Command topic: {command.topic}")
        std_out(f"Command options: {command.options}")

        if not self.dry_run:
            asyncio.gather(self.conn.datachannel.pub_sub.publish_request_new(
                command.topic, command.options))

    # TODO Add MediaStreamTrack
    # def audio_handler(self, address, *args):
    #     std_out(f"{address}: {args}")
    #     argsd = json.loads(args[0])
    #     std_out (argsd)

    async def publish_response(self, channel, response):
        print (f'{RESPONSE_TOPIC}/{channel}')
        if self.broadcast:
            await self.mqtt_handler.publish(topic=f'{RESPONSE_TOPIC}/{channel}', \
                payload=json.dumps(response))

    async def publish_state(self, channel):
        if self.broadcast:
            await self.mqtt_handler.publish(topic=f'{STATE_TOPIC}/{channel}', \
                payload=json.dumps(self.state))

    def lowstate_callback(self, message):
        current_message = message['data']
        self.state['LOW_STATE'] = current_message
        asyncio.gather(self.publish_state('LOW_STATE'))

    def multiplestate_callback(self, message):
        # TODO For whatever reason this needs to be parsed into json
        current_message = json.loads(message['data'])
        self.state['MULTIPLE_STATE'] = current_message
        asyncio.gather(self.publish_state('MULTIPLE_STATE'))

    def sportstate_callback(self, message):
        current_message = message['data']
        # Update state
        self.state['LF_SPORT_MOD_STATE'] = current_message
        # Update mode
        self._mode = self.state['LF_SPORT_MOD_STATE']['mode']
        asyncio.gather(self.publish_state('LF_SPORT_MOD_STATE'))

    @property
    def mode(self):
        return self._mode

    @property
    def motion_switcher(self):
        return self._motion_switcher

