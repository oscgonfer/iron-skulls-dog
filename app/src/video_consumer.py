import os
import cv2
import redis
import argparse
import numpy as np
import imagezmq
from config import *
import datetime

open_port = 'tcp://*:{}'.format(ZEROMQ_PORT)
image_hub = imagezmq.ImageHub(open_port=open_port)

now = datetime.datetime.now().strftime("%m%d%Y-%H%M%S")
fourcc = cv2.VideoWriter_fourcc(*'XVID')
vname = f'output-{now}.avi'
out = cv2.VideoWriter('video/' + vname, fourcc, 30.0, (1280, 720))

print('Open Port is {}'.format(image_hub))
print('Receiving frames...')
print(f'Video: {vname}')

hosts = {}
# show streamed images
while True:
    try:
        # tpye(jpg_buffer) is <class 'zmq.sugar.frame.Frame'>
        host_name, jpg_buffer = image_hub.recv_jpg()

        # image is 1-d numpy.ndarray and decode to 3-d array
        image = np.frombuffer(jpg_buffer, dtype='uint8')
        image = cv2.imdecode(image, -1)
        width, height, channel = image.shape

        if host_name not in hosts:
            hosts[host_name] = True
            print('Producer connected >>', host_name+':', width, height, channel)

        cv2.imshow('Dog', image)
        out.write(image)

        image_hub.send_reply(b'OK')

        # Quit
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    except Exception as ex:
        print(ex)

# Cleanup
image_hub.send_reply(b'CLOSED')
out.release()
cv2.destroyAllWindows()

