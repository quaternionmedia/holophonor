from holophonor.holospecs import Holophonor
from holophonor import holoimpl
from rtmidi.midiutil import open_midioutput
from rtmidi.midiconstants import CONTROL_CHANGE
FX = [35, 36, 37, 38, 45, 46, 47, 48 ]

class Bitwig:
    def __init__(self, hook, port, client_name='bitwig', **kwargs):
        self.hook = hook
        self.midi, self.name = open_midioutput(port, client_name=client_name)
        self.fx = [False]*8
    @holoimpl
    def toggleFX(self, fx: int):
        self.midi.send_message([CONTROL_CHANGE, FX[fx], 0 if self.fx[fx] else 127])
        self.fx[fx] = not self.fx[fx]