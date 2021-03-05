from holophonor import holoimpl
from holospecs import Holophonor
from rtmidi.midiconstants import NOTE_ON, NOTE_OFF, POLY_AFTERTOUCH, CONTROL_CHANGE, PROGRAM_CHANGE


class Fweelin(Holophonor):
    # def __init__(self, *args, **kwargs):
    #     super().__init__(*args, **kwargs)
        
        
        
    @holoimpl
    def triggerLoop(self, loop, volume):
        self.midi.send_message([NOTE_ON, loop, volume])
    