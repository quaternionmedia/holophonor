from pluggy import HookspecMarker
from rtmidi.midiutil import open_midioutput

holospec = HookspecMarker('holophonor')

class Holophonor:
    def __init__(self, hook, port, plugins=[]):
        self.port = port
        self.midi, self.name = open_midioutput(self.port, client_name='holo->fweelin')
        self.plugins = plugins
        self.loops = [None]*32
        self.scenes = [None]*8
    
    @holospec
    def triggerLoop(self, loop: int, volume: int):
        """trigger loop at volume"""
    
    @holospec
    def close(self):
        """close the connection"""