
import os, sys, inspect, thread, time
import numpy as np
import mido
import time
import rtmidi
import re 

# the python-rtmidi
# https://github.com/SpotlightKid/python-rtmidi/tree/master/examples

# for note of MIDI to different octave

notes_dic = {'C':0, 'C#':1, 'D':2, 'D#':3, \
                'E':4, 'F':5, 'F#':6, 'G':7, \
                'G#':8, 'A':9, 'A#':10, 'B':11}

def create_note(midiout, pitch, sleep_time, velocity):
    note = re.findall('([A-Z|#]+)[0-9]+', pitch)[0]
    octave = int(re.findall('[A-Z|#]+([0-9]+)', pitch)[0])
    pitch_int = 12 * (1+octave) + notes_dic[note]
    note_on = [0x90, pitch_int, velocity] # channel 1, middle C, velocity 112
    note_off = [0x80, pitch_int, 0]
    midiout.send_message(note_on)
    time.sleep(sleep_time)
    midiout.send_message(note_off)

