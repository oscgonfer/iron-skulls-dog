import asyncio
import cv2
import numpy as np
from config import *
from aiortc import MediaStreamTrack
import time

# Create an OpenCV window and display a blank image
height, width = 720, 1280  # Adjust the size as needed
img = np.zeros((720, 1080, 3), dtype=np.uint8)
time.sleep(1)
cv2.imshow('Video', img)
cv2.waitKey(1)

class VideoHandler:
    def __init__(self, dog):
        self.dog = dog
        self.queue = Queue()

    async def recv_camera_stream(track: MediaStreamTrack):
        while True:
            frame = await track.recv()
            # Convert the frame to a NumPy array
            img = frame.to_ndarray(format="bgr24")
            self.queue.put(img)

    async def handle_frame(self):
        try:
            while True:
                if not self.queue.empty():
                    img = self.queue.get()
                    print(f"Shape: {img.shape}, Dimensions: {img.ndim}, Type: {img.dtype}, Size: {img.size}")
                    # Display the frame
                    cv2.imshow('Video', img)
                    if cv2.waitKey(1) & 0xFF == ord('q'):
                        break
                else:
                    # Sleep briefly to prevent high CPU usage
                    asyncio.sleep(0.01)
        except:
            pass


