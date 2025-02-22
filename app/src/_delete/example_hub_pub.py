import asyncio
import websockets
from config import *

async def say():
    async with websockets.connect(f'ws://{WS_IP}:{WS_PORT}/pub') as websocket:
        while True:
            msg = input("Enter message:")
            if not msg:
                break
            await websocket.send(msg)

asyncio.get_event_loop().run_until_complete(say())