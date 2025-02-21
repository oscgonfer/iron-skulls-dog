import asyncio
from websockets.asyncio.server import serve
from websockets import ConnectionClosed

from config import *
from tools import std_out
import json

connections = set()

async def relay(websocket):

    match websocket.request.path:
        case "/sub":

            connections.add(websocket)
            std_out (f'Adding connection {websocket.request}', True)

            try:
                async for msg in websocket:
                    pass  # ignore
            except ConnectionClosed:
                pass
            finally:
                connections.remove(websocket)
                std_out (f'Removing connection {websocket.request}', True)

        case "/pub":
            async for msg in websocket:
                std_out("<", msg)
                # TODO Think if we filter here the messages
                for ws in connections:
                    await ws.send(json.dumps(msg))

async def main():
    async with serve(relay, WS_IP, WS_PORT) as server:
        await server.serve_forever()

asyncio.run(main())
