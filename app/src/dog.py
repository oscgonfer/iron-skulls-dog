import asyncio
import websockets
import json

# Config
from config import *
from tools import *
from go2_webrtc_driver.constants import *

# TODO Make this stateful
class Dog:
    def __init__(self, conn=None, dry_run = False, broadcast_state = False):
        # State
        self.state = {
            'LOW_STATE': None,
            'LF_SPORT_MOD_STATE': None,
            'MULTIPLE_STATE': None
        }
        self.conn = conn
        self.lock = asyncio.Lock()
        self.dry_run = dry_run
        self.broadcast_state = broadcast_state

    async def connect(self):
        return await self.conn.connect()

    async def send_async_command(self, command):
        # Reply command, to acquire lock
        std_out(f"Command topic: {command.topic}")
        std_out(f"Command options: {command.options}")
        std_out(f"Waiting for lock...")

        await self.lock.acquire()

        if self.dry_run:
            std_out(f"Sleeping 3s...")
            await asyncio.sleep(3)
        else:
            response = await self.conn.datachannel.pub_sub.publish_request_new(
                topic = command.topic, options = command.options)

            std_out(f"Command Response: {response}")
            if command.expect_reply:
                print ("Command reply")
                print (response)
                # TODO put this somewhere to log the response

        self.lock.release()
        std_out(f"Done!")

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

    async def get_motion_switcher_status(self):
        # Get the current motion_switcher status
        response = await self.conn.datachannel.pub_sub.publish_request_new(
            RTC_TOPIC["MOTION_SWITCHER"],
            {"api_id": 1001}
        )

        if response['data']['header']['status']['code'] == 0:
            data = json.loads(response['data']['data'])
            current_motion_switcher_mode = data['name']
            std_out(f"Current motion mode: {current_motion_switcher_mode}")

        return current_motion_switcher_mode

    async def set_motion_switcher_status(self, desired_mode = None):

        current_motion_switcher_mode = await self.get_motion_switcher_status()

        if desired_mode is not None:
            if current_motion_switcher_mode != desired_mode:
                std_out(f"Switching motion mode from {current_motion_switcher_mode} to {desired_mode}...")
                await self.conn.datachannel.pub_sub.publish_request_new(
                    RTC_TOPIC["MOTION_SWITCHER"],
                    {
                        "parameter": {"name": desired_mode}
                    }
                )
                await asyncio.sleep(5)  # Wait while it stands up

        return current_motion_switcher_mode

    async def publish_state(self, channel):
        if self.broadcast_state:
            async with websockets.connect(f'ws://{WS_IP}:{WS_PORT}/pub') as websocket:
                await websocket.send(json.dumps(self.state))

    async def lowstate_callback(self, message):
        current_message = message['data']
        self.state['LOW_STATE'] = current_message
        await self.publish_state('LOW_STATE')

    async def multiplestate_callback(self, message):
        # TODO For whatever reason this needs to be parsed into json
        current_message = json.loads(message['data'])
        self.state['MULTIPLE_STATE'] = current_message
        await self.publish_state('MULTIPLE_STATE')

    async def sportstate_callback(self, message):
        current_message = message['data']
        self.state['LF_SPORT_MOD_STATE'] = current_message
        await self.publish_state('LF_SPORT_MOD_STATE')

