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
from dog import DogMode

async def midi_bridge(midi_handler=None, queue=None, mqtt_handler=None):
    dog_state = None

    while True:
        cmd = None
        # Get status of midi here
        midi_values = midi_handler.status.copy()
        if midi_values[0]['trigger']: print (midi_values[0]['trigger'])
        midi_handler.reset_triggers()
        
        try:
            # TODO Get state from dog (moving, not moving)
            # Get ai / not ai
            # Get capture status
            # Find a way to capture here when a command is running
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

        # If something happened...
        if any([midi_values[item]['trigger'] for item in midi_values]):
            # std_out(f"{[(midi_values[item]['name'], midi_values[item]['input_state'], midi_values[item]['trigger']) for item in midi_values]}")

            for midi_item in midi_values:
                _mi = midi_values[midi_item]
                if _mi['trigger']:
                    action = _mi["action"]
                    if action.type == APCMK2ActionType.command and action.command is not None:
                        if 'FADER' in str(_mi['name']):
                            cmd = action.command(_mi['input_state'], 
                            value_range = APC_MK2_FADER_LIMITS)
                        else:
                            if _mi['input_state']:
                                # Check status here? (AI vs not AI)
                                cmd = action.command()
                        
                        outgoing_topic = action.payload

        if cmd is not None:
            if midi_handler.current_state.id != 'preview':
                std_out (f'Robot command: {cmd.as_dict()}')
                await mqtt_handler.publish(topic=outgoing_topic, payload=cmd.to_json())
            else:
                std_out (f'PREVIEW: Command: {action.command.__name__}', priority = True, timestamp = False)
                print ()
                std_out (f'{action.command.__doc__}', priority = True, timestamp = False)
                print ()
        # This sleep is needed to receive mqtt commands. Could it be avoided with an additional task through the joystick_handler?
        await asyncio.sleep(0.001)

async def start_bridge(mqtt_handler = None, midi_handler = None):
    queue = asyncio.Queue()

    async with asyncio.TaskGroup() as tg:
        tg.create_task(mqtt_handler.bridge_incomming(topic=STATE_FILTER, queue=queue))
        tg.create_task(mqtt_handler.bridge_incomming(topic=CAPTURE_FILTER, queue=queue))
        tg.create_task(midi_bridge(midi_handler=midi_handler, queue=queue, mqtt_handler = mqtt_handler))

async def main():
    std_out('Starting midi coroutine...')
    coroutine = await start_bridge(
        mqtt_handler = mqtt_handler,
        midi_handler = midi_handler)

    loop = asyncio.get_event_loop()
    std_out('Bridge coroutine started')

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
