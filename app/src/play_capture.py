import argparse
import random
import time
import json
from mqtt_handler import MQTTHandler
from config import *
from tools import *
from command import *
import datetime

async def main():

    start_time = datetime.datetime.now()
    for item in capture:
        timestamp = datetime.timedelta(seconds = item["timestamp"]["seconds"], microseconds=item["timestamp"]["microseconds"])
        cmd = Command(json.loads(item["command"]))
        topic = item["mqtt_topic"]
        
        while not datetime.datetime.now()-start_time > timestamp:
            time.sleep(0.001)

        await mqtt_handler.publish(topic=topic, payload=cmd.to_json())

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
