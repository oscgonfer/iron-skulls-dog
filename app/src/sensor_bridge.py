from config import *
from tools import std_out
import asyncio
import json
import os
from dotenv import load_dotenv
load_dotenv()

from rtmidi.midiconstants import NOTE_OFF, NOTE_ON, CONTROLLER_CHANGE
from midi_handler import MIDIHandler
from mqtt_handler import MQTTHandler
from subprocess_run import subprocess_run
import time
import datetime
from tools import get_by_path

sensor_map = {
    "/out/state/LF_SPORT_MOD_STATE": [
        {
            'field': 'LOW_STATE.foot_force',
            'midi_event': [NOTE_ON, NOTE_OFF],
            'notes': [55, None, None, None],
            'threshold': 50,
            'velocity': 2
        }
    ]
}

TIME_THD_US = 50000

async def sensor_bridge(midi_handler=None, queue=None, mqtt_handler=None):

    note_events = {'on': [], 'off': []}
    timer = datetime.datetime.now()
    while True:
        
        payload = None
        try:
            source, data = queue.get_nowait()
        except asyncio.QueueEmpty:
            pass
        else:
            if STATE_TOPIC in source.value:
                try:
                    _payload = json.loads(data)
                except json.decoder.JSONDecodeError:
                    std_out('Malformed payload. Ignoring')
                    pass
                else:
                    payload = _payload


        if payload is not None:
            for topic in sensor_map:
                for item in sensor_map[topic]:
                    field = item['field']
                    midi_event = item['midi_event']
                    notes = item['notes']
                    thd = item['threshold']
                    vel = item['velocity']

                    data = get_by_path(payload, field.split('.'))
                    print (data)

                    if type(data) == list and type(notes)==list:
                        if len(data) != len(notes):
                            print ('Bad mapping')
                            continue
                        idx = 0
                        for idx in range(len(data)):
                            if data[idx] > thd:
                                if notes[idx] not in note_events['on']:
                                    midi_handler.send([midi_event[0],
                                        notes[idx],
                                        vel
                                    ])
                                    note_events['on'].append(notes[idx])
                            else:
                                if notes[idx] not in note_events['off']:
                                    midi_handler.send([midi_event[1],
                                        notes[idx],
                                        vel
                                    ])
                                    note_events['off'].append(notes[idx])
            print (note_events)
        
        # This sleep is needed to receive mqtt commands. Could it be avoided with an additional task through the joystick_handler?
        await asyncio.sleep(0.0001)
        
        if datetime.datetime.now() - timer > datetime.timedelta(microseconds = TIME_THD_US):
            print ('timer cleared')
            for ev in note_events:
                note_events[ev] = []
            timer = datetime.datetime.now()

async def start_bridge(mqtt_handler = None, midi_handler = None):
    queue = asyncio.Queue()

    async with asyncio.TaskGroup() as tg:
        tg.create_task(mqtt_handler.bridge_incomming(topic=STATE_FILTER, queue=queue))
        tg.create_task(mqtt_handler.bridge_incomming(topic=MODE_FILTER, queue=queue))
        tg.create_task(mqtt_handler.bridge_incomming(topic=CAPTURE_FILTER, queue=queue))
        tg.create_task(sensor_bridge(midi_handler=midi_handler, queue=queue, mqtt_handler = mqtt_handler))

async def main():
    std_out('Starting midi coroutine...', priority=True)
    coroutine = await start_bridge(
        mqtt_handler = mqtt_handler,
        midi_handler = midi_handler)

    loop = asyncio.get_event_loop()

    try:
        loop.run_until_complete(coroutine)
    # Quit midi smoothly
    except KeyboardInterrupt:
        
        pass
    finally:
        midi_handler.close()
        raise SystemExit()

if __name__ == '__main__':
    midi_handler = MIDIHandler()

    # MQTT Handler
    mqtt_handler = MQTTHandler(broker=MQTT_BROKER)

    asyncio.run(main())
