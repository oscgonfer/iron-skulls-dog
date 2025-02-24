from command import *

# ---------------------------------------------------
# Config
DEBUG=True
TIMESTAMP=True
CAPTURE_PATH = 'capture'
# ---------------------------------------------------


# ---------------------------------------------------
# MQTT
MQTT_BROKER = "localhost"
MQTT_RECONNECT = 5

# Message filter
PRE_FILTER = "/dog"

## Incoming topics

SPORT_FILTER = f"{PRE_FILTER}/sport/#"
SPORT_TOPIC = SPORT_FILTER.replace("/#","")

MOVE_FILTER = f"{PRE_FILTER}/move/#"
MOVE_TOPIC = MOVE_FILTER.replace("/#","")

SWITCHER_FILTER = f"{PRE_FILTER}/switch/#"
SWITCHER_TOPIC = SWITCHER_FILTER.replace("/#","")

VUI_FILTER = f"{PRE_FILTER}/vui/#"
VUI_TOPIC = VUI_FILTER.replace("/#","")

CAPTURE_FILTER = f"{PRE_FILTER}/capture/#"
CAPTURE_TOPIC = CAPTURE_FILTER.replace("/#","")

# SAFE_FILTER = f"{PRE_FILTER}/safety/#"
# SAFE_TOPIC = SAFE_FILTER.replace("/#","")

INCOMING_TOPICS = {
    SPORT_TOPIC: 'async',
    MOVE_TOPIC: 'sync',
    SWITCHER_TOPIC: 'async',
    CAPTURE_TOPIC: 'capture',
    VUI_TOPIC: 'async'
}

## Outgoing topics

STATE_FILTER = f"{PRE_FILTER}/state/#"
STATE_TOPIC = STATE_FILTER.replace("/#","")

RESPONSE_FILTER = f"{PRE_FILTER}/response/#"
RESPONSE_TOPIC = RESPONSE_FILTER.replace("/#","")
# ---------------------------------------------------

# ---------------------------------------------------
# JOYSTICK
# 8bitDo SN30Pro+ Commands
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
# ---------------------------------------------------
