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
import time
import json
import os
import pygame
from dotenv import load_dotenv
load_dotenv()

from go2_webrtc_driver.constants import *
from joystick_handler import JoystickHandler
from mqtt_handler import MQTTHandler
from dog import DogState
from apc_mk2_config import *

def get_limit(dog_state_name, param, mpc_state):
    if dog_state_name not in CMD_LIMITS:
        return 0

    key = CMD_LIMITS[dog_state_name][param]["mpc_key"]
    value_range = map_range(mpc_state[key]["input_state"], 
        APC_MK2_FADER_LIMITS[0], 
        APC_MK2_FADER_LIMITS[1], 
        0,
        # CMD_LIMITS[dog_state_name]["vx"][0],
        CMD_LIMITS[dog_state_name][param]["range"][1])
    return value_range

async def joystick_bridge(joystick_handler=None, queue=None, mqtt_handler=None):
    dog_state = None
    mpc_state = None

    while True:
        joystick_status = await joystick_handler.get_item_status()
        # std_out (f"Joystick status: {joystick_status}")
        cmd = None

        try:
            source, data = queue.get_nowait()
        except asyncio.QueueEmpty:
            pass
        else:
            # Add here topics to subscribe
            if STATE_TOPIC in source.value:
                try:
                    state_payload = json.loads(data)
                except json.decoder.JSONDecodeError:
                    std_out('Malformed state. Ignoring')
                    pass
                else:
                    try:
                        _dog_state = state_payload['LF_SPORT_MOD_STATE']['mode']
                    except:
                        std_out('Payload doesnt contain dog mode')
                        pass
                    else:
                        dog_state = _dog_state

            if MPC_TOPIC in source.value:
                try:
                    mpc_payload = json.loads(data)
                except json.decoder.JSONDecodeError:
                    std_out('Malformed payload. Ignoring')
                    pass
                else:
                    mpc_state = mpc_payload
        
        if dog_state is not None:
            dog_state_name = None
            try:
                dog_state_name = DogState(dog_state).name
            except:
                pass

        if mpc_state is not None:
            roll_range = get_limit(dog_state_name, "roll", mpc_state)
            pitch_range = get_limit(dog_state_name, "pitch", mpc_state)
            yaw_range = get_limit(dog_state_name, "yaw", mpc_state)

            vx_range = get_limit(dog_state_name, "vx", mpc_state)
            vy_range = get_limit(dog_state_name, "vy", mpc_state)
            vyaw_range = get_limit(dog_state_name, "vyaw", mpc_state)

        else:
            roll_range = joystick_handler.sensitivity["roll"]/4
            pitch_range = joystick_handler.sensitivity["pitch"]/4
            yaw_range = joystick_handler.sensitivity["yaw"]/4

            vx_range = joystick_handler.sensitivity["vx"]
            vy_range = joystick_handler.sensitivity["vy"]
            vyaw_range = joystick_handler.sensitivity["vyaw"]

        # We are moving the axes
        if any([joystick_status[item] for item in joystick_status if 'Axis' in item]):
            std_out ('Movement with axis!')
            match dog_state:
                case DogState.MOVE | DogState.MOVING | DogState.AI_AGILE | DogState.AI_FREEAVOID | DogState.AI_FREEBOUND | DogState.AI_WALKSTAIR | DogState.AI_FREEJUMP | DogState.AI_WALKUPRIGHT | DogState.AI_CROSSSTEP:

                    outgoing_topic = MOVE_TOPIC

                    # TODO make this with modifiers to joystick axes behaviour. 
                    # This right now mimicks the approach in the bluetooth joystick
                    if not joystick_status["R2"]:
                        
                        cmd = Move(
                            x = round(joystick_status["Axis 1"] * vx_range, 2),
                            y = round(joystick_status["Axis 0"] * vy_range, 2),
                            z = round(joystick_status["Axis 2"] * vyaw_range, 2)
                        )

                        if cmd is not None:
                            std_out (f'Robot command: {cmd.as_dict()}')
                            await mqtt_handler.publish(topic=outgoing_topic, payload=cmd.to_json())
                        
                        # While moving, we don't send any Euler
                        roll_range = 0
                        yaw_range = 0
                        if not joystick_status["Axis 3"]:
                            pitch_range = 0

                    if roll_range or pitch_range or yaw_range:
                        
                        cmd = Euler(
                            roll = round(joystick_status["Axis 0"]\
                                * roll_range, 2),
                            pitch = round(joystick_status["Axis 3"]\
                                * pitch_range, 2),
                            yaw = round(joystick_status["Axis 1"]\
                                * yaw_range, 2)
                        )

                        if cmd is not None:
                            std_out (f'Robot command: {cmd.as_dict()}')
                            await mqtt_handler.publish(topic=outgoing_topic, payload=cmd.to_json())

                case DogState.STANDING:
                    
                    cmd = Euler(
                        roll = round(joystick_status["Axis 0"]\
                            * roll_range, 2),
                        pitch = round(joystick_status["Axis 1"]\
                            * pitch_range, 2),
                        yaw = round(joystick_status["Axis 2"]\
                            * yaw_range, 2)
                    )

            outgoing_topic = MOVE_TOPIC

        # We are pressing a button
        if any([joystick_status[item] for item in joystick_status if ('Axis' not in item and 'Hat' not in item)]):
            # std_out ('A button was pressed!')

            for item in joystick_status:
                if 'Axis' in item or 'Hat' in item: continue
                
                if joystick_status[item]:

                    cmd_class = joystick_handler.buttons[item].command
                    
                    if cmd_class is not None:
                        # print (cmd_class)
                        # if cmd_class in SAFETY_CMD:
                        #     cmd = SportCommand(gen_safe_command(BUTTON_CMD[item]))
                        #     std_out (f'Robot command {cmd.as_dict()}')
                        #     send_msg_no_reply(client, SAFE_TOPIC, cmd.to_json())
                        # else:

                        # TODO Could the joystick have associated parameter?

                        # TODO 
                        # Check DogState for Pose or other toggle commands
                        # Is there anything reflecting those?
                        # case DogState.MOVE | DogState.MOVING | DogState.AI:
                        # Bring from midi-handler the same logic here

                        if cmd_class.__name__ in CMD_W_DATA:
                            cmd = cmd_class(True)
                        else:
                            cmd = cmd_class()

                        outgoing_topic = SPORT_TOPIC

        if cmd is not None:
            # std_out (f'Robot command: {cmd.as_dict()}')
            await mqtt_handler.publish(topic=outgoing_topic, payload=cmd.to_json())

        # This sleep is needed to receive mqtt commands. 
        # Could it be avoided with an additional task through the joystick_handler?
        await asyncio.sleep(0.001)

async def start_bridge(mqtt_handler = None, joystick = None):
    queue = asyncio.Queue()
    joystick_handler = JoystickHandler(joystick)

    async with asyncio.TaskGroup() as tg:
        tg.create_task(mqtt_handler.bridge_incomming(topic=f'{OUT_FILTER}/#', queue=queue))
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
