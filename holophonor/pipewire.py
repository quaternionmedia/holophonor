from holophonor import holoimpl
from holophonor.holospecs import Holophonor


class Pipewire(Holophonor):
    @holoimpl
    def playLoop(self, loop: int, volume: int):
        '''play loop at volume'''

    @holoimpl
    def stopLoop(self, loop: int):
        '''pause loop'''

    @holoimpl
    def recordLoop(self, loop: int):
        '''record loop'''

    @holoimpl
    def eraseLoop(self, loop: int):
        '''erase the selected loop'''

    @holoimpl
    def clearLoop(self, loop: int):
        '''clear the button on release for the selected loop'''

    @holoimpl
    def overdubLoop(self, loop: int):
        '''overdub the selected loop'''

    @holoimpl
    def recallScene(self, scene: int):
        '''recall a scene'''

    @holoimpl
    def storeScene(self, scene: int):
        '''store a scene'''

    @holoimpl
    def eraseScene(self, scene: int):
        '''erase a scene'''

    @holoimpl
    def clearScene(self, scene: int):
        '''release the scene button'''

    @holoimpl
    def toggleShift(self):
        '''toggle shift mode'''

    @holoimpl
    def toggleCut(self):
        '''toggle cut mode'''

    @holoimpl
    def toggleOverdub(self):
        '''toggle overdub mode'''

    @holoimpl
    def deletePulse(self):
        '''delete pulse'''

    @holoimpl
    def clearPulse(self):
        '''release pulse button'''

    @holoimpl
    def stopAllLoops(self):
        '''stop all loops'''

    @holoimpl
    def tapPulse(self):
        '''tap pulse'''

    @holoimpl
    def toggleMute(self, channel: int):
        '''toggle mute on channel'''

    @holoimpl
    def toggleFX(self, fx: int):
        '''toggle fx'''

    @holoimpl
    def setDrumPatch(self, patch: int):
        '''set drum pad patch'''

    @holoimpl
    def setDrumBank(self, bank: int):
        '''set drum pad bank'''

    @holoimpl
    def playNote(self, note: tuple):
        '''play a synth note'''

    @holoimpl
    def clearNote(self, note: tuple):
        '''clear button from note'''

    @holoimpl
    def close(self):
        '''close the connection'''
