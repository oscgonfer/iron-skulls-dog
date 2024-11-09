# Copyright (c) 2024, RoboVerse community
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# 1. Redistributions of source code must retain the above copyright notice, this
#    list of conditions and the following disclaimer.
#
# 2. Redistributions in binary form must reproduce the above copyright notice,
#    this list of conditions and the following disclaimer in the documentation
#    and/or other materials provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
# OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

from config import *
import asyncio
import json
import os
import pygame
from dotenv import load_dotenv
load_dotenv()

from pythonosc import tcp_client
from go2_webrtc_driver.constants import *
from tools import *

from joystick_handler import JoystickState

def gen_command_payload(command_name):

    payload = {
        "parameter": "",
        "api_id": SPORT_CMD[command_name],
        "topic": RTC_TOPIC["SPORT_MOD"],
    }

    return json.dumps(payload)

def gen_movement_payload(x: float, y: float, z: float):
    x = round(x * JOY_SENSE, 2)
    y = round(y * JOY_SENSE, 2)

    payload = {
        "parameter": json.dumps({"x": x, "y": y, "z": z}),
        "api_id": SPORT_CMD["Move"],
        "topic": RTC_TOPIC["SPORT_MOD"],
    }

    return json.dumps(payload)

def handle_client_msg(client, topic, msg):
    if client is not None:
        try:
            client.send_message(topic, msg)
        except BrokenPipeError:
            client.close()
            raise SystemExit("Broken pipe. Disconnected")

async def start_joy_bridge(client = None, joystick=None):

    joystick_state = JoystickState(joystick)

    # TODO Make this listen to topics?
    robot_stat = "BalanceStand"

    while True:
        joystick_values = await joystick_state.get_item_values()

        if DEBUG:
            std_out (f"Joystick values: {joystick_values}")

        robot_cmd = None

        # We are moving the axes
        if any([joystick_values[item] for item in joystick_values if 'Axis' in item]):
            if DEBUG:
                std_out ('Movement with axis!')

            if robot_stat == "BalanceStand":
                robot_cmd = gen_movement_payload(
                    x = joystick_values["Axis 1"],
                    y = joystick_values["Axis 0"],
                    z = joystick_values["Axis 2"]
                )

            if DEBUG:
                std_out (f'Robot command: {robot_cmd}')

            if robot_cmd is not None: handle_client_msg(client, MOVE_TOPIC, robot_cmd)

        # TODO asign to the hat
        # We are moving the hat
        # if any([joystick_values[item] for item in joystick_values if 'Hat' in item]):
        #     if DEBUG:
        #         std_out ('Movement with hat!')

            # robot_cmd = gen_movement_payload(
            #     x = joystick_values["Axis 1"],
            #     y = joystick_values["Axis 0"],
            #     z = joystick_values["Axis 2"]
            # )

            # if DEBUG:
            #     std_out ('Robot command ', robot_cmd)

            # if client is not None:
            #     client.send_message("/dog/move", robot_cmd)

        # We are pressing a button
        if any([joystick_values[item] for item in joystick_values if ('Axis' not in item and 'Hat' not in item)]):
            std_out ('A button was pressed!')

            for item in joystick_values:
                if 'Axis' in item or 'Hat' in item: continue

                if joystick_values[item]:
                    if BUTTON_CMD[item] is not None:
                        robot_cmd = gen_command_payload(BUTTON_CMD[item])
                        std_out (f'Robot command {robot_cmd}')

                        robot_stat = BUTTON_CMD[item]
                        std_out (f'Robot status {robot_stat}')

                        if robot_cmd is not None:
                            handle_client_msg(client, CMD_TOPIC, robot_cmd)

        await asyncio.sleep(0.001)

async def main():
    coroutine = await start_joy_bridge(
        client = client,
        joystick = joystick)

    loop = asyncio.get_event_loop()

    try:
        loop.run_until_complete(coroutine)
    # Quit pygame smoothly
    except KeyboardInterrupt:
        raise SystemExit()
        pass
    finally:
        pygame.joystick.quit()

if __name__ == '__main__':
    pygame.init()
    pygame.joystick.init()

    if pygame.joystick.get_count() > 0:
        joystick = pygame.joystick.Joystick(0)
        joystick.init()
    else:
        joystick = None

    std_out('Starting TCP client...')
    client = None
    client = tcp_client.SimpleTCPClient(SERVER_IP, SERVER_PORT)

    asyncio.run(main())
