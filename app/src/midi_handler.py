from rtmidi.midiutil import open_midiinput, open_midioutput
from rtmidi import MidiOut
from tools import std_out

MIDI_PORT_NAME = 'Midi Through '

class MIDIHandler():

    def __init__(self, port=MIDI_PORT_NAME):
        self.port = port
        self.midi_in, _ = open_midiinput(self.port)
        self.midi_out, _ = open_midioutput(self.port)

    def send(self, note):
        # TODO Limits
        self.midi_out.send_message(note)
