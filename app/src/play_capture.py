import argparse
import random
import time
import json
from pythonosc import tcp_client
from config import *
from tools import *
from command import *
import datetime


if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--ip", default=SERVER_IP, help="The ip of the OSC server"
    )

    parser.add_argument(
        "--port", type=int, default=SERVER_PORT, help="The port the OSC server is listening on"
    )

    parser.add_argument(
        "--capture-file", type=str, dest='capture_file', default=None, help="Capture file"
    )

    args = parser.parse_args()

    with open(args.capture_file, 'r') as file:
        capture = json.load(file)

    start_time = datetime.datetime.now()
    for item in capture:
        timestamp = datetime.timedelta(seconds = item["timestamp"]["seconds"], microseconds=item["timestamp"]["microseconds"])
        command = Command(json.loads(item["command"]))
        topic = item["osc_topic"]
        while not datetime.datetime.now()-start_time > timestamp:
            time.sleep(0.001)

        client = tcp_client.SimpleTCPClient(args.ip, args.port)
        client.send_message(topic, command.to_json())