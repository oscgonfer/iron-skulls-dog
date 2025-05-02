from rtmidi.midiutil import open_midiinput, open_midioutput
from rtmidi.midiconstants import NOTE_OFF, NOTE_ON, CONTROLLER_CHANGE
from rtmidi import MidiOut
from statemachine import StateMachine, Event
from statemachine.states import States

from tools import std_out
from apc_mk2_config import *
from apc_mk2_items import *
from capture import CaptureAction, CaptureCommand
import traceback

class APCMK2Handler(StateMachine):
    action_map = ACTION_MAP.copy()
    
    _ = States.from_enum(APCMK2Mode, initial=APCMK2Mode.normal)

    ev_normal = _.record.to(_.normal)

    ev_preview = _.normal.to(_.preview)
    ev_finish_preview = _.preview.to(_.normal)

    ev_record = _.normal.to(_.record)
    ev_finish_record = _.record.to(_.normal)

    ev_recording = _.record.to(_.recording)
    ev_finish_recording = _.recording.to(_.normal)

    ev_stop = _.normal.to(_.stop)
    ev_finish_stop = _.stop.to(_.normal)

    _status = {}

    _dog_mode = None # DogMode in dog.py Normal, Advance, AI
    _dog_state = None # DogState in dog.py

    def __init__(self, port=APC_PORT_NAME):
        self.port = port
        self.midi_in, _ = open_midiinput(self.port)
        self.midi_out, _ = open_midioutput(self.port)
        self.midi_in.set_callback(self.message_callback)
        # TODO Read status of the apc

        self.pads = {}
        self.buttons = {}
        self.faders = {}

        super(APCMK2Handler, self).__init__()
        
        self.assign_pads()
        self.assign_buttons()
        self.assign_faders()

        self.update_status()
        self.update_lights()

        self.target_pad = None
        self.locked = False

        for button in self.buttons:
            if self.buttons[button].action is None: continue
            if self.buttons[button].action.topic == RESUME_TOPIC:
                self.buttons[button].press()

    def on_transition(self,event_data, event: Event):
        assert event_data.event == event

        print (
            f"Running {event.name} from {event_data.transition.source.id} to "
            f"{event_data.transition.target.id}"
        )

    def lock(self):
        std_out('Locked')
        self.locked = True

    def unlock(self):
        std_out('Unlocked')
        self.locked = False

    def on_enter_state(self, event, state):
        if state.name not in ['Normal', 'Recording']:
            self.assign_recordings()
        self.assign_pads()
        # Buttons don't change?
        self.assign_buttons()
        self.update_lights()

    def after_transition(self, event, state):
        if state.name == 'Normal':
            for button in self.buttons:
                if self.buttons[button].action is None: continue
                if self.buttons[button].action.topic == RESUME_TOPIC:
                    self.buttons[button].press()
                    self.buttons[button].input_state = 127
        elif state.name == 'Stop':
            for button in self.buttons:
                if self.buttons[button].action is None: continue
                if self.buttons[button].action.topic == STOP_TOPIC:
                    self.buttons[button].press()
                    self.buttons[button].input_state = 127
                    print ('done')

        self.update_lights()

    def assign_recordings(self):
        cap_files = get_cap_files()
        for item in range(APC_MK2_NUM_PADS):
            if item <APC_MK2_NUM_PADS/2: continue
            if item in cap_files:
                self.action_map["normal"]["pads"][item] = APCMK2Action(command='play', payload=item, atype=APCMK2ActionType.subprocess)

                self.action_map["preview"]["pads"][item] = APCMK2Action(command='preview', payload=item, atype=APCMK2ActionType.subprocess)

                self.action_map["record"]["pads"][item] = APCMK2Action(command=None, atype=APCMK2ActionType.subprocess)

                self.action_map["recording"]["pads"][item] = APCMK2Action(command=None, atype=APCMK2ActionType.subprocess)
            else: 
                self.action_map["normal"]["pads"][item] = APCMK2Action(command=None, atype=APCMK2ActionType.unassigned)

                self.action_map["preview"]["pads"][item] = APCMK2Action(command=None, atype=APCMK2ActionType.unassigned)

                self.action_map["record"]["pads"][item] = APCMK2Action(command=CaptureCommand(action=CaptureAction.START, name=item), topic=CAPTURE_TOPIC, atype=APCMK2ActionType.capture)

                self.action_map["recording"]["pads"][item] = APCMK2Action(command=CaptureCommand(action=CaptureAction.STOP, name=item), topic=CAPTURE_TOPIC, atype=APCMK2ActionType.capture)
    
    def assign_pads(self):
        for item in range(APC_MK2_NUM_PADS):
            if item not in self.action_map[self.current_state.id]["pads"]: continue
            action = self.action_map[self.current_state.id]["pads"][item]
            _map = COLOR_EFFECT_MAP["pads"][self.current_state.id][action.type.name]

            self.pads[item] = APCMK2Pad(channel = item, name = item, action = self.action_map[self.current_state.id]["pads"][item], map = _map)

    def assign_buttons(self):
        for item in APCMK2ButtonName:
            if item.name not in self.action_map[self.current_state.id]["buttons"]: continue
            action = self.action_map[self.current_state.id]["buttons"][item.name]
            _map = COLOR_EFFECT_MAP["buttons"][self.current_state.id][action.type.name]

            self.buttons[item.value] = APCMK2Button(item.value, item.name, action = action, map = _map)

    def assign_faders(self):
        for item in APCMK2FaderName:
            if item.name not in self.action_map[self.current_state.id]["faders"]: continue 
            action = self.action_map[self.current_state.id]["faders"][item.name]
            self.faders[item.value] = APCMK2Fader(item.value, item.name, fader_defaults[item.name], action = action)
        
    def close(self):
        self.midi_in.close_port()
        self.midi_out.close_port()

    def update_dog_mode(self, mode):
        # Updates mode mode (Normal, Advanced, AI)
        if mode == 'null': self._dog_mode = None
        else: self._dog_mode = mode

        # TODO Associate available pads with DogMode?
        for button in self.buttons.values():
            if button.action.type == APCMK2ActionType.dog_mode_toggle:
                if self._dog_mode is not None:
                    if self._dog_mode in button.action.command.__name__.lower():
                        self.buttons[button.channel].press()
                    else:
                        self.buttons[button.channel].release()
                    self.light_button(button=button)

    def update_dog_state(self, state):
        # Updates value of DogState
        self._dog_state = state

        if self._dog_state == None: return
        
        for pad in self.pads.values():
            if pad.action.type == APCMK2ActionType.command:

                if pad.action.command is None: continue
                pad_cmd=pad.action.command()

                if pad_cmd.associated_states is None: continue

                if any([self._dog_state == cmd_assoc_state.value for cmd_assoc_state in pad_cmd.associated_states]):
                    self.pads[pad.channel].press()
                else:
                    self.pads[pad.channel].release()
            
        self.update_lights()
            
    def update_lights(self):
        for pad in self.pads.values():
            # if pad.trigger:
            #     print (pad.effect.value, pad.channel, pad.color.value)
            self.light_pad(pad=pad)
        for button in self.buttons.values():
            self.light_button(button=button)

    def light_pad(self, pad: APCMK2Pad):
        self.midi_out.send_message([pad.effect.value, pad.channel, pad.color.value])

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
        if self.locked: 
            std_out('WARNING: Locked')
            return
        
        action = self.pads[channel].action

        if self.target_pad is None:
            if action.type == APCMK2ActionType.capture:
                if note == NOTE_ON:
                    self.pads[channel].press()
                    self.target_pad = channel

        else:
            if action.type == APCMK2ActionType.capture:
                if note == NOTE_OFF and channel == self.target_pad and self.current_state.id == 'record':
                    self.send('ev_recording')
                    # We press here to make the impression we are still recording
                    self.pads[channel].press()

                elif note == NOTE_ON and channel == self.target_pad:
                    
                    self.action_map["normal"]["pads"][channel]=APCMK2Action(command='play', payload=f'{channel}', atype=APCMK2ActionType.subprocess)
                    self.action_map["preview"]["pads"][channel]=APCMK2Action(command='preview', payload=f'{channel}', atype=APCMK2ActionType.subprocess)

                    self.action_map["record"]["pads"][channel]=APCMK2Action(command=None,  atype=APCMK2ActionType.subprocess)
                    self.action_map["recording"]["pads"][channel]=APCMK2Action(command=None,  atype=APCMK2ActionType.subprocess)
                
                elif note == NOTE_OFF and channel == self.target_pad and self.current_state.id == 'recording':

                    # TODO Sometimes the recording doesn't get stored. Maybe because the thing is busy?
                    self.send('ev_finish_recording')
                    self.pads[channel].release()
                    self.target_pad = None
                
        self.update_lights()

    def trigger_button_action(self, note, channel, value):
        if self.locked: 
            std_out('Locked')
            return
        
        action = self.buttons[channel].action
        update_state = False
        # Careful when printing payloads, they don't always have names
        # print ('Triggered action:', action.payload.name)
        std_out ('Current state:', self.current_state)
        if action.type == APCMK2ActionType.apc_mode_toggle:
            if note == NOTE_ON:
                self.buttons[channel].press()
                self.send('ev_'+action.payload.name)
                
            elif note == NOTE_OFF:
                self.buttons[channel].release()
                self.send('ev_finish_'+action.payload.name)
                
        elif action.type == APCMK2ActionType.apc_mode_change:
            if note == NOTE_ON:
                std_out ('Sending', action.payload.name)
                self.send('ev_'+action.payload.name)
                # Workaround because buttons don't have a mapping
                if action.payload.name == 'normal':
                    self.buttons[channel].release()
                else:
                    self.buttons[channel].press()
        
        elif action.type == APCMK2ActionType.command:
            if note == NOTE_ON:
                if action.topic == RESUME_TOPIC:
                    self.send('ev_finish_'+action.payload.name)
                elif action.topic == STOP_TOPIC:
                    self.send('ev_'+action.payload.name)

        std_out ('Updated state:', self.current_state)
        self.update_lights()
    
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
                # print (f'Fader: ', self.faders[channel].name, self.faders[channel].input_state)
        
        elif note == NOTE_OFF or note == NOTE_ON:
            # Pad or button pressed
            if channel in self.pads:
                # Pad pressed
                self.pads[channel].input_state = value
                self.pads[channel].trigger = True
                std_out (f"Pad: {note} {self.pads[channel].name} {self.pads[channel].input_state} {self.pads[channel].trigger}")

                self.trigger_pad_action(note, channel, value)

            elif channel in self.buttons:
                # Button pressed
                self.buttons[channel].trigger = True
                self.buttons[channel].input_state = value
                std_out (f"Button: {self.buttons[channel].name} {self.buttons[channel].input_state}")
                self.trigger_button_action(note, channel, value)

        self.update_status()
