# https://cdn.inmusicbrands.com/akai/attachments/APC%20mini%20mk2%20-%20Communication%20Protocol%20-%20v1.0.pdf

brightness_10 = 0
brightness_25 = 1
brightness_50 = 2
brightness_100 = 7
pulsing_1_8 = 8
pulsing_1_4 = 9
pulsing_1_2 = 10
blinking_1_24 = 11
blinking_1_16 = 12
blinking_1_8 = 13
blinking_1_4 = 14
blinking_1_2 = 15

effectsArr = [
    brightness_10,
    brightness_25,
    brightness_50,
    brightness_100,
    pulsing_1_8,
    pulsing_1_4,
    pulsing_1_2,
    blinking_1_16,
    blinking_1_8,
    blinking_1_4,
    blinking_1_2,
]

colorsArr = [
    3, #White #FFFFFF
    5, #Red #FF0000
    9, #Orange #FF5400
    13, #Yellow #FFFF00
    17, #Green #00FF00
    29, #Aqua Green #00FF55
    36, #Sky Blue #4CC3FF
    41, #Blue 2 #0055FF
    45, #Blue #0000FF
    53, #Purple #FF00FF
    57, #Lavender #FF0054
]

import rtmidi
from rtmidi.midiconstants import NOTE_OFF, NOTE_ON
import time

midiout = rtmidi.MidiOut()

inports = range(midiin.get_port_count())
outports = range(midiout.get_port_count())

if inports and outports:
    for i in outports:
        portname = midiout.get_port_name(i)
        print("Found port " + str(i) + ":" + portname)
        if portname == "APC mini mk2:APC mini mk2 APC mini mk2 Contr 20:0":
            midiout.open_port(i)
            print("Opening port " + str(i) + "(APC mini mk2) as OUTPUT")
    channel = 0
    note = 0x64
    color = 24
    behaviour = 2

    while True:
        # m = midiin.get_message() # some timeout in ms
        print (channel)
        
        # midiout.send_message([NOTE_ON, channel, 21])
        midiout.send_message([0x96, channel, color])
        time.sleep(0.1)
        midiout.send_message([0x90, note, behaviour])

        channel +=1
        note +=1
        if channel==64: 
            channel = 0
            color+=1
        
        if note == 0x78:
            note = 0x64
            behaviour = 0

        time.sleep(0.1)
else:
    print('NO MIDI INPUT OR OUTPUT PORTS!')

