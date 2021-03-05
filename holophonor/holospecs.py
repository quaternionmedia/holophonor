from pluggy import HookspecMarker
from rtmidi.midiutil import open_midioutput

holospec = HookspecMarker('holophonor')

class Holophonor:
    def __init__(self, hook, port, plugins=[]):
        self.hook = hook
        self.port = port
        self.midi, self.name = open_midioutput(self.port, client_name='holo->fweelin')
        self.plugins = plugins
        self.loops = [None]*32
        self.scenes = [None]*8
        self.current_scene = None
        self.shift = False
        self.mutes = [False]*4
        self.overdub = False
        self.cut = False
        self.tap = False
    
    @holospec
    def triggerLoop(self, loop: int, volume: int):
        '''trigger loop at volume'''
    
    @holospec
    def triggerScene(self, scene: int):
        '''trigger a scene'''
        
    @holospec
    def eraseLoop(self, loop: int):
        '''erase the selected loop'''
    
    @holospec
    def clear(self):
        '''clear all loops'''
    
    @holospec
    def toggleOverdub(self, overdub=True):
        '''set overdub mode'''
    
    @holospec
    def toggleCut(self, cut=True):
        '''toggle cut mode'''
    
    @holospec
    def close(self):
        '''close the connection'''
    
    