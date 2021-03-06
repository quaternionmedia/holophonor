from holophonor import holoimpl
from holophonor.holospecs import Holophonor
from rtmidi.midiconstants import NOTE_ON, NOTE_OFF, POLY_AFTERTOUCH, CONTROL_CHANGE, PROGRAM_CHANGE


class Fweelin(Holophonor):
    @holoimpl
    def playLoop(self, loop: int, volume: int):
        self.midi.send_message([NOTE_ON, loop, volume])
        
    @holoimpl
    def stopLoop(self, loop: int):
        self.playLoop(loop, 127)
    
    @holoimpl
    def recordLoop(self, loop: int):
        self.playLoop(loop, 127)
    
    @holoimpl
    def eraseLoop(self, loop: int):
        self.playLoop(loop, 127)
    
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
        '''recall a scene'''
    
    @holoimpl
    def storeScene(self, scene: int):
        '''store a scene'''
    
    @holoimpl
    def eraseScene(self, scene: int):
        '''erase a scene'''
    
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
    
