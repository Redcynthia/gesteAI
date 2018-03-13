
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

pitchs_dic = {'left4':'C', 'left3':'D', 'left2':'E', 'left1':'F', 'left0':'F#', \
                'right0':'G', 'right1':'G#', 'right2':'A', 'right3':'A#', 'right4':'B'}


def create_note(midiout, pitch, sleep_time, velocity):
    note = re.findall('([A-Z|#]+)[0-9]+', pitch)[0]
    octave = int(re.findall('[A-Z|#]+([0-9]+)', pitch)[0])
    pitch_int = 12 * (1+octave) + notes_dic[note]
    note_on = [0x90, pitch_int, velocity] # channel 1, middle C, velocity 112
    note_off = [0x80, pitch_int, 0]
    midiout.send_message(note_on)
    time.sleep(sleep_time)
    midiout.send_message(note_off)


def on_play(midiout, frames, hand, finger_num, octave=5):

    frame = frames[0]
    previous_frame = frames[1]
    back_frame = frames[2]

    if hand == 'left':
        index_1 = frame.hands.leftmost.fingers[finger_num].bone(0).center
        index_2 = previous_frame.hands.leftmost.fingers[finger_num].bone(0).center
        index_3 = back_frame.hands.leftmost.fingers[finger_num].bone(0).center

    if hand == 'right':
        index_1 = frame.hands.rightmost.fingers[finger_num].bone(0).center
        index_2 = previous_frame.hands.rightmost.fingers[finger_num].bone(0).center
        index_3 = back_frame.hands.rightmost.fingers[finger_num].bone(0).center

    distance_to_palm_1 = frame.hands.leftmost.palm_position.distance_to(index_1)
    distance_to_palm_2 = frame.hands.leftmost.palm_position.distance_to(index_2)
    delta_t = previous_frame.timestamp - back_frame.timestamp

    velo_ = (index_2.y - index_3.y)*1e6/delta_t
    velo_abs = abs(velo_)*127/500
    #and velo_abs > 20
    if (index_2.y-index_1.y)*(index_3.y-index_2.y)<0  and distance_to_palm_1 - distance_to_palm_2 > 1 and index_2.y < 100:   
        print(finger_num, velo_abs, index_2.y)
        print distance_to_palm_1, distance_to_palm_2
        pitch = pitchs_dic[hand + str(finger_num)]+str(octave)
        create_note(midiout, pitch, 0.1, 50)
