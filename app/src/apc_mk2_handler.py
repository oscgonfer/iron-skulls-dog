from rtmidi.midiutil import open_midiinput, open_midioutput
from rtmidi.midiconstants import NOTE_OFF, NOTE_ON, CONTROLLER_CHANGE
from rtmidi import MidiOut
from enum import Enum

class APCMK2ButtonName(Enum):
    VOLUME = 0x64
    PAN = 0x65
    SEND = 0x66
    DEVICE = 0x67
    UP = 0x68
    DOWN = 0x69
    LEFT = 0x6A
    RIGHT = 0x6B
    CLIP_STOP = 0x70
    SOLO = 0x71
    MUTE = 0x72
    REC_ARM = 0x73
    SELECT = 0x74
    DRUM = 0x75
    NOTE = 0x76
    STOP_ALL = 0x77
    SHIFT = 0x7a

class APCMK2FaderName(Enum):
    FADER_1 = 0x30
    FADER_2 = 0x31
    FADER_3 = 0x32
    FADER_4 = 0x33
    FADER_5 = 0x34
    FADER_6 = 0x35
    FADER_7 = 0x36
    FADER_8 = 0x37
    FADER_9 = 0x38

class APCMK2ButtonEffect(Enum):
    OFF = 0x00
    ON = 0x01
    BLINK = 0x02

class APCMK2PadEffect(Enum):
    ON_10 = 0x90
    ON_25 = 0x91
    ON_50 = 0x92
    ON_65 = 0x93
    ON_75 = 0x94
    ON_90 = 0x95
    ON_100 = 0x96
    PULSE_1_16 = 0x97
    PULSE_1_8 = 0x98
    PULSE_1_4 = 0x99
    PULSE_1_2 = 0x9A
    BLINK_1_24 = 0x9B
    BLINK_1_16 = 0x9C
    BLINK_1_8 = 0x9D
    BLINK_1_4 = 0x9E
    BLINK_1_2 = 0x9F

class APCMK2PadColor(Enum):
    BLACK = 0        #000000
    WHITE =  3       #FFFFFF
    RED =  5         #FF0000
    ORANGE =  9      #FF5400
    YELLOW = 13      #FFFF00
    GREEN = 17       #00FF00
    AQUA_GREEN = 29  #00FF55
    SKY_BLUE = 36    #4CC3FF
    BLUE = 45        #0000FF
    PURPLE = 53      #FF00FF
    LAVENDER = 57    #FF0054

MIDI_PORT_NAME = 'APC mini mk2:APC mini mk2 APC mini mk2 Contr 20:0'
APC_MK2_NUM_PADS = 64

class APCMK2Input():
    def __init__(self, channel: int, name: str):
        self.channel = channel
        self.name = name
        self.action =  None
        self.input_state: int = 0

class APCMK2Pad(APCMK2Input):
    def __init__(self, channel, name):
        self.effect: APCMK2PadEffect = APCMK2PadEffect.ON_100
        self.prev_effect: APCMK2PadEffect = APCMK2PadEffect.ON_100
        self.color: APCMK2PadColor = APCMK2PadColor.BLACK
        self.prev_color: APCMK2PadColor = APCMK2PadColor.BLACK
        super().__init__(channel, name)
    
    def to_dict(self):
        return {
            'effect': self.effect.name,
            'color': self.color.name,
            'channel': self.channel,
            'name': self.name,
            'action': self.action,
            'input_state': self.input_state
        }
    
class APCMK2Button(APCMK2Input):
    def __init__(self, channel, name):
        self.effect: APCMK2ButtonEffect = APCMK2ButtonEffect.OFF
        super().__init__(channel, name)

    def to_dict(self):
        return {
            'effect': self.effect.name,
            'channel': self.channel,
            'name': self.name,
            'action': self.action,
            'input_state': self.input_state
        }

class APCMK2Fader(APCMK2Input):
    def __init__(self, channel, name):
        super().__init__(channel, name)

    def to_dict(self):
        return {
            'channel': self.channel,
            'name': self.name,
            'action': self.action,
            'input_state': self.input_state
        }
    
class APCMK2Handler():
    def __init__(self, port=MIDI_PORT_NAME, keymap = None, propagate=True):
        self.port = port
        self.midi_in, _ = open_midiinput(self.port)
        self.midi_out, _ = open_midioutput(self.port)

        self.propagate = propagate

        self.pads = {item: APCMK2Pad(item, item) for item in range(APC_MK2_NUM_PADS)}
        self.buttons = {item.value: APCMK2Button(item.value, item.name) for item in APCMK2ButtonName}
        self.faders = {item.value: APCMK2Fader(item.value, item.name) for item in APCMK2FaderName}
        self._status = {}

        self.keymap = keymap
        self.init_inputs()
        self.midi_in.set_callback(self.message_callback)

    def init_inputs(self):
        # TODO validate keymap
        # TODO use keymap to start inputs / actions then update status
        self.update_status()
        
        if self.keymap is None:
            for pad in self.pads.values():
                # TODO decide init values
                effect=APCMK2PadEffect.ON_25
                if pad.channel<APC_MK2_NUM_PADS/2:
                    color=APCMK2PadColor.ORANGE
                else:
                    color=APCMK2PadColor.YELLOW
                self.light_pad(pad=pad,
                    effect=effect,
                    color=color
                )
            for button in self.buttons.values():
                self.light_button(button=button,
                    effect=APCMK2ButtonEffect.OFF
                )

    def close(self):
        self.midi.close_port()

    def light_pad(self, pad: APCMK2Pad, effect: APCMK2PadEffect, color: APCMK2PadColor):
        self.pads[pad.channel].prev_color = self.pads[pad.channel].color
        self.pads[pad.channel].prev_effect = self.pads[pad.channel].effect
        self.midi_out.send_message([effect.value, pad.channel, color.value])
        self.pads[pad.channel].color = color
        self.pads[pad.channel].effect = effect

    def light_button(self, button: APCMK2Button, effect: APCMK2ButtonEffect):
        self.midi_out.send_message([0x90, button.channel, effect.value])
    
    @property
    def status(self):
        # Representation of current apc in a dict with names
        return _status

    def update_status(self):
        for pad in self.pads.values():
            self._status[pad.name] = pad.to_dict()
        for button in self.buttons.values():
            self._status[button.name] = button.to_dict()
        for fader in self.faders.values():
            self._status[fader.name] = fader.to_dict()
        
        return self._status
    
    def message_callback(self, event, data=None):
        message, deltatime = event
        # MIDI_EVENT, CHANNEL, VALUE
        channel = int(message[1])
        value = int(message[2])

        if message[0] == CONTROLLER_CHANGE:
            if channel in self.faders:
                self.faders[channel].value = value
                print ('Fader:', self.faders[channel].name, self.faders[channel].value)
        elif message[0] == NOTE_OFF or message[0] == NOTE_ON:
            if channel in self.pads:
                # Pad pressed
                self.pads[channel].value = value
                print ('Pad:', self.pads[channel].name, self.pads[channel].value)

                # TODO Decide behaviour
                if self.pads[channel].action is None:
                    if message[0]==NOTE_ON:
                        self.light_pad(self.pads[channel], APCMK2PadEffect.ON_75, APCMK2PadColor.AQUA_GREEN)
                    elif message[1]:
                        self.light_pad(self.pads[channel], self.pads[channel].prev_effect, self.pads[channel].prev_color)
                
            elif channel in self.buttons:
                self.buttons[channel].value = value
                print ('Button:', self.buttons[channel].name, self.buttons[channel].value)

        self.update_status()

