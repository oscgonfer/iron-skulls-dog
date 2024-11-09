from dotenv import load_dotenv
load_dotenv()

import json
import asyncio
import os

# Config
from config import *

# Extras
from tools import *
from dog import *

# TCP SERVER
from pythonosc.osc_tcp_server import AsyncOSCTCPServer
from pythonosc.dispatcher import Dispatcher

# GO2 WEBRTC DRIVER
from go2_webrtc_driver.webrtc_driver import Go2WebRTCConnection, WebRTCConnectionMethod
from go2_webrtc_driver.constants import *

async def command_handler(address, *args):

    payload = json.loads(args[0])
    std_out(f"{address}: {args}")
    std_out(f"Command Payload: {payload}")
    std_out(f"Waiting for lock...")

    await lock.acquire()

    if DRY_RUN:
        std_out(f"Sleeping 3s...")
        await asyncio.sleep(3)
        std_out(f"Done!")
    else:
        response = await conn.datachannel.pub_sub.publish_request_new(
            payload["topic"],
            {
                "api_id": payload["api_id"],
                "parameter": payload["parameter"]
            }
        )

        std_out(f"Command Response: {response}")

    lock.release()

def movement_handler(address, *args):
    payload = json.loads(args[0])

    std_out(f"{address}: {args}")
    std_out(f"Movement Payload: {payload}")
    if not DRY_RUN:
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
        conn = Go2WebRTCConnection(WebRTCConnectionMethod.LocalSTA,
            ip=os.getenv("GO2_IP"))
        # conn = Go2WebRTCConnection(WebRTCConnectionMethod.LocalAP)
    else:
        std_out("Running dry..")

    std_out ("Starting handlers...")
    dispatcher = Dispatcher()
    dispatcher.map(CMD_FILTER, command_handler)
    dispatcher.map(MOVE_FILTER, movement_handler)
    # dispatcher.map(AUDIO_FILTER, audio_handler)

    std_out ("Starting worker...")
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    lock = asyncio.Lock()

    std_out ("Looping forever..")
    if not DRY_RUN:
        loop.run_until_complete(connect_dog(conn))
        loop.run_until_complete(set_motion_switcher_status(conn,
            desired_mode = 'normal'))
    loop.run_until_complete(main())
