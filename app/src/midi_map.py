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
    4: [WalkStair, SPORT_TOPIC],
    5: [WalkUpright, SPORT_TOPIC],
    6: [StandOut, SPORT_TOPIC],
    7: [RecoveryStand, SPORT_TOPIC],
    # Second row - 8-15
    8: [Damp, SPORT_TOPIC],
    9: [Wallow, SPORT_TOPIC],
    14: [SetObstacleAvoidance, AVOIDANCE_TOPIC],
    # Third row - 16-23
    16: [Dance1, SPORT_TOPIC],
    17: [Heart, SPORT_TOPIC],
    # Fourth row - 24-31
    24: [BalanceStand, SPORT_TOPIC],
    25: [StandUp, SPORT_TOPIC],
    26: [StandDown, SPORT_TOPIC],
    27: [Pose, SPORT_TOPIC]
}
