from holophonor import holoimpl
from holophonor.holospecs import Holophonor
from rtmidi.midiutil import open_midiinput
from rtmidi.midiconstants import NOTE_ON


class LaunchpadX(Holophonor):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.live = False
        self.toggleLive()
        self.map = []
        n = 81
        for y in range(4):
            for x in range(8):
                self.map.append(n + x)
            n -= 10
        self.input, self.input_name = open_midiinput(self.port)
        self.input.set_callback(self)
    def toggleLive(self):
        # switch to / from programming / Live mode
        self.midi.send_message([240, 0, 32, 41, 2, 12, 14, 0 if self.live else 1, 247])
        self.live = not self.live
    
    @holoimpl    
    def close(self):
        # exit programming mode
        self.midi.send_message([240, 0, 32, 41, 2, 12, 14, 0, 247])
    
    @holoimpl
    def triggerLoop(self, loop, volume):
        self.midi.send_message([NOTE_ON, self.map[loop - 1], volume])
    
    def __call__(self, event, data=None):
        message, deltatime = event
        print(message)
        if message[0] == NOTE_ON:
            if message[1] in self.map:
                l = self.map.index(message[1])
                self.hook.triggerLoop(loop=l, volume=message[2])