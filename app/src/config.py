# TODO
# Add ways for it to map movement to music and emit the sound via jack

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
DOG_FILTER = "/dog"
CMD_FILTER = "/cmd"
OUT_FILTER = "/out"

## Incoming topics

SPORT_FILTER = f"{DOG_FILTER}/sport/#"
SPORT_TOPIC = SPORT_FILTER.replace("/#","")

MOVE_FILTER = f"{DOG_FILTER}/move/#"
MOVE_TOPIC = MOVE_FILTER.replace("/#","")

SWITCHER_FILTER = f"{DOG_FILTER}/switch/#"
SWITCHER_TOPIC = SWITCHER_FILTER.replace("/#","")

VUI_FILTER = f"{DOG_FILTER}/vui/#"
VUI_TOPIC = VUI_FILTER.replace("/#","")

AVOIDANCE_FILTER = f"{CMD_FILTER}/avoidance/#"
AVOIDANCE_TOPIC = AVOIDANCE_FILTER.replace("/#","")

CAPTURE_FILTER = f"{CMD_FILTER}/capture/#"
CAPTURE_TOPIC = CAPTURE_FILTER.replace("/#","")

AUDIO_FILTER = f"{CMD_FILTER}/audio/#"
AUDIO_TOPIC = AUDIO_FILTER.replace("/#","")

SAFE_FILTER = f"{CMD_FILTER}/safety/#"
RESUME_TOPIC = SAFE_FILTER.replace("#","resume")
STOP_TOPIC = SAFE_FILTER.replace("#","stop")

INCOMING_TOPICS = {
    RESUME_TOPIC: 'async',
    STOP_TOPIC: 'async',
    SPORT_TOPIC: 'async',
    MOVE_TOPIC: 'sync',
    SWITCHER_TOPIC: 'async',
    CAPTURE_TOPIC: 'capture',
    VUI_TOPIC: 'sync',
    AVOIDANCE_TOPIC: 'async',
    AUDIO_TOPIC: 'audio'
}

## Outgoing topics
STATE_FILTER = f"{OUT_FILTER}/state/#"
STATE_TOPIC = STATE_FILTER.replace("/#","")

MODE_FILTER = f"{OUT_FILTER}/mode/#"
MODE_TOPIC = MODE_FILTER.replace("/#","")

RESPONSE_FILTER = f"{OUT_FILTER}/response/#"
RESPONSE_TOPIC = RESPONSE_FILTER.replace("/#","")

MPC_FILTER = f"{OUT_FILTER}/mpc/#"
MPC_TOPIC = MPC_FILTER.replace("/#","")

# TODO Make something to add who listens where here?
# ---------------------------------------------------
