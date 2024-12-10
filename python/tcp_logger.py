import sys
import asyncio
from config import *
from tools import display_data
import json
import asyncio

async def handle_echo(reader, writer):
    data = await reader.read(10000) # READ as much as we can
    message = json.loads(data.decode())
    # if DEGUG:
    #     print (message)
    addr = writer.get_extra_info('peername')

    # if DEBUG:
    #     print(f"Received {message!r} from {addr!r}")
    try:
        display_data(message)
    except KeyError:
        raise RuntimeError("Can't process received message")
    finally:
        pass

async def main():
    server = await asyncio.start_server(
        handle_echo, LOGGER_IP, LOGGER_PORT)

    addrs = ', '.join(str(sock.getsockname()) for sock in server.sockets)
    print(f'Serving on {addrs}')

    async with server:
        await server.serve_forever()

asyncio.run(main())

