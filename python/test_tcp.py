import asyncio
from config import *
import json

async def tcp_echo_client(message):
    reader, writer = await asyncio.open_connection(
        LOGGER_IP, LOGGER_PORT)

    print(f'Send: {message!r}')
    writer.write(json.dumps(message).encode())
    await writer.drain()

    data = await reader.read(100)
    print(f'Received: {data.decode()!r}')

    print('Close the connection')
    writer.close()
    await writer.wait_closed()


message = {'imu_state': {'rpy': 20}}
asyncio.run(tcp_echo_client(message))