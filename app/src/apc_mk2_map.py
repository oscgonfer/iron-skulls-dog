from command import *
from config import *

# Here the pads are numbered from 0 to 31 (both inclusive)
# Add a line to make a new command
# TODO Make this with pages? -> so that it depends on the DogMode? Or simply the pages?

pad_commands ={
    # First row - 0-7
    0: {'command': FreeWalk, "topic": SPORT_TOPIC},
    1: {'command': FreeBound, "topic": SPORT_TOPIC},
    2: {'command': FreeJump, "topic": SPORT_TOPIC},
    4: {'command': CrossWalk, "topic": SPORT_TOPIC},
    5: {'command': BackFlip, "topic": SPORT_TOPIC},
    6: {'command': FrontFlip, "topic": SPORT_TOPIC},
    7: {'command': RecoveryStand, "topic": SPORT_TOPIC},
    
    # Second row - 8-15
    8: {'command': StandOut, "topic": SPORT_TOPIC},
    9: {'command': WalkUpright, "topic": SPORT_TOPIC},
    10: {'command': PlayDogAudioFile, "topic": AUDIO_TOPIC, 
        "payload": {'audio_file': 'dog-barking'}
        },
    11: {'command': PlayClientAudioFile, "topic": AUDIO_TOPIC, 
        "payload": {'audio_file': 'dog-barking.wav'}
        },
    13: {'command': SwitchTrot, "topic": SPORT_TOPIC},
    14: {'command': SwitchRunning, "topic": SPORT_TOPIC},
    15: {'command': SetObstacleAvoidance, "topic": SPORT_TOPIC},

    # Third row - 16-23
    16: {'command': Hello, "topic": SPORT_TOPIC},
    17: {'command': Damp, "topic": SPORT_TOPIC},
    19: {'command': Dance1, "topic": SPORT_TOPIC},
    # 20: {'command': Dance2, "topic": SPORT_TOPIC},
    21: {'command': Content, "topic": SPORT_TOPIC},
    22: {'command': WiggleHips, "topic": SPORT_TOPIC},
    23: {'command': WalkStair, "topic": SPORT_TOPIC},
    
    # Fourth row - 24-31
    24: {'command': FrontJump, "topic": SPORT_TOPIC},
    25: {'command': Sit, "topic": SPORT_TOPIC},
    26: {'command': RiseSit, "topic": SPORT_TOPIC},
    27: {'command': Stretch, "topic": SPORT_TOPIC},
    28: {'command': FrontPounce, "topic": SPORT_TOPIC},
    30: {'command': Wallow, "topic": SPORT_TOPIC},
    31: {'command': Pose, "topic": SPORT_TOPIC},
    
}