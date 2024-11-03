from config import *
import datetime

def std_out(msg):
    if TIMESTAMP:
        print (f"{datetime.datetime.now()}: {msg}")
    else:
        print (msg)