from holophonor import holoimpl
from holophonor.holospecs import Holophonor
from holophonor.constants import NUMBER_LOOPS, NUMBER_SCENES
from rtmidi.midiconstants import (
    NOTE_ON,
    NOTE_OFF,
    POLY_AFTERTOUCH,
    CONTROL_CHANGE,
    PROGRAM_CHANGE,
)
from time import sleep


class Fweelin(Holophonor):
    @holoimpl
    def playLoop(self, loop: int, volume: int):
        if self.loops[loop] and self.loops[loop] != volume:
            # loop was playing at a differet volume
            # stop first
            self.stopLoop(loop)
        self.midi.send_message([NOTE_ON, loop, volume if volume > 0 else 100])
        self.loops[loop] = volume

    @holoimpl
    def stopLoop(self, loop: int):
        if self.loops[loop]:
            self.midi.send_message([NOTE_ON, loop, 1])
            if self.loops[loop] < 0:
                # loop was recording or overdubbing
                # send another message to stop
                sleep(0.01)
                self.midi.send_message([NOTE_ON, loop, 1])
            self.loops[loop] = 0

    @holoimpl
    def recordLoop(self, loop: int):
        if self.loops[loop] == None:
            self.playLoop(loop, 127)
            self.loops[loop] = -1

    @holoimpl
    def eraseLoop(self, loop: int):
        if self.loops[loop] is not None:
            self.toggleShift()
            self.playLoop(loop, 127)
            self.toggleShift()
            self.loops[loop] = None

    @holoimpl
    def overdubLoop(self, loop: int):
        self.toggleOverdub()
        self.midi.send_message([NOTE_ON, loop, 127])
        self.toggleOverdub()
        self.loops[loop] = -2

    @holoimpl
    def recallScene(self, scene: int):
        if self.current_scene and self.scenes[self.current_scene] == -1:
            # store changes to old scene
            self.scenes[self.current_scene] = self.loops.copy()
        self.current_scene = scene
        s = self.scenes[scene]
        for l in range(NUMBER_LOOPS):
            if self.loops[l] != None:
                # loop exists
                if s[l] != self.loops[l]:
                    # loop needs to be changed
                    if s[l] in (0, None):
                        if self.loops[l]:
                            # stop loop
                            self.stopLoop(l)
                    else:
                        # change volume
                        # if the loop is < 0 (recording, overdubbing)
                        # we have no volume information. Guess at 100
                        self.playLoop(l, s[l] if s[l] > 0 else 100)

    @holoimpl
    def storeScene(self, scene: int):
        if self.current_scene != None and self.scenes[self.current_scene] == -1:
            # store changes to old scene
            self.scenes[self.current_scene] = self.loops.copy()
        self.current_scene = scene
        if self.scenes[scene] == None:
            self.scenes[scene] = -1
        elif self.scenes[scene] == -1:
            self.scenes[scene] = self.loops.copy()

    @holoimpl
    def eraseScene(self, scene: int):
        self.scenes[scene] = None

    @holoimpl
    def toggleShift(self):
        self.midi.send_message([CONTROL_CHANGE, 98, 0 if self.shift else 127])
        self.shift = not self.shift

    @holoimpl
    def toggleCut(self):
        self.midi.send_message([CONTROL_CHANGE, 96, 0 if self.cut else 127])
        self.cut = not self.cut

    @holoimpl
    def toggleOverdub(self):
        self.midi.send_message([CONTROL_CHANGE, 97, 0 if self.overdub else 127])
        self.overdub = not self.overdub

    @holoimpl
    def deletePulse(self):
        self.midi.send_message([CONTROL_CHANGE, 108, 0])
        self.loops = [None] * NUMBER_LOOPS
        self.scenes = [None] * NUMBER_SCENES
        self.current_scene = None

    @holoimpl
    def tapPulse(self):
        self.midi.send_message([CONTROL_CHANGE, 95, 127])

    @holoimpl
    def stopAllLoops(self):
        for i, l in enumerate(self.loops):
            if l:
                self.stopLoop(i)

    @holoimpl
    def toggleMute(self, channel: int):
        self.midi.send_message(
            [CONTROL_CHANGE, 56 + channel, 0 if self.mutes[channel] else 127]
        )
        self.mutes[channel] = not self.mutes[channel]
