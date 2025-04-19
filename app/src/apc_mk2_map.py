from command import *
from config import *


# Here the pads are numbered from 0 to 31 (both inclusive)
# Add a line to make a new command
# TODO Make this with pages? -> so that it depends on the DogMode (ai, advanced, normal)

pad_commands ={
    # First row - 0-7
    0: [FreeWalk, SPORT_TOPIC],
    1: [FreeBound, SPORT_TOPIC],
    2: [FreeJump, SPORT_TOPIC],
    3: [FreeAvoid, SPORT_TOPIC],
    4: [CrossWalk, SPORT_TOPIC],
    5: [BackFlip, SPORT_TOPIC],
    6: [FrontFlip, SPORT_TOPIC],
    7: [RecoveryStand, SPORT_TOPIC],
    # Second row - 8-15
    8: [StandOut, SPORT_TOPIC],
    9: [WalkUpright, SPORT_TOPIC],
    13: [SwitchTrot, SPORT_TOPIC],
    14: [SwitchRunning, SPORT_TOPIC],
    15: [SetObstacleAvoidance, SPORT_TOPIC],
   
    # Third row - 16-23
    16: [Hello, SPORT_TOPIC],
    17: [Heart, SPORT_TOPIC],
    18: [Damp, SPORT_TOPIC],
    19: [Dance1, SPORT_TOPIC],
    20: [Dance2, SPORT_TOPIC],
    21: [Content, SPORT_TOPIC],
    22: [WiggleHips, SPORT_TOPIC],
    23: [WalkStair, SPORT_TOPIC],
   
    # Fourth row - 24-31
    24: [FrontJump, SPORT_TOPIC],
    25: [Sit, SPORT_TOPIC],
    26: [RiseSit, SPORT_TOPIC],
    27: [Stretch, SPORT_TOPIC],
    28: [Wallow, SPORT_TOPIC],
    29: [Pose, SPORT_TOPIC],
    30: [FrontPounce, SPORT_TOPIC],
    31: [Scrape, SPORT_TOPIC],
}
