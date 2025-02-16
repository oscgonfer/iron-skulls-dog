import sys
import asyncio
from config import *
from tools import display_data, std_out
import json
import asyncio

async def handle_echo(reader, writer):
    data = await reader.read(10000) # READ as much as we can
    message = json.loads(data.decode())
    std_out (message)
    addr = writer.get_extra_info('peername')

    std_out (f"Received {message!r} from {addr!r}")

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

    std_out(f'Serving on {addrs}', True)

    async with server:
        await server.serve_forever()

asyncio.run(main())

