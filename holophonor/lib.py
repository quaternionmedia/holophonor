from holophonor import holoimpl
from holospecs import Holophonor
from rtmidi.midiutil import open_midioutput
from rtmidi.midiconstants import NOTE_ON, NOTE_OFF, POLY_AFTERTOUCH, CONTROL_CHANGE, PROGRAM_CHANGE


class Fweelin(Holophonor):
    def __init__(self, port, plugins=[]):
        super().__init__()
        self.port = port
        self.midi, self.name = open_midioutput(self.port, client_name='holo->fweelin')
        self.plugins = plugins
        
        
    @holoimpl
    def triggerLoop(self, loop, volume):
        self.midi.send_message([NOTE_ON, loop, volume])
    