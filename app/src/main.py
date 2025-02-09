from dotenv import load_dotenv
load_dotenv()

import json
import asyncio
import os
import argparse

# Config
from config import *

# Extras
from tools import *
from dog import Dog
from osc_handler import OscHandler

# TCP SERVER
from pythonosc.osc_tcp_server import AsyncOSCTCPServer
from pythonosc.dispatcher import Dispatcher

# GO2 WEBRTC DRIVER
from go2_webrtc_driver.webrtc_driver import Go2WebRTCConnection, WebRTCConnectionMethod
from go2_webrtc_driver.constants import *


async def main():
    server = AsyncOSCTCPServer(SERVER_IP, SERVER_PORT, dispatcher)
    await server.start()

if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--dry-run", default=False, dest='dry_run', action='store_true', help="Dry run mode"
    )

    args = parser.parse_args()

    if not args.dry_run:
        conn = Go2WebRTCConnection(WebRTCConnectionMethod.LocalSTA,
            ip=os.getenv("GO2_IP"))
        # conn = Go2WebRTCConnection(WebRTCConnectionMethod.LocalAP)
    else:
        std_out("Running dry..")
        conn = None

    dog = Dog(conn, dry_run=args.dry_run)
    osc_handler = OscHandler(dog)
    std_out ("Starting handlers...")
    dispatcher = Dispatcher()
    # dispatcher.map(SPECIAL_CMD_FILTER, dog.command_handler)
    dispatcher.map(SPECIAL_FILTER, osc_handler.handle_special_command)
    dispatcher.map(MOVE_FILTER, osc_handler.handle_movement_command)
    dispatcher.map(CAPTURE_FILTER, osc_handler.handler_capture_command)
    # dispatcher.map(MOVE_FILTER, dog.movement_handler)
    # dispatcher.map(VUI_FILTER, dog.command_handler)
    # dispatcher.map(AUDIO_FILTER, dog.audio_handler)
    # dispatcher.map(SWITCHER_TOPIC, dog.command_handler)

    std_out ("Starting worker...")
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    std_out ("Looping forever..")
    if not args.dry_run:
        loop.run_until_complete(dog.connect())
        loop.run_until_complete(dog.set_motion_switcher_status(desired_mode = 'normal'))

        if TCP_LOG:
            dog.conn.datachannel.pub_sub.subscribe(RTC_TOPIC['LOW_STATE'], dog.lowstate_callback)
            dog.conn.datachannel.pub_sub.subscribe(RTC_TOPIC['MULTIPLE_STATE'], dog.multiplestate_callback)
            dog.conn.datachannel.pub_sub.subscribe(RTC_TOPIC['LF_SPORT_MOD_STATE'], dog.sportstate_callback)

    loop.run_until_complete(main())
