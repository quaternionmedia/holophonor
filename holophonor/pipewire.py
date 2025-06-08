from holophonor import holoimpl
from holophonor.holospecs import Holophonor
from holophonor.exceptions import *
from pipewire_python.controller import Controller
import asyncio
from datetime import datetime
from loguru import logger as log
from psutil import process_iter
from os import path
from multiprocessing import Process
from subprocess import run


class Pipewire(Holophonor):
    '''Pipewire implementation of the Holophonor interface'''

    def __init__(self, *args, **kwargs):
        self.RECORDING_DIR = kwargs.get('RECORDING_DIR', 'recordings')

        self.pw = Controller()
        self.pw.set_config(
            rate=48000, channels=2, _format='s32', volume=1.0, latency='64', quality=4
        )
        self.event_loop = asyncio.get_event_loop()
        self.loops = [None] * 32
        self.playing = {}
        self.recording = {}

    def _find_process(self, process, filename: str):
        '''Find a process by filename'''
        for proc in process_iter(['pid', 'cmdline']):
            if proc.name() == process:
                if filename in proc.cmdline():
                    log.debug(f'Found PipeWire process: {proc}')
                    return proc
        raise ProcessNotFoundException(
            f'No PipeWire process found for loop {loop} recording'
        )

    def _play(self, loop: int, volume: int, repeat: int = -1):
        '''Play a file using PipeWire'''
        filename = self.loops[loop]
        run(['./uphonor', filename, f'{volume / 127.0}'])

    @holoimpl
    def playLoop(self, loop: int, volume: int):
        '''play loop at volume'''
        filename = self.loops[loop]
        if filename is None:
            raise LoopNotFoundException(f'Loop {loop} is not recorded')
        if self.recording.get(loop):
            log.debug(
                f'Loop {loop} is currently being recorded, stopping recording first'
            )
            self.recording[loop].terminate()
            proc = self._find_process('pw-cat', filename)
            log.debug(f'Stopping recording process: {proc}')
            proc.kill()
            del self.recording[loop]
        log.info(f'Playing loop {loop} at volume {volume}')
        task = Process(target=self._play, args=(loop, volume, -1), daemon=True)
        task.start()
        self.playing[loop] = task

    @holoimpl
    def stopLoop(self, loop: int):
        '''pause loop'''
        filename = self.loops[loop]
        if filename is None:
            raise LoopNotFoundException(f'Loop {loop} is not playing')
        log.info(f'Stopping loop {loop}')
        self.playing[loop].terminate()
        log.debug(f'Stopped loop {loop}')
        del self.playing[loop]
        proc = self._find_process('uphonor', filename)
        log.debug(f'Stopping playing loop process {proc=}')
        proc.kill()

    @holoimpl
    def recordLoop(self, loop: int):
        '''record loop'''
        filename = path.join(self.RECORDING_DIR, f'{datetime.now().isoformat()}.wav')
        self.loops[loop] = filename
        task = Process(target=self.pw.record, args=(filename, -1, True), daemon=True)
        task.start()
        self.recording[loop] = task

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
