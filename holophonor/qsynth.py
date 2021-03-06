from holophonor import holoimpl
from rtmidi.midiutil import open_midioutput

class Qsynth:
    def __init__(self, hook, port, client_name='qsynth', **kwargs):
        self.hook = hook
        self.midi, self.name = open_midioutput(port, client_name=client_name)
    @holoimpl
    def playNote(self, note: tuple):
        self.midi.send_message(note)