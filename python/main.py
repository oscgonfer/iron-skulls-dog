import os
from dotenv import load_dotenv
load_dotenv()

import json

from go2_webrtc_driver.webrtc_driver import Go2WebRTCConnection, WebRTCConnectionMethod
from go2_webrtc_driver.constants import *

# Config
from config import *
from pythonosc.osc_tcp_server import AsyncOSCTCPServer
from pythonosc.dispatcher import Dispatcher
import asyncio

conn = Go2WebRTCConnection(WebRTCConnectionMethod.LocalSTA, ip=os.getenv("GO2_IP"))

async def connect_dog(conn):
    return await conn.connect()

def filter_handler(address, *args):
    print(f"{address}: {args}")
    argsd = json.loads(args[0])
    print (argsd)

    topic = "SPORT_MOD"
    if "topic" in argsd:
        topic = argsd["topic"]

    parameter = ""
    if "parameter" in argsd:
        parameter = argsd["parameter"]

    api_id = ""
    if "api_id" in argsd:
        api_id = argsd["api_id"]

    response = loop.create_task(
        conn.datachannel.pub_sub.publish_request_new(
            RTC_TOPIC[topic],
            {"api_id": api_id, "parameter": parameter}
        ))

dispatcher = Dispatcher()
dispatcher.map(UDP_FILTER, filter_handler)

async def loop():
    while True:
        print("loop")
        await asyncio.sleep(.1)

async def init_main():
    loop = asyncio.get_event_loop()
    server = AsyncOSCTCPServer(SERVER_IP, SERVER_PORT, dispatcher)
    await server.start()

if __name__ == "__main__":

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(connect_dog(conn))
    loop.run_until_complete(init_main())
