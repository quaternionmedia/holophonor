from holophonor.launchpadX import LaunchpadX
from holophonor.holospecs import Holophonor
from rtmidi.midiutil import open_midiinput
from rtmidi.midiconstants import NOTE_ON, CONTROL_CHANGE


class LaunchpadMK2(LaunchpadX):
    UP_ARROW = 104
    DOWN_ARROW = 105
    LEFT_ARROW = 106
    RIGHT_ARROW = 107
    SESSION_BUTTON = 108
    NOTE_BUTTON = 109
    CUSTOM_BUTTON = 110
    CAPTURE_MIDI_BUTTON = 111