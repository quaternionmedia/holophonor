from holophonor import holoimpl
from holophonor.launchpadX import LaunchpadX
from itertools import chain

SCENES = list(range(8, 121, 16))
FUNCTIONS = list(range(104, 112))
DRUMS = [i for i in chain.from_iterable([list(range(x, x+4)) for x in list(range(64, 113, 16))])]

DRUM_BANKS = [69, 79, 35, 15, 59]
DRUM_PATCHES = list(range(100, 104))
DRUM_PATCH_COLORS = [32, 24, 25, 56]
FX = [i for i in chain.from_iterable([list(range(x, x+4)) for x in list(range(68, 113, 16))])]
MUTES = list(range(116, 120))

RECORDING = 15
ERASE = 47
GREEN = list(range(28, 61, 16)) + [60]
STOPPED = 46
EMPTY = 0
CUT = 63
PULSE = 60
TAP = 62

UP_ARROW = 104
DOWN_ARROW = 105
LEFT_ARROW = 106
RIGHT_ARROW = 107
SESSION_BUTTON = 108
NOTE_BUTTON = 109
CUSTOM_BUTTON = 110
CAPTURE_MIDI_BUTTON = 111

class LaunchpadS(LaunchpadX):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.map = []
        n = 0
        for y in range(4):
            for x in range(8):
                self.map.append(n + x)
            n += 16
        self.input, self.input_name = open_midiinput(self.port, client_name='launchpadS->holo')
        self.input.set_callback(self)
        self.drum_bank = 0
        self.drum_patch = 0
        self.fx = [False]*8
        self.clear()
        self.lightDrums()
    
    @holoimpl
    def recordLoop(self, loop):
        self.midi.send_message([NOTE_ON, self.map[loop], RECORDING])
        self.loops[loop] = 0
    
    @holoimpl
    def playLoop(self, loop, volume):
        self.midi.send_message([NOTE_ON, self.map[loop], GREEN[volume >> 5]])
        self.loops[loop] = volume
        if not self.pulse:
            self.pulse = True
            self.midi.send_message([CONTROL_CHANGE, 95, PULSE])
            self.midi.send_message([CONTROL_CHANGE, 99, PULSE])