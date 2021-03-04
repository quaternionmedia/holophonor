from holophonor import holoimpl
from holophonor.holospecs import Holophonor
from rtmidi.midiutil import open_midioutput
from rtmidi.midiconstants import NOTE_ON


class LaunchpadX(Holophonor):
    def __init__(self, port, plugins=[]):
        super().__init__()
        self.port = port
        self.midi, self.name = open_midioutput(self.port, client_name='holo->launchpadX')
        self.plugins = plugins
        self.live = False
        self.toggleLive()
        self.map = []
        n = 81
        for y in range(4):
            for x in range(8):
                self.map.append(n + x)
            n -= 10
    def toggleLive(self):
        # switch to / from programming / Live mode
        self.midi.send_message([240, 0, 32, 41, 2, 12, 14, 0 if self.live else 1, 247])
        self.live = not self.live
    @holoimpl    
    def close(self):
        if self.live:
            self.toggleLive()
    @holoimpl
    def triggerLoop(self, loop, volume):
        self.midi.send_message([NOTE_ON, self.map[loop - 1], volume])
