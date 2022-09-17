from holophonor import holoimpl
from rtmidi.midiutil import open_midioutput
from rtmidi.midiconstants import PROGRAM_CHANGE
from rtmidi import API_UNIX_JACK


class Qsynth:
    DRUM_PATCH_COLORS = [32, 24, 25, 56]

    def __init__(self, hook, port, client_name='qsynth', **kwargs):
        self.hook = hook
        self.midi, self.name = open_midioutput(
            port, client_name=client_name, api=API_UNIX_JACK
        )

    @holoimpl
    def playNote(self, note: tuple):
        self.midi.send_message(note)

    @holoimpl
    def setDrumPatch(self, patch: int):
        self.midi.send_message([PROGRAM_CHANGE | 0x9, self.DRUM_PATCH_COLORS[patch]])
