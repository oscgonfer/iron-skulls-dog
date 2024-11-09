from config import *
import datetime

def std_out(msg, priority=False):
    if DEBUG or priority:
        if TIMESTAMP:
            print (f"{datetime.datetime.now()}: {msg}")
        else:
            print (msg)