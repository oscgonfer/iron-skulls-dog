import asyncio
import websockets
from config import *

async def listen():
    async with websockets.connect(f'ws://{LOGGER_IP}:{LOGGER_PORT}/sub') as websocket:
        while True:
            greeting = await websocket.recv()
            print("< {}".format(greeting))

asyncio.get_event_loop().run_until_complete(listen())