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

from go2_webrtc_driver.constants import *
from joystick_handler import JoystickHandler, JOY_SENSE
from mqtt_handler import MQTTHandler
from dog import DogMode

async def joystick_bridge(joystick_handler=None, queue=None, mqtt_handler=None):
    dog_state = None

    while True:
        joystick_values = await joystick_handler.get_item_values()
        # std_out (f"Joystick values: {joystick_values}")
        cmd = None

        try:
            source, data = queue.get_nowait()
        except asyncio.QueueEmpty:
            pass
        else:
            if STATE_TOPIC in source:
                try:
                    payload = json.loads(data)
                except json.decoder.JSONDecodeError:
                    std_out('Malformed payload. Ignoring')
                    pass
                else:
                    try:
                        _dog_state = payload['LF_SPORT_MOD_STATE']['mode']
                    except:
                        std_out('Payload doesnt contain dog mode')
                        pass
                    else:
                        dog_state = _dog_state

        # We are moving the axes
        if any([joystick_values[item] for item in joystick_values if 'Axis' in item]):
            # std_out ('Movement with axis!')

            match dog_state:
                case DogMode.MOVE | DogMode.MOVING:
                    cmd = Move(
                        x = round(joystick_values["Axis 1"] * JOY_SENSE["speed"], 2),
                        y = round(joystick_values["Axis 0"] * JOY_SENSE["speed"], 2),
                        z = round(joystick_values["Axis 2"] * JOY_SENSE["speed"], 2)
                    )
                case DogMode.STANDING:
                    cmd = Euler(
                        roll = round(joystick_values["Axis 0"] * JOY_SENSE["roll"], 2),
                        pitch = round(joystick_values["Axis 1"] * JOY_SENSE["pitch"], 2),
                        yaw = round(joystick_values["Axis 2"] * JOY_SENSE["yaw"], 2)
                    )

            outgoing_topic = MOVE_TOPIC

        # We are pressing a button
        if any([joystick_values[item] for item in joystick_values if ('Axis' not in item and 'Hat' not in item)]):
            # std_out ('A button was pressed!')

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

                        outgoing_topic = SPORT_TOPIC

        if cmd is not None:
            std_out (f'Robot command: {cmd.as_dict()}')
            await mqtt_handler.publish(topic=outgoing_topic, payload=cmd.to_json())

        # This sleep is needed to receive mqtt commands. Could it be avoided with an additional task through the joystick_handler?
        await asyncio.sleep(0.001)

async def start_bridge(mqtt_handler = None, joystick = None):
    queue = asyncio.Queue()
    joystick_handler = JoystickHandler(joystick)

    async with asyncio.TaskGroup() as tg:
        tg.create_task(mqtt_handler.bridge_incomming(topic=STATE_FILTER, queue=queue))
        tg.create_task(joystick_bridge(joystick_handler=joystick_handler, queue=queue, mqtt_handler = mqtt_handler))

async def main():

    std_out('Starting joystick coroutine...')
    coroutine = await start_bridge(
        mqtt_handler = mqtt_handler,
        joystick = joystick)

    loop = asyncio.get_event_loop()
    std_out('Bridge coroutine started')

    try:
        loop.run_until_complete(coroutine)
    # Quit pygame smoothly
    except KeyboardInterrupt:
        raise SystemExit()
        pass
    finally:
        pygame.joystick.quit()

if __name__ == '__main__':
    # Start pygame
    pygame.init()
    pygame.joystick.init()

    #Get joystick
    if pygame.joystick.get_count() > 0:
        joystick = pygame.joystick.Joystick(0)
        joystick.init()
    else:
        joystick = None

    # MQTT Handler
    mqtt_handler = MQTTHandler(broker=MQTT_BROKER)

    asyncio.run(main())
