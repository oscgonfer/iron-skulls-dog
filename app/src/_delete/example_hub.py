import asyncio
import random


class Hub():

    def __init__(self):
        self.subscriptions = set()

    def publish(self, message):
        for queue in self.subscriptions:
            queue.put_nowait(message)


class Subscription():

    def __init__(self, hub):
        self.hub = hub
        self.queue = asyncio.Queue()

    def __enter__(self):
        hub.subscriptions.add(self.queue)
        return self.queue

    def __exit__(self, type, value, traceback):
        hub.subscriptions.remove(self.queue)


async def reader(name, hub):

    await asyncio.sleep(random.random() * 15)
    print(f'Reader {name} has decided to subscribe now!')

    msg = ""
    with Subscription(hub) as queue:
        while msg != 'SHUTDOWN':
            msg = await queue.get()
            print(f'Reader {name} got message: {msg}')

            if random.random() < 0.1:
                print(f'Reader {name} has read enough')
                break

    print(f'Reader {name} is shutting down')


async def writer(iterations, hub):

    for x in range(iterations):
        print(f'Writer: I have {len(hub.subscriptions)} subscribers now')
        hub.publish(f'Hello world - {x}')
        await asyncio.sleep(3)
    hub.publish('SHUTDOWN')


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    hub = Hub()
    readers = [reader(x, hub) for x in range(10)]
    loop.run_until_complete(asyncio.gather(writer(10, hub), *readers))