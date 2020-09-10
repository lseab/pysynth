import os
import numpy as np
import pysynth.params as p
from typing import List
from pysynth.waveforms import Oscillator
from scipy.io.wavfile import write
from datetime import datetime


class AudioSample:

    def __init__(self, name: str, framerate: int = p.framerate, channels: int = 1):
        self.name = name
        self._framerate = framerate
        self._frames = []
        self._channels = channels

    def __len__(self):
        """
        Returns the total number of frames in the sample.
        """
        return len(self._frames)

    @property
    def framerate(self):
        return self._framerate

    @property
    def channels(self):
        return self._channels

    @property
    def frames(self):
        return self._frames

    def join(self, other):
        assert(self.framerate == other.framerate)
        self._frames += other._frames

    @classmethod
    def from_array(cls, array: List[float], framerate: int = p.framerate, name: str = ""):
        """
        Generate an audio sample from an array of audio data.
        """
        sample = cls(name=name, framerate=framerate, channels=1)
        sample._frames += array
        return sample

    @classmethod
    def from_oscillator(cls, osc: Oscillator, duration: float):
        """
        Generate an audio sample of a given duration from an oscillator object.
        """
        sample = cls(name=osc.__class__.__name__, framerate=osc.framerate, channels=1)

        block_gen = osc.data()
        total_frames = int(duration * osc.framerate)
        num_blocks, last_block = divmod(total_frames, p.blocksize)
        
        if last_block > 0: num_blocks +=1
        
        if num_blocks > 0:
            for block in block_gen:
                num_blocks -= 1
                if num_blocks == 0: block = block[:last_block]
                sample.join(AudioSample.from_array(block, osc.framerate))
                if num_blocks == 0: break

        return sample

    def save_to_wav(self):
        if not os.path.exists('recordings'):
            os.makedirs('recordings')
        file_no = 0
        filename = ''.join(['pysynth_', datetime.now().strftime("%m_%d_%Y_"), str(file_no), '.wav'])
        filepath = os.path.join('recordings', filename)
        while os.path.exists(filepath):
            file_no += 1
            filename = ''.join(['pysynth_', datetime.now().strftime("%m_%d_%Y_"), str(file_no), '.wav'])
            filepath = os.path.join('recordings', filename)
        write(filepath, self.framerate, np.asarray(self._frames))