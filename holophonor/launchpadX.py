from holophonor import holoimpl
from holophonor.holospecs import Holophonor
from holophonor.constants import *
from rtmidi.midiutil import open_midiinput
from rtmidi.midiconstants import NOTE_ON, CONTROL_CHANGE



class LaunchpadX(Holophonor):
    SCENES = [89, 79, 69, 59, 49, 39, 29, 19]
    FUNCTIONS = [91, 92, 93, 94 , 95, 96, 97, 98]
    DRUMS = [11, 12, 13, 14, 21, 22, 23, 24, 31, 32, 33, 34, 41, 42, 43, 44]
    DRUM_BANKS = [69, 79, 35, 15, 59]
    DRUM_PATCHES = [25, 26, 27, 28]
    DRUM_PATCH_COLORS = [32, 24, 25, 56]
    FX = [35, 36, 37, 38, 45, 46, 47, 48]
    MUTES = [15, 16, 17, 18]
    
    UP_ARROW = 91
    DOWN_ARROW = 92
    LEFT_ARROW = 93
    RIGHT_ARROW = 94
    SESSION_BUTTON = 95
    NOTE_BUTTON = 96
    CUSTOM_BUTTON = 97
    CAPTURE_MIDI_BUTTON = 98
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.map = []
        n = 81
        for y in range(4):
            for x in range(8):
                self.map.append(n + x)
            n -= 10
        self.live = False
        self.toggleLive()
        self.input, self.input_name = open_midiinput(self.port, client_name='launchpadX->holo')
        self.input.set_callback(self)
        self.drum_bank = 0
        self.drum_patch = 0
        self.fx = [False]*8
        self.clear()
        self.lightDrums()
    
    def toggleLive(self):
        # switch to / from programming / Live mode
        self.midi.send_message([240, 0, 32, 41, 2, 12, 14, 0 if self.live else 1, 247])
        self.live = not self.live
    
    def clear(self):
        for i in self.map:
            self.midi.send_message([NOTE_ON, i, EMPTY])
        for i in self.SCENES:
            self.midi.send_message([NOTE_ON, i, EMPTY])
        for i in range(len(self.mutes)):
            self.midi.send_message([NOTE_ON, self.MUTES[i], EMPTY if self.mutes[i] else RECORDING])
        self.midi.send_message([CONTROL_CHANGE, 99, 1])
        self.midi.send_message([CONTROL_CHANGE, self.LEFT_ARROW, STOPPED])
    
    def lightDrums(self):
        for i in self.DRUMS:
            self.midi.send_message([NOTE_ON, i, self.DRUM_BANKS[self.drum_bank]])
        self.midi.send_message([CONTROL_CHANGE, self.UP_ARROW, self.DRUM_BANKS[min(self.drum_bank + 1, 3)]])
        self.midi.send_message([CONTROL_CHANGE, self.DOWN_ARROW, self.DRUM_BANKS[max(self.drum_bank - 1, -1)]])
    
    def lightButton(self, note):
        self.midi.send_message(note)
        
    @holoimpl    
    def close(self):
        # exit programming mode
        self.midi.send_message([240, 0, 32, 41, 2, 12, 14, 0, 247])
    
    @holoimpl
    def recordLoop(self, loop):
        self.midi.send_message([NOTE_ON | 0x2, self.map[loop], RECORDING])
        self.loops[loop] = -1
    
    @holoimpl
    def playLoop(self, loop, volume):
        self.midi.send_message([NOTE_ON | 0x2, self.map[loop], GREEN[(volume if volume > 0 else 100 )>> 4]])
        self.loops[loop] = volume
        if not self.pulse:
            self.pulse = True
            self.midi.send_message([CONTROL_CHANGE, self.SESSION_BUTTON, PULSE])
            self.midi.send_message([CONTROL_CHANGE, 99, PULSE])
    
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
    def overdubLoop(self, loop: int):
        if self.loops[loop] != -2:
            self.midi.send_message([NOTE_ON, self.map[loop], RECORDING])
            self.loops[loop] = -2
        
    @holoimpl
    def recallScene(self, scene: int):
        if self.current_scene != None:
            self.midi.send_message([NOTE_ON, self.SCENES[self.current_scene], STOPPED])
        self.current_scene = scene
        self.midi.send_message([NOTE_ON | 0x2, self.SCENES[scene], GREEN[-1]])
        s = self.scenes[scene]
        for l in range(len(self.map)):
            if self.loops[l] != None:
                # loop exists
                if s[l] != self.loops[l]:
                    # loop needs to be changed
                    if s[l] in (0, None):
                        if self.loops[l]:
                            # stop loop
                            self.stopLoop(l)
                    elif self.loops[l] == 0:
                        # start loop
                        self.playLoop(l, s[l])
                    else:
                        # start loop (or change volume)
                        self.playLoop(l, s[l] if s[l] > 0 else 100)
    
    @holoimpl
    def storeScene(self, scene: int):
        if self.current_scene != None:
            self.midi.send_message([NOTE_ON, self.SCENES[self.current_scene], STOPPED])
        self.current_scene = scene
        self.scenes[scene] = self.loops.copy()
        self.midi.send_message([NOTE_ON, self.SCENES[scene], GREEN[-1]])
    
    @holoimpl
    def eraseScene(self, scene: int):
        self.midi.send_message([NOTE_ON, self.SCENES[scene], ERASE])
        self.scenes[scene] = None
        if self.current_scene == scene:
            self.current_scene = None
    
    @holoimpl
    def clearScene(self, scene: int):
        self.midi.send_message([NOTE_ON, self.SCENES[scene], EMPTY])
    
    @holoimpl
    def toggleShift(self):
        self.shift = not self.shift
        self.midi.send_message([CONTROL_CHANGE, self.CAPTURE_MIDI_BUTTON, ERASE if self.shift else 0])
    
    @holoimpl
    def toggleCut(self):
        self.cut = not self.cut
        self.midi.send_message([CONTROL_CHANGE, self.NOTE_BUTTON, CUT if self.cut else 0])
    
    @holoimpl
    def toggleOverdub(self):
        self.overdub = not self.overdub
        self.midi.send_message([CONTROL_CHANGE, self.CUSTOM_BUTTON, RECORDING if self.overdub else 0])
    
    @holoimpl
    def deletePulse(self):
        self.midi.send_message([CONTROL_CHANGE, self.SESSION_BUTTON, ERASE])
        self.clear()
        self.pulse = False
        self.loops = [None]*len(self.map)
        self.scenes = [None]*len(self.scenes)
        self.midi.send_message([CONTROL_CHANGE, 99, 1])
    
    @holoimpl
    def clearPulse(self):
        self.midi.send_message([CONTROL_CHANGE, self.SESSION_BUTTON, EMPTY])
    
    @holoimpl
    def stopAllLoops(self):
        for i, l in enumerate(self.loops):
            if l:
                self.midi.send_message([NOTE_ON, self.map[i], STOPPED])
        if self.current_scene != None:
            self.midi.send_message([NOTE_ON, self.SCENES[self.current_scene], STOPPED])
            self.current_scene = None

    @holoimpl
    def tapPulse(self):
        self.tap = not self.tap
        self.midi.send_message([CONTROL_CHANGE, self.SESSION_BUTTON, TAP if self.tap else PULSE])
        if not self.tap and not self.pulse:
            self.pulse = True
            self.midi.send_message([CONTROL_CHANGE, 99, PULSE])
    
    @holoimpl
    def toggleMute(self, channel: int):
        self.midi.send_message([NOTE_ON, self.MUTES[channel], RECORDING if self.mutes[channel] else EMPTY])
        self.mutes[channel] = not self.mutes[channel]

    
    @holoimpl
    def toggleFX(self, fx: int):
        self.midi.send_message([NOTE_ON, self.FX[fx], EMPTY if self.fx[fx] else self.FX[fx]])
        self.fx[fx] = not self.fx[fx]
    
    @holoimpl
    def setDrumPatch(self, patch: int):
        self.midi.send_message([CONTROL_CHANGE, self.DRUM_PATCHES[patch], self.DRUM_PATCH_COLORS[patch]])
        for button in set(self.DRUM_PATCHES) - {self.DRUM_PATCHES[patch]}:
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
                if message[2]:
                    # note on event
                    if not self.shift:
                        # normal (unshifted) mode
                        if loop == None:
                            # no existing loop, we are now recording.
                            self.hook.recordLoop(loop=l, volume=message[2])
                        elif self.cut:
                            # cut mode
                            self.hook.playLoop(loop=l, volume=message[2])
                        elif self.overdub:
                            # overdub loop
                            if loop != -2:
                                self.hook.overdubLoop(loop=l)
                            else:
                                self.hook.playLoop(loop=l, volume=message[2])
                            # regular mode - no cut, no overdub
                        elif loop > 0:
                            # loop was playing
                            self.hook.stopLoop(loop=l)
                        else:
                            # loop must be stopped, recording or overdubbing
                            self.hook.playLoop(loop=l, volume=message[2])
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
            elif message[1] in self.DRUMS:
                self.hook.playNote(note=[NOTE_ON | 0x9, 36 + self.DRUMS.index(message[1]) + self.drum_bank*16, message[2]])
                self.lightButton([NOTE_ON, message[1], message[2] if message[2] else self.DRUM_BANKS[self.drum_bank]])
            elif message[1] in self.FX and message[2]:
                f = self.FX.index(message[1])
                self.hook.toggleFX(fx=f)
            elif message[1] in self.DRUM_PATCHES and message[2]:
                i = self.DRUM_PATCHES.index(message[1])
                self.hook.setDrumPatch(patch=i)
            elif message[1] in self.MUTES and message[2]:
                n = self.MUTES.index(message[1])
                self.hook.toggleMute(channel=n)
            else:
                # no matching rule found for note
                pass
        if message[0] in (CONTROL_CHANGE, NOTE_ON):
            # for MK2 compatibility, where scenes are sent as NOTE_ON
            if message[1] in self.SCENES:
                s = self.SCENES.index(message[1])
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
                    if self.scenes[s] == None:
                        self.hook.clearScene(scene=s)
        if message[0] == CONTROL_CHANGE:
            if message[1] in self.FUNCTIONS:
                if message[1] == self.CAPTURE_MIDI_BUTTON:
                    # capture midi button
                    # enable shift mode
                    self.toggleShift()
                if self.shift:
                    if message[1] == self.SESSION_BUTTON:
                        # erase session
                        # delete pulse
                        if message[2] == 127:
                            self.hook.deletePulse()
                        else:
                            self.hook.clearPulse()
                else:
                    # normal (unshifted) mode
                    if message[1] == self.UP_ARROW and message[2] == 127:
                        # arrow up button
                        # drum bank increment
                        # not attached to hook
                        # multiple devices can have seperate local banks
                        self.setDrumBank(bank=min(self.drum_bank + 1, 3))
                    elif message[1] == self.DOWN_ARROW and message[2] == 127:
                        # arrow down button
                        # drum bank decrement
                        self.setDrumBank(bank=max(self.drum_bank - 1, -1))
                    elif message[1] == self.LEFT_ARROW and message[2] == 127:
                        # left arrow button
                        self.hook.stopAllLoops()
                    elif message[1] == self.NOTE_BUTTON:
                        # note button
                        # momentary cut mode - normal on release
                        # note: because all logic is explicit (playLoop, stopLoop, etc)
                        # all state changes can be purely local!
                        self.toggleCut()
                    elif message[1] == self.CUSTOM_BUTTON and message[2] == 127:
                        # custom button
                        # toggle overdub on button press
                        self.toggleOverdub()
                    elif message[1] == self.SESSION_BUTTON:
                        # session button
                        # tap-pulse
                        if message[2] == 127:
                            self.hook.tapPulse()
                        elif self.pulse == False:
                            # this also clears the ERASE color from the Session button if shift mode is released first
                            self.hook.clearPulse()
