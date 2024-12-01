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

    dog = Dog(conn)

    std_out ("Starting handlers...")
    dispatcher = Dispatcher()
    dispatcher.map(CMD_FILTER, dog.command_handler)
    dispatcher.map(MOVE_FILTER, dog.movement_handler)
    dispatcher.map(VUI_FILTER, dog.command_handler)
    dispatcher.map(AUDIO_FILTER, dog.audio_handler)

    std_out ("Starting worker...")
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    std_out ("Looping forever..")
    if not DRY_RUN:
        loop.run_until_complete(dog.connect())
        loop.run_until_complete(dog.set_motion_switcher_status(desired_mode = 'normal'))

        if TCP_LOG:
            dog.conn.datachannel.pub_sub.subscribe(RTC_TOPIC['LOW_STATE'], dog.lowstate_callback)
            dog.conn.datachannel.pub_sub.subscribe(RTC_TOPIC['MULTIPLE_STATE'], dog.multiplestate_callback)
            dog.conn.datachannel.pub_sub.subscribe(RTC_TOPIC['LF_SPORT_MOD_STATE'], dog.sportstate_callback)

    loop.run_until_complete(main())
