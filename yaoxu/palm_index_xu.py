################################################################################
# Copyright (C) 2012-2013 Leap Motion, Inc. All rights reserved.               #
# Leap Motion proprietary and confidential. Not for distribution.              #
# Use subject to the terms of the Leap Motion SDK Agreement available at       #
# https://developer.leapmotion.com/sdk_agreement, or another agreement         #
# between Leap Motion and you, your company or other organization.             #
################################################################################
import os, sys, inspect, thread, time
import numpy as np
import mido
import time
import rtmidi
src_dir = os.path.dirname(inspect.getfile(inspect.currentframe()))
# Windows and Linux
#arch_dir = '../lib/x64' if sys.maxsize > 2**32 else '../lib/x86'
# Mac
arch_dir = os.path.abspath(os.path.join(src_dir, '../../LeapSDK/lib'))

sys.path.insert(0, os.path.abspath(os.path.join(src_dir, arch_dir)))

import Leap, sys, thread, time
import midi
from Leap import CircleGesture, KeyTapGesture, ScreenTapGesture, SwipeGesture


class SampleListener(Leap.Listener):
    finger_names = ['Thumb', 'Index', 'Middle', 'Ring', 'Pinky']
    bone_names = ['Metacarpal', 'Proximal', 'Intermediate', 'Distal']
    state_names = ['STATE_INVALID', 'STATE_START', 'STATE_UPDATE', 'STATE_END']


    def on_init(self, controller):
        print "Initialized"

    def on_connect(self, controller):
        print "Connected"
        self.first_frame = controller.frame()
        self.first_timestamp = self.first_frame.timestamp
        self.note_num = 0

        self.midiout = rtmidi.MidiOut()
        self.midiout.open_virtual_port("To Ableton")

        # Enable gestures
        controller.enable_gesture(Leap.Gesture.TYPE_CIRCLE);
        controller.enable_gesture(Leap.Gesture.TYPE_KEY_TAP);
        controller.enable_gesture(Leap.Gesture.TYPE_SCREEN_TAP);
        controller.enable_gesture(Leap.Gesture.TYPE_SWIPE);

    def on_disconnect(self, controller):
        # Note: not dispatched when running in a debugger.
        print "Disconnected"

    def on_exit(self, controller):
        print "Exited"

    def on_frame(self, controller):
        # Get the most recent frame and report some basic information
        frame = controller.frame()
        previous_frame = controller.frame(1)
        last_frame = controller.frame(10)
        back_frame = controller.frame(20)

        #print "Frame id: %d, timestamp: %d, hands: %d, fingers: %d, tools: %d, gestures: %d" % (
        #      frame.id, frame.timestamp, len(frame.hands), len(frame.fingers), len(frame.tools), len(frame.gestures()))

        # direction of index finger
        index_1 = frame.hands.rightmost.fingers[1].bone(2).direction
        index_2 = last_frame.hands.rightmost.fingers[1].bone(2).direction
        index_3 = back_frame.hands.rightmost.fingers[1].bone(2).direction

        index_y_1 = frame.hands.rightmost.fingers[1].bone(0).center.y
        index_y_2 = last_frame.hands.rightmost.fingers[1].bone(0).center.y
        index_y_3 = back_frame.hands.rightmost.fingers[1].bone(0).center.y

        middle_1 = frame.hands.rightmost.fingers[2].bone(2).direction
        middle_2 = last_frame.hands.rightmost.fingers[2].bone(2).direction
        middle_3 = back_frame.hands.rightmost.fingers[2].bone(2).direction

        middle_y_1 = frame.hands.rightmost.fingers[2].bone(0).center.y
        middle_y_2 = last_frame.hands.rightmost.fingers[2].bone(0).center.y
        middle_y_3 = back_frame.hands.rightmost.fingers[2].bone(0).center.y

        # angle of these two finger vector
        if (index_1).angle_to(index_2)>np.pi/9 and (index_1).angle_to(index_3)<np.pi/15 and index_y_2 < index_y_3 and index_y_2 < index_y_1:
            print "index finger press action, direction vector: ", index_1, index_2, index_3
            # tick of midi is milli second 1e-3second, timestamp of frame is micro second 1e-6second
            #start_ = int((frame.timestamp - self.first_timestamp)/ 1000.0)
            #self.track.append(midi.NoteOnEvent(tick=50, velocity=50, pitch=midi.G_3))
            #self.track.append(midi.NoteOffEvent(tick=150, velocity=50, pitch=midi.G_3))
            note_on = [0x90, 60, 50] # channel 1, middle C, velocity 112
            note_off = [0x80, 60, 0]
            self.midiout.send_message(note_on)
            time.sleep(0.5)
            self.midiout.send_message(note_off)


        if (middle_1).angle_to(middle_2)>np.pi/10 and (middle_1).angle_to(middle_3)<np.pi/15 and middle_y_2 < middle_y_3 and middle_y_2 < middle_y_1:
            print "middle finger press action, direction vector: ", middle_1, middle_2, middle_3
            # tick of midi is milli second 1e-3second, timestamp of frame is micro second 1e-6second
            #start_ = int((frame.timestamp - self.first_timestamp)/ 1000.0)
            note_on = [0x90, 90, 50] # channel 1, middle C, velocity 112
            note_off = [0x80, 90, 0]
            self.midiout.send_message(note_on)
            time.sleep(0.5)
            self.midiout.send_message(note_off)

        # get the normal vector of the palm
        normal = frame.hands.rightmost.palm_normal
        previous_normal = previous_frame.hands.rightmost.palm_normal

        print normal[0], normal[1], normal[2]

        # stop is the palm normal is inversed
        if previous_normal[2] * normal[2] < 0:
            # end the track, add it to the midiout
            print "end track event, track adds to midiout"
            #self.track.append(midi.EndOfTrackEvent(tick=1))
            #self.midiout.append(self.track)
            # write midiout to file midi
            print "write midiout to file: "
            #outport = mido.open_output('To Ableton')
            #outport.send(self.midiout)
            #midi.write_midifile("example.mid", self.midiout)

            # stop the listener
            print "stop"
            controller.remove_listener(self)


    def state_string(self, state):
        if state == Leap.Gesture.STATE_START:
            return "STATE_START"

        if state == Leap.Gesture.STATE_UPDATE:
            return "STATE_UPDATE"

        if state == Leap.Gesture.STATE_STOP:
            return "STATE_STOP"

        if state == Leap.Gesture.STATE_INVALID:
            return "STATE_INVALID"

def main():
    # Create a sample listener and controller
    listener = SampleListener()
    controller = Leap.Controller()

    # Have the sample listener receive events from the controller
    controller.add_listener(listener)

    # Keep this process running until Enter is pressed

    print "Press Enter to quit..."
    try:
        sys.stdin.readline()
    except KeyboardInterrupt:
        pass

    finally:
        # Remove the sample listener when done
        controller.remove_listener(listener)


if __name__ == "__main__":
    main()
