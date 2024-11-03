"""Small example OSC client

This program sends 10 random values between 0.0 and 1.0 to the /filter address,
waiting for 1 seconds between each value.
"""

import argparse
import random
import time
import json
from pythonosc import tcp_client
from go2_webrtc_driver.constants import *
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
        "--move-api-id", type=int, dest='api_id', default=None, help="Command api id"
    )

    parser.add_argument(
        "--move-name", type=str, dest='move_name', default=None, help="Command name"
    )

    parser.add_argument(
        "--topic", type=str, default="SPORT_MOD", help="RTC topic"
    )

    parser.add_argument(
        "--param-name", type=str, dest='param_name', default="", help="Parameter name"
    )

    parser.add_argument(
        "--param-data", default=False, dest='param_data', action='store_true', help="Parameter data"
    )

    parser.add_argument(
        "--no-param-data", default=False, dest='no_param_data', action='store_true', help="Avoid sending parameter data"
    )


    parser.add_argument(
        "--dry-run", default=False, dest='dry_run', action='store_true', help="Dry run mode"
    )

    args = parser.parse_args()

    if args.api_id is not None:
        if args.api_id in SPORT_CMD.values():
            api_id = args.api_id
        else:
            raise SystemExit("api_id not in valid commands")
    elif args.move_name is not None:
        if args.move_name in SPORT_CMD:
            api_id = SPORT_CMD[args.move_name]
        else:
            raise SystemExit("Name not in valid commands")
    else:
        raise SystemExit("Can't publish without valid api_id")

    payload = {
        "topic": "",
        "api_id": api_id,
        "parameter": {}
    }

    # This is confusing but oh well
    if args.param_name:
        payload["parameter"] = {"name": args.param_name}

    if args.param_data is not None:
        if "name" in payload["parameter"]:
            if not args.no_param_data:
                payload["parameter"]["data"] = args.param_data
        else:
            if not args.no_param_data:
                payload["parameter"] = {"data": args.param_data}

    if args.topic in RTC_TOPIC:
        payload["topic"] = RTC_TOPIC[args.topic]
    else:
        raise SystemExit("RTC topic not valid")

    if DEBUG:
        std_out (f"Command: {json.dumps(payload)}")

    if not args.dry_run:
        client = tcp_client.SimpleTCPClient(args.ip, args.port)
        client.send_message(CMD_TOPIC, json.dumps(payload))