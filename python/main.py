from dotenv import load_dotenv
load_dotenv()

import json
import asyncio
import os

# GO2 WEBRTC DRIVER
from go2_webrtc_driver.webrtc_driver import Go2WebRTCConnection, WebRTCConnectionMethod
from go2_webrtc_driver.constants import *

# Config
from config import *
from tools import *

# TCP SERVER
from pythonosc.osc_tcp_server import AsyncOSCTCPServer
from pythonosc.dispatcher import Dispatcher

async def connect_dog(conn):
    return await conn.connect()

async def get_motion_switcher_status(conn, desired_mode = None):
    # Get the current motion_switcher status
    response = await conn.datachannel.pub_sub.publish_request_new(
        RTC_TOPIC["MOTION_SWITCHER"],
        {"api_id": 1001}
    )

    if response['data']['header']['status']['code'] == 0:
        data = json.loads(response['data']['data'])
        current_motion_switcher_mode = data['name']
        std_out(f"Current motion mode: {current_motion_switcher_mode}")

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

# TODO Check busystatus...
async def command_handler(address, *args):
    if DEBUG:
        std_out(f"{address}: {args}")

    payload = json.loads(args[0])
    if DEBUG:
        std_out(f"Command Payload: {payload}")

    response = await conn.datachannel.pub_sub.publish_request_new(
        payload["topic"],
        {
            "api_id": payload["api_id"],
            "parameter": payload["parameter"]
        }
    )

    await asyncio.sleep(3)

    if DEBUG:
        std_out(f"Command Response: {payload}")

def movement_handler(address, *args):
    if DEBUG:
        std_out(f"{address}: {args}")

    payload = json.loads(args[0])
    if DEBUG:
        std_out(f"Movement Payload: {payload}")

    loop.create_task(conn.datachannel.pub_sub.publish_request_new(
        payload["topic"],
        {
            "api_id": payload["api_id"],
            "parameter": payload["parameter"]
        }
    ))

# def audio_handler(address, *args):
#     std_out(f"{address}: {args}")
#     argsd = json.loads(args[0])
#     std_out (argsd)

async def main():
    server = AsyncOSCTCPServer(SERVER_IP, SERVER_PORT, dispatcher)
    await server.start()

if __name__ == "__main__":

    if not DRY_RUN:
        # conn = Go2WebRTCConnection(WebRTCConnectionMethod.LocalSTA,
        #     ip=os.getenv("GO2_IP"))
        conn = Go2WebRTCConnection(WebRTCConnectionMethod.LocalAP)
    else:
        std_out("Running dry..")

    std_out ("Starting handlers...")
    dispatcher = Dispatcher()
    dispatcher.map(CMD_FILTER, command_handler)
    dispatcher.map(MOVE_FILTER, movement_handler)
    # dispatcher.map(AUDIO_FILTER, audio_handler)

    std_out ("Starting workers...")
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    std_out ("Looping forever..")
    if not DRY_RUN:
        loop.run_until_complete(connect_dog(conn))
        loop.run_until_complete(get_motion_switcher_status(conn,
            desired_mode = 'normal'))
    loop.run_until_complete(main())
