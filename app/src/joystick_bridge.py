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
from tools import std_out
import asyncio
import json
import os
import pygame
from dotenv import load_dotenv
load_dotenv()

from pythonosc import tcp_client
from go2_webrtc_driver.constants import *

from joystick_handler import JoystickState
import websockets

def send_msg_no_reply(client, topic, msg):
    if client is not None:
        try:
            client.send_message(topic, msg)
        except BrokenPipeError:
            client.close()
            raise SystemExit("Broken pipe. Disconnected")

async def ws_bridge(incoming_url, queue):
    async with websockets.connect(incoming_url) as ws:
        while True:
            try:
                data = await ws.recv()
                # TODO Add filter for response
                # Load json, and get data first,
                # before putting it on the queue
                await queue.put(('ws', data))
            except websockets.exceptions.ConnectionClosed:
                # TODO Handle a retry?
                pass

async def joystick_bridge(client=None, joystick=None, queue=None):

    joystick_state = JoystickState(joystick)

    while True:
        joystick_values = await joystick_state.get_item_values()
        std_out (f"Joystick values: {joystick_values}")
        cmd = None
        robot_state = 'BalanceStand'

        try:
            source, data = queue.get_nowait()
        except asyncio.QueueEmpty:
            pass
        else:
            if source == 'ws':
                print(f'WS Incomming: {data}')

        # We are moving the axes
        if any([joystick_values[item] for item in joystick_values if 'Axis' in item]):
            std_out ('Movement with axis!')

            # TODO Bring state from dog.py
            if robot_state == "BalanceStand":
                cmd = Move(
                    x = round(joystick_values["Axis 1"] * JOY_SENSE["speed"], 2),
                    y = round(joystick_values["Axis 0"] * JOY_SENSE["speed"], 2),
                    z = round(joystick_values["Axis 2"] * JOY_SENSE["speed"], 2)
                )
            elif robot_state == 'Pose':
                cmd = Euler(
                    roll = round(joystick_values["Axis 0"] * JOY_SENSE["roll"], 2),
                    pitch = round(joystick_values["Axis 1"] * JOY_SENSE["pitch"], 2),
                    yaw = round(joystick_values["Axis 2"] * JOY_SENSE["yaw"], 2)
                )

            if cmd is not None:
                std_out (f'Robot command: {cmd.as_dict()}')
                send_msg_no_reply(client, MOVE_TOPIC, cmd.to_json())

        # We are pressing a button
        if any([joystick_values[item] for item in joystick_values if ('Axis' not in item and 'Hat' not in item)]):
            std_out ('A button was pressed!')

            for item in joystick_values:
                if 'Axis' in item or 'Hat' in item:
                    continue

                cmd_class = BUTTON_CMD[item]

                if joystick_values[item]:
                    if cmd_class is not None:
                        # if cmd_class in SAFETY_CMD:

                        #     cmd = SportCommand(gen_safe_command(BUTTON_CMD[item]))
                        #     std_out (f'Robot command {cmd.as_dict()}')
                        #     send_msg_no_reply(client, SAFE_TOPIC, cmd.to_json())

                        # else:

                        # TODO Could the joystick have associated parameter?
                        cmd = cmd_class()
                        std_out (f'Robot command {cmd.as_dict()}')

                        # robot_state = BUTTON_CMD[item]
                        # std_out (f'Robot status {robot_state}')

                        if cmd is not None:
                            send_msg_no_reply(client, SPORT_TOPIC, cmd.to_json())

        await asyncio.sleep(0.001)

async def start_bridge(client = None, joystick = None):
    queue = asyncio.Queue()

    ws_task = asyncio.create_task(ws_bridge(incoming_url = f'ws://{WS_IP}:{WS_PORT}/sub', queue=queue))
    joy_task = asyncio.create_task(joystick_bridge(client = client, joystick=joystick, queue=queue))

    await asyncio.gather(*[ws_task, joy_task])

async def main():

    std_out('Starting joystick coroutine...')
    coroutine = await start_bridge(
        client = client,
        joystick = joystick)

    loop = asyncio.get_event_loop()
    std_out('Joystick coroutine started')

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
    std_out('TCP client started')

    asyncio.run(main())
