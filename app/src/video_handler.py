import cv2
from imagezmq import ImageSender

import numpy as np
from config import *
from aiortc import MediaStreamTrack
import time
import base64
import asyncio

class VideoHandler:
    def __init__(self, dog, server="tcp://localhost:5555"):
        self.dog = dog
        self.server = server
        self.sender = ImageSender(
                connect_to="tcp://{}:{}".format(
                ZEROMQ_BROKER,
                ZEROMQ_PORT
            )
        )

    async def recv_camera_stream(self, track: MediaStreamTrack):
        while True:
            try:
                frame = await track.recv()
                # Convert the frame to a NumPy array
                img = frame.to_ndarray(format="bgr24")
                # print(f"Shape: {img.shape}, Dimensions: {img.ndim}, Type: {img.dtype}, Size: {img.size}")
                _, jpg_buffer = cv2.imencode('.jpg', img)
                hub_reply = self.sender.send_jpg(self.server, jpg_buffer)
                print (hub_reply)
            except Exception as e:
                print ('Issue', e)
                pass
            await asyncio.sleep(0.01)

    # Define a callback function to handle LIDAR messages when received.
    def lidar_callback(self, message):
        # Print the data received from the LIDAR sensor.
        print(message["data"])



