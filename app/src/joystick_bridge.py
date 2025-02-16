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
from command import *
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
        "topic": RTC_TOPIC["SPORT_MOD"],
        "options": {
            "parameter": "",
            "api_id": SPORT_CMD[command_name]
        }
    }

    return payload

def gen_movement_payload(x: float, y: float, z: float):
    x = round(x * JOY_SENSE["speed"], 2)
    y = round(y * JOY_SENSE["speed"], 2)

    payload = {
        "topic": RTC_TOPIC["SPORT_MOD"],
        "options": {
            "parameter": json.dumps({"x": x, "y": y, "z": z}),
            "api_id": SPORT_CMD["Move"]
        }
    }

    return payload

def gen_euler_payload(roll: float, pitch: float, yaw: float):
    _roll = round(roll * JOY_SENSE["roll"], 2)
    _pitch = round(pitch * JOY_SENSE["pitch"], 2)
    _yaw = round(yaw * JOY_SENSE["yaw"], 2)

    payload = {
        "topic": RTC_TOPIC["SPORT_MOD"],
        "options": {
            "parameter": json.dumps({"x": _roll, "y": _pitch, "z": _yaw}),
            "api_id": SPORT_CMD["Euler"]
        }
    }

    return payload

def handle_hat(joystick_values):
    # Handles the hat // Changes joystick sensitivity
    if joystick_values[0]:
        JOY_SENSE["speed"] = min(VAL_LIMITS["speed"][1], JOY_SENSE["speed"] + 0.1)
    elif joystick_values[1]:
        JOY_SENSE["speed"] = max(VAL_LIMITS["speed"][0], JOY_SENSE["speed"] - 0.1)

    if joystick_values[2]:
        JOY_SENSE["roll"] = min(VAL_LIMITS["roll"][1], JOY_SENSE["roll"] + 0.1)
        JOY_SENSE["pitch"] = min(VAL_LIMITS["pitch"][1], JOY_SENSE["pitch"] + 0.1)
        JOY_SENSE["yaw"] = min(VAL_LIMITS["yaw"][1], JOY_SENSE["yaw"] + 0.1)
    elif joystick_values[3]:
        JOY_SENSE["roll"] = max(VAL_LIMITS["roll"][0], JOY_SENSE["roll"] - 0.1)
        JOY_SENSE["pitch"] = max(VAL_LIMITS["pitch"][0], JOY_SENSE["pitch"] - 0.1)
        JOY_SENSE["yaw"] = max(VAL_LIMITS["yaw"][0], JOY_SENSE["yaw"] - 0.1)

    std_out(f'New joysense speed: {JOY_SENSE}')

def gen_safe_command(command):
    payload = {
        "command": command
    }

    return payload

def handle_client_msg(client, topic, msg):
    if client is not None:
        try:
            client.send_message(topic, msg)
        except BrokenPipeError:
            client.close()
            raise SystemExit("Broken pipe. Disconnected")

async def start_joy_bridge(client = None, joystick=None):

    joystick_state = JoystickState(joystick)

    # TODO Make this listen to topics
    robot_stat = "BalanceStand"

    while True:
        joystick_values = await joystick_state.get_item_values()

        std_out (f"Joystick values: {joystick_values}")

        cmd = None

        # We are moving the axes
        if any([joystick_values[item] for item in joystick_values if 'Axis' in item]):
            std_out ('Movement with axis!')

            if robot_stat == "BalanceStand":
                cmd = MovementCommand(gen_movement_payload(
                    x = joystick_values["Axis 1"],
                    y = joystick_values["Axis 0"],
                    z = joystick_values["Axis 2"]
                ))
            elif robot_stat == 'Pose':
                cmd = MovementCommand(gen_euler_payload(
                    roll = joystick_values["Axis 0"],
                    pitch = joystick_values["Axis 1"],
                    yaw = joystick_values["Axis 2"]
                ))

            if cmd is not None:
                std_out (f'Robot command: {cmd.as_dict()}')
                handle_client_msg(client, MOVE_TOPIC, cmd.to_json())

        # We are moving the hat
        if any([joystick_values[item] for item in joystick_values if 'Hat' in item]):

            for item in joystick_values:
                if 'Hat' not in item: continue
                if any(joystick_values[item]):
                    handle_hat(joystick_values[item])

        # We are pressing a button
        if any([joystick_values[item] for item in joystick_values if ('Axis' not in item and 'Hat' not in item)]):
            std_out ('A button was pressed!')

            for item in joystick_values:
                if 'Axis' in item or 'Hat' in item: continue

                if joystick_values[item]:
                    if BUTTON_CMD[item] is not None:

                        if BUTTON_CMD[item] in SAFETY_CMD:
                            cmd = SpecialCommand(gen_safe_command(BUTTON_CMD[item]))
                            std_out (f'Robot command {cmd.as_dict()}')
                            handle_client_msg(client, SAFE_TOPIC, cmd.to_json())
                        else:
                            cmd = SpecialCommand(gen_command_payload(BUTTON_CMD[item]))
                            std_out (f'Robot command {cmd.as_dict()}')

                            robot_stat = BUTTON_CMD[item]
                            std_out (f'Robot status {robot_stat}')

                            if cmd is not None:
                                handle_client_msg(client, SPECIAL_TOPIC, cmd.to_json())

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
