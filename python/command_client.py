"""Small example OSC client

This program sends 10 random values between 0.0 and 1.0 to the /filter address,
waiting for 1 seconds between each value.
"""

import argparse
import random
import time
import json
from pythonosc import tcp_client

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--ip", default="127.0.0.1", help="The ip of the OSC server")
    parser.add_argument(
        "--port", type=int, default=5005, help="The port the OSC server is listening on"
    )
    parser.add_argument(
        "--id", type=int, default=1008, help="The api id"
    )

    parser.add_argument(
        "--topic", type=str, default="SPORT_MOD", help="The name mode"
    )

    parser.add_argument(
        "--name", type=str, default="", help="The name mode"
    )

    args = parser.parse_args()
    payload = {
        "api_id": args.id,
        "parameter": ""
    }

    if args.name:
        payload["parameter"] = {"name": args.name}

    if args.topic:
        payload["topic"] = args.topic

    client = tcp_client.SimpleTCPClient(args.ip, args.port)

    client.send_message("/dog", json.dumps(payload))