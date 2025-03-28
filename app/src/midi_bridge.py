from config import *
from command import *
from tools import std_out, map_range
import asyncio
import json
import os
from dotenv import load_dotenv
load_dotenv()

from go2_webrtc_driver.constants import *
from apc_mk2_handler import APCMK2Handler
from apc_mk2_config import *
from mqtt_handler import MQTTHandler
from dog import DogState
import subprocess

# TODO
# --------
# Captures
# --------
# Interface for editing
# name and description
# interface to edit name, descriptions and add tracks
# add slider for delaying the music
# show name and description for captures on preview
# -----
# Music
# -----
# drum - pipe to synth (intro)
# -----
# Modes
# -----
# Change mapping of limits on each command based on the ai mode
# Change commands available on each mode?
# 

async def midi_bridge(midi_handler=None, queue=None, mqtt_handler=None):
    dog_state = None
    dog_mode = None

    cmd = GetMotionSwitcherStatus()
    outgoing_topic = SPORT_TOPIC

    while True:
        
        # Get status of midi
        midi_values = midi_handler.status.copy()
        midi_handler.reset_triggers()
        
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
                        std_out('Payload doesnt contain dog state')
                        pass
                    else:
                        dog_state = _dog_state
                        midi_handler.update_dog_state(dog_state)
            if MODE_TOPIC in source:
                try:
                    payload = json.loads(data)
                except json.decoder.JSONDecodeError:
                    std_out('Malformed payload. Ignoring')
                    pass
                else:
                    try:
                        _dog_mode = payload
                    except:
                        std_out('Payload doesnt contain dog mode')
                        pass
                    else:
                        dog_mode = _dog_mode                
                        midi_handler.update_dog_mode(dog_mode)
        
        # If something happened...
        if any([midi_values[item]['trigger'] for item in midi_values]):
            # std_out(f"{[(midi_values[item]['name'], midi_values[item]['input_state'], midi_values[item]['trigger']) for item in midi_values]}")

            for midi_item in midi_values:
                _mi = midi_values[midi_item]

                if _mi['trigger']:
                    action = _mi["action"]

                    # Dog commands go here
                    if action.type == APCMK2ActionType.command and action.command is not None:
                        if 'FADER' in str(_mi['name']):
                            cmd = action.command(_mi['input_state'], 
                            value_range = APC_MK2_FADER_LIMITS)
                        else:
                            if _mi['input_state']:
                                # TODO Commands with data... what to do with it?
                                cmd = action.command()

                                if cmd.toggle:
                                    print ('Toggle command!')
                                    if cmd.associated_modes is not None:
                                        if dog_state == cmd.associated_modes:
                                            cmd = action.command(False)
                                else:
                                    print ('non toggle command!')
                        
                        outgoing_topic = action.payload
                    # Dog mode toggles go here
                    elif action.type == APCMK2ActionType.dog_mode_toggle and action.command is not None:
                        if _mi['input_state']:
                            cmd = action.command()

                        outgoing_topic = action.payload

                    # Capture commands go here
                    elif action.type == APCMK2ActionType.capture:
                        if _mi['input_state']:
                            cmd = action.command # Capture commands are not callable
                        outgoing_topic = action.payload

                    # Subprocess commands go here
                    elif action.type == APCMK2ActionType.subprocess:
                        if _mi['input_state']:
                            # Subprocesses are self-contained
                            file_path = os.path.dirname(os.path.realpath(__file__))
                            capture_path = os.path.join(file_path, CAPTURE_PATH, f'{action.payload}.cap')

                            if action.command == 'play':
                                std_out ('Play capture requested')
                                std_out (action.payload)

                                command = os.path.join(file_path, 'play_capture.py')

                                midi_handler.pads[midi_item].press()
                                midi_handler.update_lights()
                                midi_handler.lock()
                                std_out ('Play capture started')
                                subprocess.call(['python', command,'--capture-file', capture_path])
                                std_out ('Play capture done')
                                midi_handler.pads[midi_item].release()
                                midi_handler.unlock()
                                midi_handler.update_lights()
                            
                            elif action.command == 'preview':
                                print ('Preview capture requested')

                                with open(capture_path, 'r') as file:
                                    capture = json.load(file)
                                std_out (f'PREVIEW CAPTURE: {action.payload}', priority = True, timestamp = False)
                                std_out (f"\n\tName: {capture['metadata']['short_name']}", priority = True, timestamp = False)
                                std_out (f"\n\tDescription: {capture['metadata']['description']}\n", priority = True, timestamp = False)

        if cmd is not None:
            if midi_handler.current_state.id != 'preview':
                std_out (f'Command: {cmd.as_dict()}')
                await mqtt_handler.publish(topic=outgoing_topic, payload=cmd.to_json())
            else:
                std_out (f'PREVIEW: Command: {action.command.__name__}', priority = True, timestamp = False)
                print ()
                std_out (f'{action.command.__doc__}', priority = True, timestamp = False)
                print ()
        # This sleep is needed to receive mqtt commands. Could it be avoided with an additional task through the joystick_handler?
        await asyncio.sleep(0.001)
        cmd = None

async def start_bridge(mqtt_handler = None, midi_handler = None):
    queue = asyncio.Queue()

    async with asyncio.TaskGroup() as tg:
        tg.create_task(mqtt_handler.bridge_incomming(topic=STATE_FILTER, queue=queue))
        tg.create_task(mqtt_handler.bridge_incomming(topic=MODE_FILTER, queue=queue))
        tg.create_task(mqtt_handler.bridge_incomming(topic=CAPTURE_FILTER, queue=queue))
        tg.create_task(midi_bridge(midi_handler=midi_handler, queue=queue, mqtt_handler = mqtt_handler))

async def main():
    std_out('Starting midi coroutine...', priority=True)
    coroutine = await start_bridge(
        mqtt_handler = mqtt_handler,
        midi_handler = midi_handler)

    loop = asyncio.get_event_loop()

    try:
        # TODO Not working
        loop.run_until_complete(coroutine)
    # Quit midi smoothly
    except KeyboardInterrupt:
        
        pass
    finally:
        midi_handler.close()
        raise SystemExit()

if __name__ == '__main__':
    # Start Midi handler
    keymap = None
    midi_handler = APCMK2Handler()

    # MQTT Handler
    mqtt_handler = MQTTHandler(broker=MQTT_BROKER)

    asyncio.run(main())
