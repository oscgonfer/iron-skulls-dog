import argparse
import random
import time
import json
from mqtt_handler import MQTTHandler
from config import *
from tools import *
from command import *
import datetime
import os

async def main():

    # cstart = 0
    start_time = datetime.datetime.now()
    # Discarded the start_at because feels dangerous to cut commands halfway
    # if 'start_at' in capture['metadata']:
    #     cstart = capture['metadata']['start_at']
    # print (cstart)
    
    for item in capture['commands']:
        timestamp = datetime.timedelta(seconds = item["timestamp"]["seconds"], microseconds=item["timestamp"]["microseconds"])

        # print (timestamp.total_seconds()*1000)
        # print (item)
        # if timestamp.total_seconds()*1000<cstart: print ('skip'); continue

        if "command" in item:
            cmd = Command(json.loads(item["command"]))
        elif "audio_command" in item:
            cmd = AudioCommand(json.loads(item["audio_command"]))
        
        topic = item["mqtt_topic"]
        
        while not datetime.datetime.now()-start_time > timestamp:
            time.sleep(0.001)

        await mqtt_handler.publish(topic=topic, payload=cmd.to_json())
    
    # TODO
    # Keep playing the track until it's done no matter the commands

if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--capture-file", type=str, dest='capture_file', default=None, help="Capture file"
    )

    args = parser.parse_args()

    with open(args.capture_file, 'r') as file:
        capture = json.load(file)
    
    mqtt_handler = MQTTHandler(broker=MQTT_BROKER)
    asyncio.run(main())
