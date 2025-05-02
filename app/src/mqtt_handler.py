import asyncio
import aiomqtt
from config import *
from tools import std_out

class MQTTHandler(object):
    def __init__(self, broker = 'localhost'):
        self.broker = broker
        self.reconnect_interval = MQTT_RECONNECT

    async def bridge_incomming(self, topic, queue):
        client = aiomqtt.Client(self.broker)
        while True:
            try:
                async with client:
                    std_out(f'Subscribing to {topic}', priority=True)
                    await client.subscribe(topic)
                    async for message in client.messages:
                        await queue.put((message.topic, message.payload))
            except aiomqtt.MqttError:
                std_out(f"Connection lost; Reconnecting in {self.reconnect_interval} seconds ...")
                await asyncio.sleep(self.reconnect_interval)

    async def publish(self, topic, payload):
        async with aiomqtt.Client(self.broker) as client:
            await client.publish(topic, payload=payload)

