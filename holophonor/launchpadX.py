from holophonor import holoimpl
from holophonor.holospecs import Holophonor
from holophonor.constants import *
from rtmidi.midiutil import open_midiinput
from rtmidi.midiconstants import NOTE_ON, CONTROL_CHANGE, NOTE_OFF
from rtmidi import API_UNIX_JACK
from loguru import logger as log


class LaunchpadX(Holophonor):
    SCENES = [89, 79, 69, 59, 49, 39, 29, 19]
    FUNCTIONS = [91, 92, 93, 94, 95, 96, 97, 98]
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
        log.info('Initializing LaunchpadX')
        self.map = []
        n = 81
        for y in range(4):
            for x in range(8):
                self.map.append(n + x)
            n -= 10
        self.live = False
        self.toggleLive()
        self.input, self.input_name = open_midiinput(
            self.port, client_name='launchpadX->holo', api=API_UNIX_JACK
        )
        self.input.set_callback(self)
        self.drum_bank = 0
        self.drum_patch = 0
        self.fx = [False] * 8
        self.clear()
        self.lightDrums()
        log.info('LaunchpadX ready!')

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
            self.midi.send_message(
                [NOTE_ON, self.MUTES[i], EMPTY if self.mutes[i] else RECORDING]
            )
        for i in range(len(self.FX)):
            self.midi.send_message(
                [NOTE_ON, self.FX[i], EMPTY if self.fx[i] else self.fx[i]]
            )
        for i in range(len(self.FUNCTIONS)):
            self.midi.send_message([CONTROL_CHANGE, self.FUNCTIONS[i], EMPTY])
        for i in range(len(self.DRUM_PATCHES)):
            self.midi.send_message([NOTE_ON, self.DRUM_PATCHES[i], EMPTY])
        self.midi.send_message(
            [
                NOTE_ON,
                self.DRUM_PATCHES[self.drum_patch],
                self.DRUM_PATCH_COLORS[self.drum_patch],
            ]
        )

        self.current_scene = None
        self.midi.send_message([CONTROL_CHANGE, 99, 1])
        self.midi.send_message(
            [CONTROL_CHANGE, self.UP_ARROW, self.DRUM_BANKS[min(self.drum_bank + 1, 3)]]
        )
        self.midi.send_message(
            [
                CONTROL_CHANGE,
                self.DOWN_ARROW,
                self.DRUM_BANKS[max(self.drum_bank - 1, -1)],
            ]
        )
        self.midi.send_message([CONTROL_CHANGE, self.LEFT_ARROW, STOPPED])
        self.midi.send_message([CONTROL_CHANGE, self.SESSION_BUTTON, INACTIVE])

    def lightDrums(self):
        for i in self.DRUMS:
            self.midi.send_message([NOTE_ON, i, self.DRUM_BANKS[self.drum_bank]])
        self.midi.send_message(
            [CONTROL_CHANGE, self.UP_ARROW, self.DRUM_BANKS[min(self.drum_bank + 1, 3)]]
        )
        self.midi.send_message(
            [
                CONTROL_CHANGE,
                self.DOWN_ARROW,
                self.DRUM_BANKS[max(self.drum_bank - 1, -1)],
            ]
        )

    def lightButton(self, note):
        self.midi.send_message(note)

    @holoimpl
    def close(self):
        log.info('Closing launchpadX: exiting live mode')

        # exit programming mode
        self.midi.send_message([240, 0, 32, 41, 2, 12, 14, 0, 247])

    @holoimpl
    def recordLoop(self, loop):
        log.info(f'recording loop {loop}')
        self.midi.send_message([NOTE_ON | 0x2, self.map[loop], RECORDING])
        self.loops[loop] = -1

    @holoimpl
    def playLoop(self, loop, volume):
        log.info(f'playing loop {loop} at {volume}')

        self.midi.send_message(
            [NOTE_ON | 0x2, self.map[loop], GREEN[(volume if volume > 0 else 100) >> 4]]
        )
        self.loops[loop] = volume
        if not self.pulse:
            self.pulse = True
            self.midi.send_message([CONTROL_CHANGE, self.SESSION_BUTTON, PULSE])
            self.midi.send_message([CONTROL_CHANGE, 99, PULSE])

    @holoimpl
    def stopLoop(self, loop):
        log.info(f'stopping loop {loop}')
        self.midi.send_message([NOTE_ON, self.map[loop], STOPPED])
        self.loops[loop] = 0

    @holoimpl
    def eraseLoop(self, loop):
        log.info(f'erasing loop {loop}')
        self.midi.send_message([NOTE_ON, self.map[loop], ERASE])
        self.loops[loop] = None

    @holoimpl
    def clearLoop(self, loop):
        log.info(f'clearing loop {loop}')
        self.midi.send_message([NOTE_ON, self.map[loop], EMPTY])

    @holoimpl
    def overdubLoop(self, loop: int):
        log.info(f'overdubbing loop {loop}')
        if self.loops[loop] != -2:
            self.midi.send_message([NOTE_ON, self.map[loop], RECORDING])
            self.loops[loop] = -2

    @holoimpl
    def recallScene(self, scene: int):
        log.info(f'recalling scene {scene}')
        if self.current_scene is not None:
            self.midi.send_message([NOTE_ON, self.SCENES[self.current_scene], STOPPED])
            if self.scenes[self.current_scene] == -1:
                self.scenes[self.current_scene] = self.loops.copy()
        self.current_scene = scene
        self.midi.send_message([NOTE_ON | 0x2, self.SCENES[scene], GREEN[-1]])
        s = self.scenes[scene]
        for l in range(len(self.map)):
            if self.loops[l] is not None:
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
        log.info(f'storing scene {scene}')
        if self.current_scene is not None:
            # if we are playing a scene currently, stop the light
            self.midi.send_message([NOTE_ON, self.SCENES[self.current_scene], STOPPED])
            if self.scenes[self.current_scene] == -1:
                # stop recording, store previous scene
                self.scenes[self.current_scene] = self.loops.copy()
                # also send green light
                self.midi.send_message([NOTE_ON | 0x2, self.SCENES[scene], GREEN[-1]])
        self.current_scene = scene
        if self.scenes[scene] is None:
            self.scenes[scene] = -1
            self.midi.send_message([NOTE_ON | 0x2, self.SCENES[scene], RECORDING])

    @holoimpl
    def eraseScene(self, scene: int):
        log.info(f'erasing scene {scene}')
        self.midi.send_message([NOTE_ON, self.SCENES[scene], ERASE])
        self.scenes[scene] = None
        if self.current_scene == scene:
            self.current_scene = None

    @holoimpl
    def clearScene(self, scene: int):
        log.info(f'clearing scene {scene}')
        self.midi.send_message([NOTE_ON, self.SCENES[scene], EMPTY])

    @holoimpl
    def toggleShift(self):
        self.shift = not self.shift
        log.info(f'Toggling shift mode: {self.shift}')
        self.midi.send_message(
            [CONTROL_CHANGE, self.CAPTURE_MIDI_BUTTON, ERASE if self.shift else 0]
        )

    @holoimpl
    def toggleCut(self):
        self.cut = not self.cut
        log.info(f'Toggling cut mode: {self.cut}')
        self.midi.send_message(
            [CONTROL_CHANGE, self.NOTE_BUTTON, CUT if self.cut else 0]
        )

    @holoimpl
    def toggleOverdub(self):
        self.overdub = not self.overdub
        log.info(f'Toggling overdub mode: {self.overdub}')
        self.midi.send_message(
            [CONTROL_CHANGE, self.CUSTOM_BUTTON, RECORDING if self.overdub else 0]
        )

    @holoimpl
    def deletePulse(self):
        log.info('Deleting pulse')
        self.midi.send_message([CONTROL_CHANGE, self.SESSION_BUTTON, ERASE])
        self.clear()
        self.pulse = False
        self.loops = [None] * len(self.map)
        self.scenes = [None] * len(self.scenes)
        self.midi.send_message([CONTROL_CHANGE, 99, 1])

    @holoimpl
    def clearPulse(self):
        log.info('Clearing pulse')
        self.midi.send_message([CONTROL_CHANGE, self.SESSION_BUTTON, INACTIVE])

    @holoimpl
    def stopAllLoops(self):
        log.info('Stopping all loops')
        for i, l in enumerate(self.loops):
            if l:
                self.midi.send_message([NOTE_ON, self.map[i], STOPPED])
                self.loops[i] = 0

        if self.current_scene is not None:
            self.midi.send_message([NOTE_ON, self.SCENES[self.current_scene], STOPPED])
            self.current_scene = None

    @holoimpl
    def tapPulse(self):
        log.info('tap pulse pressed')
        self.tap = not self.tap
        self.midi.send_message(
            [CONTROL_CHANGE, self.SESSION_BUTTON, TAP if self.tap else PULSE]
        )
        if not self.tap and not self.pulse:
            self.pulse = True
            self.midi.send_message([CONTROL_CHANGE, 99, PULSE])

    @holoimpl
    def toggleMute(self, channel: int):
        log.info(f'{"un" if self.mutes[channel] else ""}muting channel {channel}')
        self.midi.send_message(
            [NOTE_ON, self.MUTES[channel], RECORDING if self.mutes[channel] else EMPTY]
        )
        self.mutes[channel] = not self.mutes[channel]

    @holoimpl
    def toggleFX(self, fx: int):
        log.info(f'{"de" if self.fx[fx] else ""}activating fx {fx}')
        self.midi.send_message(
            [NOTE_ON, self.FX[fx], EMPTY if self.fx[fx] else self.FX[fx]]
        )
        self.fx[fx] = not self.fx[fx]

    @holoimpl
    def setDrumPatch(self, patch: int):
        log.info(f'setting drum patch {patch}')
        self.midi.send_message(
            [NOTE_ON, self.DRUM_PATCHES[patch], self.DRUM_PATCH_COLORS[patch]]
        )
        for button in set(self.DRUM_PATCHES) - {self.DRUM_PATCHES[patch]}:
            self.midi.send_message([NOTE_ON, button, EMPTY])
        self.drum_patch = patch

    @holoimpl
    def setDrumBank(self, bank: int):
        log.info(f'Setting drum bank {bank}')
        self.drum_bank = bank
        self.lightDrums()

    def __call__(self, event, data=None):
        message, deltatime = event
        log.debug(message)
        if message[0] == NOTE_ON:
            log.trace('NOTE ON detected')
            if message[1] in self.map:
                log.trace('This is a loop button')
                l = self.map.index(message[1])
                loop = self.loops[l]
                if message[2]:
                    log.trace('note on event')
                    if not self.shift:
                        log.trace('normal (unshifted) mode')
                        if loop is None:
                            log.trace('no existing loop, we are now recording.')
                            self.hook.recordLoop(loop=l, volume=message[2])
                        elif self.cut:
                            log.trace(f'cut mode. Play loop {l} at volume {message[2]}')
                            self.hook.playLoop(loop=l, volume=message[2])
                        elif self.overdub:
                            log.trace(f'overdub loop {l}')
                            if loop != -2:
                                self.hook.overdubLoop(loop=l)
                            else:
                                self.hook.playLoop(loop=l, volume=message[2])
                            log.trace('regular mode - no cut, no overdub')
                        elif loop > 0:
                            log.trace('loop was playing')
                            self.hook.stopLoop(loop=l)
                        else:
                            log.trace('loop must be stopped, recording or overdubbing')
                            self.hook.playLoop(loop=l, volume=message[2])
                    else:
                        log.trace('shift mode. Erase loop')
                        self.hook.eraseLoop(loop=l)
                else:
                    log.trace('note off. Button released')
                    if self.loops[l] is None:
                        log.trace('if we erased the loop, clear the color')
                        self.hook.clearLoop(loop=l)
            elif message[1] in self.DRUMS:
                log.trace('this is a drum button. Playing note')
                self.hook.playNote(
                    note=[
                        NOTE_ON | 0x9,
                        36 + self.DRUMS.index(message[1]) + self.drum_bank * 16,
                        message[2],
                    ]
                )
                self.lightButton(
                    [
                        NOTE_ON,
                        message[1],
                        message[2] if message[2] else self.DRUM_BANKS[self.drum_bank],
                    ]
                )
            elif message[1] in self.FX and message[2]:
                log.trace('this is an FX button. Toggling FX')
                f = self.FX.index(message[1])
                self.hook.toggleFX(fx=f)
            elif message[1] in self.DRUM_PATCHES and message[2]:
                log.trace('this is a drum patch button. Setting drum patch')
                i = self.DRUM_PATCHES.index(message[1])
                self.hook.setDrumPatch(patch=i)
            elif message[1] in self.MUTES and message[2]:
                log.trace('this is a mute button. Toggling mute')
                n = self.MUTES.index(message[1])
                self.hook.toggleMute(channel=n)
            else:
                log.trace(f'no matching rule found for note {message[1]}')
        if message[0] in (CONTROL_CHANGE, NOTE_ON):
            # for MK2 compatibility, where scenes are sent as NOTE_ON
            if message[1] in self.SCENES:
                log.trace('this is a scene button')
                s = self.SCENES.index(message[1])
                if message[2] == 127:
                    log.trace('scene button pressed')
                    if self.shift:
                        log.trace('shift mode. erase scene')
                        self.hook.eraseScene(scene=s)
                    else:
                        log.trace('normal (unshifted) mode. store/recall scene')
                        if self.scenes[s] in (None, -1):
                            log.trace('store scene')
                            self.hook.storeScene(scene=s)
                        else:
                            log.trace('recall scene')
                            self.hook.recallScene(scene=s)
                else:
                    log.trace('scene button released')
                    if self.scenes[s] is None:
                        log.trace('if we erased the scene, clear the color')
                        self.hook.clearScene(scene=s)
        if message[0] == CONTROL_CHANGE:
            if message[1] in self.FUNCTIONS:
                if message[1] == self.CAPTURE_MIDI_BUTTON:
                    log.trace(
                        f'capture midi button {"released" if self.shift else "pressed"}. {"de" if self.shift else ""}activating shift mode'
                    )
                    self.toggleShift()
                if self.shift:
                    if message[1] == self.SESSION_BUTTON:
                        if message[2] == 127:
                            log.trace('erase all loops and pulse')
                            self.hook.deletePulse()
                        else:
                            log.trace('clearning pulse color')
                            self.hook.clearPulse()
                else:
                    # normal (unshifted) mode
                    if message[1] == self.UP_ARROW and message[2] == 127:
                        log.trace('arrow up button. drum bank increment')
                        # not attached to hook
                        # multiple devices can have seperate local banks
                        self.setDrumBank(bank=min(self.drum_bank + 1, 3))
                    elif message[1] == self.DOWN_ARROW and message[2] == 127:
                        log.trace('arrow down button. drum bank decrement')
                        self.setDrumBank(bank=max(self.drum_bank - 1, -1))
                    elif message[1] == self.LEFT_ARROW and message[2] == 127:
                        log.trace('left arrow button. Stop all loops')
                        self.hook.stopAllLoops()
                    elif message[1] == self.NOTE_BUTTON:
                        log.trace('note button. toggle cut mode while pressed')
                        # note: because all logic is explicit (playLoop, stopLoop, etc)
                        # all state changes can be purely local!
                        self.toggleCut()
                    elif message[1] == self.CUSTOM_BUTTON and message[2] == 127:
                        log.trace('custom button. toggle overdub mode')
                        self.toggleOverdub()
                    elif message[1] == self.SESSION_BUTTON:
                        if message[2] == 127:
                            log.trace('session button pressed. tap pulse')
                            self.hook.tapPulse()
                        elif self.pulse is False:
                            log.trace('session button released. clear pulse')
                            # this clears the ERASE color from the Session button if shift mode is released first
                            self.hook.clearPulse()
        if message[0] == NOTE_OFF:
            log.trace('NOTE OFF detected')
            if message[1] in self.map:
                log.trace('This is a loop button')
                l = self.map.index(message[1])
                loop = self.loops[l]
                if loop is None:
                    log.trace('Clearing erased loop')
                    self.clearLoop(loop=l)
            elif message[1] in self.DRUMS:
                log.trace('clearing drum note')
                self.lightButton(
                    [
                        NOTE_ON,
                        message[1],
                        self.DRUM_BANKS[self.drum_bank],
                    ]
                )
