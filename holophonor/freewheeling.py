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
    
    
