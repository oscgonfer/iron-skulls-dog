import asyncio
import json

# Config
from config import *
from tools import *
from go2_webrtc_driver.constants import *

async def connect_dog(conn):
    return await conn.connect()

async def get_motion_switcher_status(conn):
    # Get the current motion_switcher status
    response = await conn.datachannel.pub_sub.publish_request_new(
        RTC_TOPIC["MOTION_SWITCHER"],
        {"api_id": 1001}
    )

    if response['data']['header']['status']['code'] == 0:
        data = json.loads(response['data']['data'])
        current_motion_switcher_mode = data['name']
        std_out(f"Current motion mode: {current_motion_switcher_mode}")

    return current_motion_switcher_mode

async def set_motion_switcher_status(conn, desired_mode = None):

    current_motion_switcher_mode = await get_motion_switcher_status(conn)

    if desired_mode is not None:
        if current_motion_switcher_mode != desired_mode:
            std_out(f"Switching motion mode from {current_motion_switcher_mode} to {desired_mode}...")
            await conn.datachannel.pub_sub.publish_request_new(
                RTC_TOPIC["MOTION_SWITCHER"],
                {
                    "parameter": {"name": desired_mode}
                }
            )
            await asyncio.sleep(5)  # Wait while it stands up

    return current_motion_switcher_mode