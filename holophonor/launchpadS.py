from holophonor import holoimpl
from holophonor.holospecs import Holophonor
from holophonor.launchpadX import LaunchpadX
from itertools import chain
from rtmidi.midiutil import open_midiinput
from rtmidi.midiconstants import NOTE_ON, CONTROL_CHANGE
from rtmidi import API_UNIX_JACK


class LaunchpadS(LaunchpadX):
    SCENES = list(range(8, 121, 16))
    FUNCTIONS = list(range(104, 112))
    DRUMS = [
        i
        for i in chain.from_iterable(
            [list(range(x, x + 4)) for x in list(range(112, 63, -16))]
        )
    ]

    DRUM_BANKS = [45, 46, 47, 31, 32]
    DRUM_PATCHES = list(range(100, 104))
    DRUM_PATCH_COLORS = [45, 46, 47, 31]
    FX = [
        i
        for i in chain.from_iterable(
            [list(range(x, x + 4)) for x in list(range(68, 113, 16))]
        )
    ]
    MUTES = list(range(116, 120))

    RECORDING = 15
    ERASE = 47
    GREEN = list(range(28, 61, 16)) + [60]
    STOPPED = 46
    EMPTY = 12
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

    def __init__(self, *args, **kwargs):
        Holophonor.__init__(self, *args, **kwargs)
        self.map = []
        n = 0
        for y in range(4):
            for x in range(8):
                self.map.append(n + x)
            n += 16
        self.input, self.input_name = open_midiinput(
            self.port, client_name='launchpadS->holo', api=API_UNIX_JACK
        )
        self.input.set_callback(self)
        self.drum_bank = 0
        self.drum_patch = 0
        self.fx = [False] * 8
        # set to x-y layout
        self.setLayout(1)
        self.clear()
        self.lightDrums()

    def setLayout(self, layout):
        self.midi.send_message([CONTROL_CHANGE, 0, layout])

    @holoimpl
    def recordLoop(self, loop):
        self.midi.send_message([NOTE_ON, self.map[loop], self.RECORDING])
        self.loops[loop] = 0

    @holoimpl
    def playLoop(self, loop, volume):
        self.midi.send_message([NOTE_ON, self.map[loop], self.GREEN[volume >> 5]])
        self.loops[loop] = volume
        if not self.pulse:
            self.pulse = True
            self.midi.send_message([CONTROL_CHANGE, self.SESSION_BUTTON, self.PULSE])

    @holoimpl
    def recallScene(self, scene: int):
        # need to overwrite LaunchpadX implementation
        # because scene light can't recieve flashing signal
        if self.current_scene != None:
            self.midi.send_message(
                [CONTROL_CHANGE, self.SCENES[self.current_scene], self.STOPPED]
            )
        self.current_scene = scene
        self.midi.send_message([CONTROL_CHANGE, self.SCENES[scene], self.GREEN[-1]])
        s = self.scenes[scene]
        for l, b in enumerate(self.map):
            if self.loops[l] != None:
                # loop exists
                if s[l] != self.loops[l]:
                    # loop needs to be changed
                    if s[l] in (0, None):
                        if self.loops[l] > 0:
                            # stop loop
                            self.stopLoop(l)
                            self.loops[l] = 0
                    elif s[l] != None and self.loops[l] == 0:
                        # start loop
                        self.playLoop(l, s[l])
                    else:
                        # change the volume
                        self.playLoop(l, s[l])
                if s[l] in (0, None):
                    self.stopLoop(l)
                else:
                    self.playLoop(l, s[l])

    @holoimpl
    def close(self):
        # clear all lights on exit
        self.midi.send_message([CONTROL_CHANGE, 0, 0])
