import asyncio
import json

# Config
from config import *
from tools import *
from go2_webrtc_driver.constants import *

# TODO Make this stateful
class Dog:
    def __init__(self, conn=None):
        self.state = {
            'LOW_STATE': None,
            'LF_SPORT_MOD_STATE': None,
            'MULTIPLE_STATE': None
        }
        self.conn = conn
        self.lock = asyncio.Lock()

    async def connect(self):
        return await self.conn.connect()

    async def command_handler(self, address, *args):
        payload = json.loads(args[0])
        std_out(f"{address}: {args}")
        std_out(f"Command Payload: {payload}")
        std_out(f"Waiting for lock...")

        await self.lock.acquire()

        if DRY_RUN:
            std_out(f"Sleeping 3s...")
            await asyncio.sleep(3)
            std_out(f"Done!")
        else:
            response = await self.conn.datachannel.pub_sub.publish_request_new(
                payload["topic"],
                {
                    "api_id": payload["api_id"],
                    "parameter": payload["parameter"]
                }
            )

            std_out(f"Command Response: {response}")

        self.lock.release()

    def movement_handler(self, address, *args):
        payload = json.loads(args[0])

        std_out(f"{address}: {args}")
        std_out(f"Movement Payload: {payload}")
        if not DRY_RUN:
            asyncio.gather(self.conn.datachannel.pub_sub.publish_request_new(
                payload["topic"],
                {
                    "api_id": payload["api_id"],
                    "parameter": payload["parameter"]
                }
            ))

    # TODO Add MediaStreamTrack
    def audio_handler(self, address, *args):
        std_out(f"{address}: {args}")
        argsd = json.loads(args[0])
        std_out (argsd)

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

    def lowstate_callback(self, message):
        current_message = message['data']
        self.state['LOW_STATE'] = current_message
        asyncio.gather(tcp_state_client(self.state))

    def multiplestate_callback(self, message):
        # TODO For whatever reason this needs to be parsed into json
        current_message = json.loads(message['data'])
        self.state['MULTIPLE_STATE'] = current_message
        asyncio.gather(tcp_state_client(self.state))

    def sportstate_callback(self, message):
        current_message = message['data']
        self.state['LF_SPORT_MOD_STATE'] = current_message
        asyncio.gather(tcp_state_client(self.state))

    def announce(self, dest):
        print ('Announce dog')