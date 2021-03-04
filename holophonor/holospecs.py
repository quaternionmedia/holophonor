from pluggy import HookspecMarker

holospec = HookspecMarker('holophonor')

class Holophonor:
    def __init__(self):
        self.loops = [None]*32
        self.scenes = [None]*8
    
    @holospec
    def triggerLoop(self, loop: int, volume: int):
        """trigger loop at volume"""
    
    @holospec
    def close(self):
        """close the connection"""