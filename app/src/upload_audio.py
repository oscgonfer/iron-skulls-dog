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

async def upload_file(file = None):

    std_out('Creating audio upload task...')

    async with asyncio.TaskGroup() as tg:
        tg.create_task(dog.upload_audio_file(audio_file = file))

if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--file", default=False, dest='file', help="Audio file to upload"
    )

    parser.add_argument(
        "--dry-run", default=False, dest='dry_run', action='store_true', help="Dry run mode"
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
    dog = Dog(conn, dry_run=args.dry_run, mqtt_handler=mqtt_handler)

    std_out ("Starting handlers...")
    command_handler = CommandHandler(dog)

    std_out ("Starting worker...")
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    if not args.dry_run:
        # Connect to the dog
        loop.run_until_complete(dog.connect())
        loop.run_until_complete(upload_file(file=args.file))
