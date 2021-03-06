from holophonor import holoimpl
from holophonor.holospecs import Holophonor
from holophonor.constants import NUMBER_LOOPS
from rtmidi.midiconstants import NOTE_ON, NOTE_OFF, POLY_AFTERTOUCH, CONTROL_CHANGE, PROGRAM_CHANGE


class Fweelin(Holophonor):
    @holoimpl
    def playLoop(self, loop: int, volume: int):
        self.midi.send_message([NOTE_ON, loop, volume])
        self.loops[loop] = volume
        
    @holoimpl
    def stopLoop(self, loop: int):
        self.playLoop(loop, 127)
        self.loops[loop] = 0
    
    @holoimpl
    def recordLoop(self, loop: int):
        self.playLoop(loop, 127)
        self.loops[loop] = 0
    
    @holoimpl
    def eraseLoop(self, loop: int):
        self.playLoop(loop, 127)
        self.loops[loop] = None
    
    @holoimpl
    def startLoopInCutMode(self, loop: int, volume: int):
        self.midi.send_message([CONTROL_CHANGE, 118, 0])
        self.midi.send_message([NOTE_ON, loop, volume])
        self.midi.send_message([CONTROL_CHANGE, 118, 127])
    
    @holoimpl
    def overdubLoop(self, loop: int):
        self.playLoop(loop, 127)
        
    @holoimpl
    def recallScene(self, scene: int):
        self.current_scene = scene
        s = self.scenes[scene]
        for l in range(NUMBER_LOOPS):
            if self.loops[l] != None:
                # loop exists
                if s[l] != self.loops[l]:
                    # loop needs to be changed
                    if s[l] in (0, None):
                        if self.loops[l] > 0:
                            # stop loop
                            self.stopLoop(l)
                    elif s[l] != None and self.loops[l] == 0:
                        # start loop
                        self.playLoop(l, s[l])
                    else:
                        # change volume
                        # send two messages: stop, then start
                        self.stopLoop(l)
                        self.playLoop(l, s[l])
    @holoimpl
    def storeScene(self, scene: int):
        self.current_scene = scene
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
    
    @holoimpl
    def tapPulse(self):
        self.midi.send_message([CONTROL_CHANGE, 95, 127])
    
    @holoimpl
    def toggleMute(self, channel: int):
        self.midi.send_message([CONTROL_CHANGE, 56  + channel, 0 if self.mutes[channel] else 127])
        self.mutes[channel] = not self.mutes[channel]
    
