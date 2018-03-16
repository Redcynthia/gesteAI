
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

fingers = ['thumb','index','middle','ring','picky']

finger_dist_to_palm = [1, 1.5, 1, 0.9, 1]
finger_y_flex = [2, 3, 3, 4, 3]


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
    back_5_frame = frames[3]


    if hand == 'left' and frame.hands.leftmost.is_left:
        index_1 = frame.hands.leftmost.fingers[finger_num].bone(3).center
        index_2 = previous_frame.hands.leftmost.fingers[finger_num].bone(3).center
        index_3 = back_frame.hands.leftmost.fingers[finger_num].bone(3).center
        index_5 = back_5_frame.hands.leftmost.fingers[finger_num].bone(3).center
        octave = (frame.hands.leftmost.palm_position.z + 40) // 30
        distance_to_palm_5 = back_5_frame.hands.leftmost.palm_position.distance_to(index_5)
        distance_to_palm_2 = previous_frame.hands.leftmost.palm_position.distance_to(index_2)
    elif hand == 'right' and frame.hands.rightmost.is_right:
        index_1 = frame.hands.rightmost.fingers[finger_num].bone(3).center
        index_2 = previous_frame.hands.rightmost.fingers[finger_num].bone(3).center
        index_3 = back_frame.hands.rightmost.fingers[finger_num].bone(3).center
        index_5 = back_5_frame.hands.rightmost.fingers[finger_num].bone(3).center
        octave = (frame.hands.leftmost.palm_position.z + 50) // 30
        distance_to_palm_5 = back_5_frame.hands.rightmost.palm_position.distance_to(index_5)
        distance_to_palm_2 = previous_frame.hands.rightmost.palm_position.distance_to(index_2)
    else:
        return

    #if finger_num == 0: print distance_to_palm_5, distance_to_palm_2
    #and velo_abs > 20 and distance_to_palm_1 - distance_to_palm_2 > 1\
            #and distance_to_palm_5 - distance_to_palm_2 > finger_dist_to_palm[finger_num] \
        #and index_5.y - index_2.y > finger_y_flex[finger_num] \
        #and distance_to_palm_5 - distance_to_palm_2 > finger_dist_to_palm[finger_num] \
        #and index_1.y < 60 \
    coeff = 2 #finger flex
    if hand == 'left': coeff = 2
    if finger_num == 0: distance_to_palm_2, distance_to_palm_5 = distance_to_palm_5, distance_to_palm_2
    if (index_1.y - index_2.y) * (index_2.y-index_3.y)<0 \
        and index_5.y - index_2.y > coeff*finger_y_flex[finger_num] \
        and distance_to_palm_5 - distance_to_palm_2 > finger_dist_to_palm[finger_num]:
        

        
        delta_t = (previous_frame.timestamp - back_frame.timestamp)/1e6
        velo_ = (index_2.y - index_3.y)/delta_t
        velo_abs = abs(velo_)*127/200
        if velo_abs > 127: velo_abs = 127
        if octave > 11: octave = 11
        if octave < 0: octave = 0
        #print "velo",velo_, velo_abs
        #print hand, finger_num, velo_abs, index_2.y
        #print frame.hands.leftmost.palm_position
        #print distance_to_palm_1, distance_to_palm_2
        pitch = pitchs_dic[hand + str(finger_num)]+str(int(octave))
        print hand, finger_num, pitch#ndex_5.y, index_2.y#, 
        create_note(midiout, pitch, delta_t, velo_abs)







