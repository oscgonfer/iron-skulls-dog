import argparse
import random
import time
import json
from pythonosc import tcp_client
from config import *
from tools import *


if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--ip", default=SERVER_IP, help="The ip of the OSC server"
    )

    parser.add_argument(
        "--port", type=int, default=SERVER_PORT, help="The port the OSC server is listening on"
    )

    parser.add_argument(
        "--action", type=str, dest='action', default=None, help="Action"
    )

    parser.add_argument(
        "--name", type=str, dest='name', default=None, help="name"
    )

    args = parser.parse_args()


    payload = {
        "action": args.action,
        "name": args.name
    }

    std_out (f"Command: {json.dumps(payload)}")

    if args.action is not None:
        client = tcp_client.SimpleTCPClient(args.ip, args.port)
        client.send_message(CAPTURE_TOPIC, json.dumps(payload))