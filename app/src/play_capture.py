import argparse
import random
import time
import json
from mqtt_handler import MQTTHandler
from config import *
from tools import *
from command import *
import datetime
from media_track import Track
import os

async def main():

    cstart = 0
    if 'track' in capture['metadata']:
        track_path = capture['metadata']['track']['path']
        if track_path is not None:
            start_at = capture['metadata']['track']['start_at']
            end_at = capture['metadata']['track']['end_at']

            if os.path.exists(track_path):
                track = Track(path = track_path, start_at = start_at, end_at = end_at)
                if track is not None:
                    track.play()
                else:
                    std_out('Track couldnt be loaded')
            else:
                std_out('Track doesnt exist')

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
