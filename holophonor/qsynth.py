from holophonor import holoimpl
from holophonor.launchpadX import DRUM_PATCH_COLORS
from rtmidi.midiutil import open_midioutput
from rtmidi.midiconstants import PROGRAM_CHANGE

class Qsynth:
    def __init__(self, hook, port, client_name='qsynth', **kwargs):
        self.hook = hook
        self.midi, self.name = open_midioutput(port, client_name=client_name)
    
    @holoimpl
    def playNote(self, note: tuple):
        self.midi.send_message(note)
    
    @holoimpl
    def setDrumPatch(self, patch: int):
        self.midi.send_message([PROGRAM_CHANGE | 0x9, DRUM_PATCH_COLORS[patch]])