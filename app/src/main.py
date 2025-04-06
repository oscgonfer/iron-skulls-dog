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
from command import *
from command_handler import CommandHandler

from mqtt_handler import MQTTHandler

# GO2 WEBRTC DRIVER
from go2_webrtc_driver.webrtc_driver import Go2WebRTCConnection, WebRTCConnectionMethod
from go2_webrtc_driver.constants import *

async def main():

    queue = asyncio.Queue()
    std_out('Creating tasks...')

    async with asyncio.TaskGroup() as tg:
        for topic in INCOMING_TOPICS:
            tg.create_task(mqtt_handler.bridge_incomming(topic=topic, queue=queue))

        tg.create_task(command_handler.dispatch_commands(queue=queue))
        std_out ("Looping forever...")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--dry-run", default=False, dest='dry_run', action='store_true', help="Dry run mode"
    )

    parser.add_argument(
        "--broadcast", default=False, dest='broadcast', action='store_true'
    )

    args = parser.parse_args()

    if not args.dry_run:
        # conn = Go2WebRTCConnection(WebRTCConnectionMethod.LocalSTA, ip=os.getenv("GO2_IP"))
        # conn = Go2WebRTCConnection(WebRTCConnectionMethod.LocalSTA, \
        #   serialNumber =os.getenv("GO2_SN"))
        conn = Go2WebRTCConnection(WebRTCConnectionMethod.LocalAP)
    else:
        std_out("Running dry..")
        conn = None

    mqtt_handler = MQTTHandler(broker=MQTT_BROKER)
    dog = Dog(conn, dry_run=args.dry_run, broadcast=args.broadcast, mqtt_handler=mqtt_handler)

    std_out ("Starting handlers...")
    command_handler = CommandHandler(dog)

    std_out ("Starting worker...")
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    if not args.dry_run:
        loop.run_until_complete(dog.connect())

        dog.conn.datachannel.pub_sub.subscribe(RTC_TOPIC['LOW_STATE'], \
            dog.lowstate_callback)
        dog.conn.datachannel.pub_sub.subscribe(RTC_TOPIC['MULTIPLE_STATE'], \
            dog.multiplestate_callback)
        dog.conn.datachannel.pub_sub.subscribe(RTC_TOPIC['LF_SPORT_MOD_STATE'], \
            dog.sportstate_callback)
    try:
        loop.run_until_complete(main())
    except KeyboardInterrupt:
        std_out("Program interrupted by user")
        sys.exit(0)
