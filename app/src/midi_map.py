from command import *
from config import *
from os import listdir
from os.path import isfile, join, dirname, realpath, splitext

# Here the pads are numbered from 0 to 31 (both inclusive)
# Add a line to make a new command
pad_commands ={
    # First row - 0-7
    0: [FreeWalk, SPORT_TOPIC],
    1: [FreeBound, SPORT_TOPIC],
    2: [FreeJump, SPORT_TOPIC],
    3: [FreeAvoid, SPORT_TOPIC],
    4: [WalkStair, SPORT_TOPIC],
    7: [RecoveryStand, SPORT_TOPIC],
    # Second row - 8-15

    # Third row - 16-23

    # Fourth row - 24-31
    24: [BalanceStand, SPORT_TOPIC],
    25: [StandUp, SPORT_TOPIC],
    26: [StandDown, SPORT_TOPIC]
}

file_path = dirname(realpath(__file__))
capture_path = join(file_path, CAPTURE_PATH)

cap_files = [int(splitext(f)[0]) for f in listdir(capture_path) if isfile(join(capture_path, f)) and splitext(f)[1] == '.cap' and splitext(f)[0].isdigit()]