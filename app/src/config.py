from command import *

# Config
DEBUG=False
TIMESTAMP=True
CAPTURE_PATH = 'capture'

# OSC Server IP and port
SERVER_IP = "127.0.0.1"
SERVER_PORT = 9996
OSSIA_PORT = 9997

# MQTT
MQTT_BROKER = "localhost"
MQTT_RECONNECT = 5

# TCP Message filter
PRE_FILTER = "/dog"

SPORT_FILTER = f"{PRE_FILTER}/sport*"
SPORT_TOPIC = SPORT_FILTER.replace("*","")

MOVE_FILTER = f"{PRE_FILTER}/move*"
MOVE_TOPIC = MOVE_FILTER.replace("*","")

SWITCHER_FILTER = f"{PRE_FILTER}/switch*"
SWITCHER_TOPIC = SWITCHER_FILTER.replace("*","")

VUI_FILTER = f"{PRE_FILTER}/vui*"
VUI_TOPIC = VUI_FILTER.replace("*","")

AUDIO_FILTER = f"{PRE_FILTER}/audio*"

SAFE_FILTER = f"{PRE_FILTER}/safety*"
SAFE_TOPIC = SAFE_FILTER.replace("*","")

CAPTURE_FILTER = f"{PRE_FILTER}/capture*"
CAPTURE_TOPIC = CAPTURE_FILTER.replace("*","")

STATE_FILTER = f"{PRE_FILTER}/state*"
STATE_TOPIC = STATE_FILTER.replace("*","")

VUI_CMD = {
    "Color": 1007,
    "Brightness": 1005,
    "SetVolume": 1003
}

# JOYSTICK
# 8bitDo SN30Pro+
JOY_SENSE = {
    "speed": 0.6,
    "roll": 0.75,
    "yaw": 0.6,
    "pitch": 0.75
}

VAL_LIMITS = {
    "speed": [0, 1],
    "roll": [0, 0.75],
    "yaw": [0, 0.6],
    "pitch": [0, 0.75]
}

BUTTONS = {
    0: "A",
    1: "B",
    2: "S",
    3: "X",
    4: "Y",
    6: "L1",
    7: "R1",
    8: "L2",
    9: "R2",
    10: "SELECT",
    11: "START",
    13: "LBALL",
    14: "RBALL"
}

AXES = {
    0: "Axis 0", # Left Axis right (-1)/left (1)
    1: "Axis 1", # Left Axis up (1)/down (-1)
    2: "Axis 2", # Right Axis right (-1)/left (1)
    3: "Axis 3"  # Right Axis up (1)/down (-1)
}

HATS = {
    0: "Hat 0"
    # First is left (-1) or right (1)
    # Second is up (1) or down (-1)
}

BALLS = {
}

DEF_JOY = {
    "A": 0,
    "B": 0,
    "S": 0,
    "X": 0,
    "Y": 0,
    "L1": 0,
    "R1": 0,
    "L2": 0,
    "R2": 0,
    "SELECT": 0,
    "START": 0,
    "LBALL": 0,
    "RBALL": 0,
    "Axis 0": 0,
    "Axis 1": 0,
    "Axis 2": 0,
    "Axis 3": 0,
    "Hat 0": (0, 0)
}

# Commands
BUTTON_CMD = {
    "A": StandDown,
    "B": StandUp,
    "S": None,
    "X": Sit,
    "Y": Hello,
    "L1": None,
    "R1": None,
    "L2": None,
    "R2": None,
    "SELECT": RecoveryStand,
    "START": None,
    "LBALL": BalanceStand,
    "RBALL": Pose
}

SAFETY_CMD = [

]
