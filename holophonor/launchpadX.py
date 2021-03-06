from holophonor import holoimpl
from holophonor.holospecs import Holophonor
from holophonor.constants import *
from rtmidi.midiutil import open_midiinput
from rtmidi.midiconstants import NOTE_ON, CONTROL_CHANGE

SCENES = [89, 79, 69, 59, 49, 39, 29, 19]
FUNCTIONS = [91, 92, 93, 94 , 95, 96, 97, 98]
DRUMS = [11, 12, 13, 14, 21, 22, 23, 24, 31, 32, 33, 34, 41, 42, 43, 44]
DRUM_BANKS = [69, 79, 35, 15, 59]
DRUM_PATCHES = [25, 26, 27, 28]
DRUM_PATCH_COLORS = [32, 24, 25, 56]
FX = [35, 36, 37, 38, 45, 46, 47, 48]
MUTES = [15, 16, 17, 18]

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
        self.input, self.input_name = open_midiinput(self.port, client_name='launchpad->holo')
        self.input.set_callback(self)
        self.drum_bank = 0
        self.drum_patch = 0
        self.fx = [False]*12
        self.clear()
        self.lightDrums()
    
    def toggleLive(self):
        # switch to / from programming / Live mode
        self.midi.send_message([240, 0, 32, 41, 2, 12, 14, 0 if self.live else 1, 247])
        self.live = not self.live
    
    def clear(self):
        for i in self.map:
            self.midi.send_message([NOTE_ON, i, EMPTY])
        for i in range(len(self.mutes)):
            self.midi.send_message([NOTE_ON, i + 15, EMPTY if self.mutes[i] else RECORDING])
    
    def lightDrums(self):
        for i in DRUMS:
            self.midi.send_message([NOTE_ON, i, DRUM_BANKS[self.drum_bank]])
        self.midi.send_message([NOTE_ON, 91, DRUM_BANKS[min(self.drum_bank + 1, 3)]])
        self.midi.send_message([NOTE_ON, 92, DRUM_BANKS[max(self.drum_bank - 1, -1)]])
    
    def lightButton(self, note):
        self.midi.send_message(note)
        
    @holoimpl    
    def close(self):
        # exit programming mode
        self.midi.send_message([240, 0, 32, 41, 2, 12, 14, 0, 247])
    
    @holoimpl
    def recordLoop(self, loop):
        self.midi.send_message([NOTE_ON | 0x2, self.map[loop], RECORDING])
        self.loops[loop] = 0
    
    @holoimpl
    def playLoop(self, loop, volume):
        self.midi.send_message([NOTE_ON | 0x2, self.map[loop], GREEN[volume >> 4]])
        self.loops[loop] = volume
        if not self.pulse:
            self.pulse = True
            self.midi.send_message([CONTROL_CHANGE, 95, PULSE])
    
    @holoimpl
    def stopLoop(self, loop):
        self.midi.send_message([NOTE_ON, self.map[loop], STOPPED])
        self.loops[loop] = 0
    
    @holoimpl
    def eraseLoop(self, loop):
        self.midi.send_message([NOTE_ON, self.map[loop], ERASE])
        self.loops[loop] = None
    
    @holoimpl
    def clearLoop(self, loop):
        self.midi.send_message([NOTE_ON, self.map[loop], EMPTY])
    
    @holoimpl
    def startLoopInCutMode(self, loop, volume):
        self.playLoop(loop, volume)
    
    @holoimpl
    def overdubLoop(self, loop: int):
        self.midi.send_message([NOTE_ON, self.map[loop], RECORDING])
        self.loops[loop] = -1

    @holoimpl
    def toggleShift(self):
        self.midi.send_message([CONTROL_CHANGE, 98, 0 if self.shift else ERASE])
        self.shift = not self.shift
    
    @holoimpl
    def toggleCut(self):
        self.midi.send_message([CONTROL_CHANGE, 96, 0 if self.cut else CUT])
        self.cut = not self.cut
    
    @holoimpl
    def toggleOverdub(self):
        self.midi.send_message([CONTROL_CHANGE, 97, 0 if self.overdub else RECORDING])
        self.overdub = not self.overdub
    
    @holoimpl
    def deletePulse(self):
        self.midi.send_message([CONTROL_CHANGE, 95, ERASE])
        self.clear()
        self.pulse = False
    
    @holoimpl
    def clearPulse(self):
        self.midi.send_message([CONTROL_CHANGE, 95, EMPTY])
    
    @holoimpl
    def tapPulse(self):
        self.midi.send_message([CONTROL_CHANGE, 95, TAP])
    
    @holoimpl
    def toggleMute(self, channel: int):
        self.midi.send_message([NOTE_ON, channel + 15, RECORDING if self.mutes[channel] else EMPTY])
        self.mutes[channel] = not self.mutes[channel]


    @holoimpl
    def toggleFX(self, fx: int):
        self.midi.send_message([NOTE_ON, FX[fx], EMPTY if self.fx[fx] else FX[fx]])
        self.fx[fx] = not self.fx[fx]

    @holoimpl
    def setDrumPatch(self, patch: int):
        self.midi.send_message([NOTE_ON, DRUM_PATCHES[patch], DRUM_PATCH_COLORS[patch]])
        for button in set(DRUM_PATCHES) - {DRUM_PATCHES[patch]}:
            self.midi.send_message([NOTE_ON, button, EMPTY])
        self.drum_patch = patch

    @holoimpl
    def setDrumBank(self, bank: int):
        self.drum_bank = bank
        self.lightDrums()
    
    def __call__(self, event, data=None):
        message, deltatime = event
        print(message)
        if message[0] == NOTE_ON:
            if message[1] in self.map:
                l = self.map.index(message[1])
                loop = self.loops[l]
                # self.hook.triggerLoop(loop=l, volume=message[2])
                if message[2]:
                    # note on event
                    if not self.shift:
                        # normal (unshifted) mode
                        if self.cut:
                            # cut mode
                            if loop in (0, None):
                                self.hook.startLoopInCutMode(loop=l, volume=message[2])
                            if loop == None:
                                # no existing loop, we are now recording.
                                self.hook.recordLoop(loop=l, volume=message[2])
                            else:
                                # loop was paused. Play now
                                self.hook.playLoop(loop=l, volume=message[2])
                            
                        else:
                            # normal (uncut) mode
                            if loop == None:
                                # no existing loop - start recording
                                # red - pulsing
                                self.hook.recordLoop(loop=l)
                            elif loop == -1:
                                # loop is overdubbing
                                # play at proper volume
                                self.hook.playLoop(loop=l, volume=message[2])
                            elif loop == 0:
                                # loop stopped (or recording)
                                if self.overdub:
                                    # overdub loop
                                    self.hook.overdubLoop(loop=l)
                                else:
                                    # start playing
                                    self.hook.playLoop(loop=l, volume=message[2])
                            else:
                                # loop is playing
                                if self.overdub:
                                    # overdub loop
                                    self.hook.overdubLoop(loop=l)
                                else:
                                    # stop loop
                                    self.hook.stopLoop(loop=l)
                    else:
                        # shift mode
                        # erase loop
                        self.hook.eraseLoop(loop=l)
                else:
                    # note off
                    # button released
                    if self.loops[l] == None:
                        # if we erased the loop, clear the color
                        self.hook.clearLoop(loop=l)
            elif message[1] in DRUMS:
                self.hook.playNote(note=[NOTE_ON | 0x9, 36 + DRUMS.index(message[1]) + self.drum_bank*16, message[2]])
                self.lightButton([NOTE_ON, message[1], message[2] if message[2] else DRUM_BANKS[self.drum_bank]])
            elif message[1] in FX and message[2]:
                f = FX.index(message[1])
                self.hook.toggleFX(fx=f)
            elif message[1] in DRUM_PATCHES and message[2]:
                i = DRUM_PATCHES.index(message[1])
                self.hook.setDrumPatch(patch=i)
            elif message[1] in MUTES and message[2]:
                n = message[1] - 15
                self.hook.toggleMute(channel=n)
            else:
                # no matching rule found for note
                pass
        elif message[0] == CONTROL_CHANGE:
            if message[1] in SCENES:
                s = SCENES.index(message[1])
                if message[2] == 127:
                    # scene button pressed
                    if self.shift:
                        # erase scene
                        self.hook.eraseScene(scene=s)
                    else:
                        # normal (unshifted) mode
                        if self.scenes[s]:
                            # recall scene
                            self.hook.recallScene(scene=s)
                        else:
                            # store scene
                            self.hook.storeScene(scene=s)
                else:
                    # scene button released
                    self.hook.clearScene(scene=s)
            elif message[1] in FUNCTIONS:
                if message[1] == 98:
                    # capture midi button
                    # enable shift mode
                    self.hook.toggleShift()
                if self.shift:
                    if message[1] == 95:
                        # erase session
                        # delete pulse
                        if message[2] == 127:
                            self.hook.deletePulse()
                        else:
                            self.hook.clearPulse()
                else:
                    # normal (unshifted) mode
                    if message[1] == 91 and message[2] == 127:
                        # arrow up button
                        # drum bank increment
                        self.hook.setDrumBank(bank=min(self.drum_bank + 1, 3))
                    elif message[1] == 92 and message[2] == 127:
                        # arrow down button
                        # drum bank decrement
                        self.hook.setDrumBank(bank=max(self.drum_bank - 1, -1))
                    elif message[1] == 96:
                        # note button
                        # momentary cut mode - normal on release
                        self.hook.toggleCut()
                    elif message[1] == 97 and message[2] == 127:
                        # custom button
                        # toggle overdub on button press
                        self.hook.toggleOverdub()
                    elif message[1] == 95:
                        # session button
                        # tap-pulse
                        if message[2] == 127:
                            self.hook.tapPulse()
