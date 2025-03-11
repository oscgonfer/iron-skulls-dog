from rtmidi.midiutil import open_midiinput, open_midioutput
from rtmidi.midiconstants import NOTE_OFF, NOTE_ON, CONTROLLER_CHANGE
from rtmidi import MidiOut


from tools import std_out
from apc_mk2_config import *

class APCMK2Handler():
    def __init__(self, port=MIDI_PORT_NAME):
        self.port = port
        self.midi_in, _ = open_midiinput(self.port)
        self.midi_out, _ = open_midioutput(self.port)
        self.midi_in.set_callback(self.message_callback)

        self._mode: APCMK2Mode = APCMK2Mode.normal
        
        self.pads = {}
        self.buttons = {}
        self.faders = {}

        for item in range(APC_MK2_NUM_PADS):
            if item not in ACTION_MAP[self._mode.name]["pads"]: continue
            action = ACTION_MAP[self._mode.name]["pads"][item]
            color = COLOR_EFFECT_MAP["pads"][self._mode.name][action.type.name]["idle"]["color"]
            effect = COLOR_EFFECT_MAP["pads"][self._mode.name][action.type.name]["idle"]["effect"]
            self.pads[item] = APCMK2Pad(channel = item, name = item, color = color, effect = effect, action = ACTION_MAP[self._mode.name]["pads"][item])
        
        for item in APCMK2ButtonName:
            if item.name not in ACTION_MAP[self._mode.name]["buttons"]: continue 
            action = ACTION_MAP[self._mode.name]["buttons"][item.name]
            effect = COLOR_EFFECT_MAP["buttons"][self._mode.name][action.type.name]["idle"]["effect"]
            self.buttons[item.value] = APCMK2Button(item.value, item.name, action = action)
        
        for item in APCMK2FaderName:
            if item.name not in ACTION_MAP[self._mode.name]["faders"]: continue 
            action = ACTION_MAP[self._mode.name]["faders"][item.name]
            self.faders[item.value] = APCMK2Fader(item.value, item.name, action = action)        
        
        self._status = {}
        self.update_status()
        self.show_lights()

    def close(self):
        self.midi_in.close_port()
        self.midi_out.close_port()

    def show_lights(self):
        for pad in self.pads.values():
            self.light_pad(pad=pad)
        for button in self.buttons.values():
            self.light_button(button=button)

    def light_pad(self, pad: APCMK2Pad):
        # self.pads[pad.channel].prev_color = self.pads[pad.channel].color
        # self.pads[pad.channel].prev_effect = self.pads[pad.channel].effect
        self.midi_out.send_message([pad.effect.value, pad.channel, pad.color.value])
        # self.pads[pad.channel].color = color
        # self.pads[pad.channel].effect = effect

    def light_button(self, button: APCMK2Button):
        self.midi_out.send_message([0x90, button.channel, button.effect.value])
    
    @property
    def status(self):
        # Representation of current apc in a dict with names
        return self._status
    
    def update_status(self):

        for pad in self.pads.values():
            self._status[pad.name] = pad.to_dict()
        for button in self.buttons.values():
            self._status[button.name] = button.to_dict()
        for fader in self.faders.values():
            self._status[fader.name] = fader.to_dict()

    def trigger_pad_action(self, note, channel, value):
        action = self.pads[channel].action
        # match self.mode:
        #     case APCMK2Mode.normal:
        #     case APCMK2Mode.edit:
        #     case APCMK2Mode.record:
        #     case APCMK2Mode.recording:
        #     case APCMK2Mode.preview:

    def change_mode(self, mode):
        print (mode)

    def trigger_button_action(self, note, channel, value):
        print (note, channel, value)
        print (self._mode)
        print (self.buttons[channel].name)
        action = self.buttons[channel].action
        print (action.command, action.payload, action.type)
        if action.type == APCMK2ActionType.change:
            print ("Mode change requested")
            self.change_mode(action.payload)
    
    def reset_triggers(self):
        for pad in self.pads.values():
            self.pads[pad.channel].trigger = False
        for button in self.buttons.values():
            self.buttons[button.channel].trigger = False
        for fader in self.faders.values():
            self.faders[fader.channel].trigger = False
        
        self.update_status()
    
    def message_callback(self, event, data=None):
        message, deltatime = event
        # MIDI_EVENT, CHANNEL, VALUE
        note = message[0]
        channel = int(message[1])
        value = int(message[2])

        if note == CONTROLLER_CHANGE:
            # Fader change
            if channel in self.faders:
                self.faders[channel].input_state = value
                self.faders[channel].trigger = True
                print (f'Fader: ', self.faders[channel].name, self.faders[channel].input_state)
        elif note == NOTE_OFF or note == NOTE_ON:
            # Pad or button pressed
            if channel in self.pads:
                # Pad pressed
                self.pads[channel].input_state = value
                self.pads[channel].trigger = True
                print ('Pad:', self.pads[channel].name, self.pads[channel].input_state, self.pads[channel].trigger)

                # # TODO Decide behaviour
                # if self.pads[channel].action is None:
                #     if note==NOTE_ON:
                #         self.pads[channel].color = APCMK2PadColor.AQUA_GREEN
                #         self.pads[channel].effect = APCMK2PadEffect.ON_75
                #     elif note==NOTE_OFF:
                #         self.pads[channel].color = APCMK2PadColor.AQUA_GREEN
                #         self.pads[channel].effect = APCMK2PadEffect.ON_50
                self.trigger_pad_action(note, channel, value)

            elif channel in self.buttons:
                # Button pressed
                self.buttons[channel].trigger = True
                self.buttons[channel].input_state = value
                print ('Button:', self.buttons[channel].name, self.buttons[channel].input_state)
                self.trigger_button_action(note, channel, value)

        self.update_status()
