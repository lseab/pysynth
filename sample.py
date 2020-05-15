from typing import List
from waveforms import Oscillator
import params

class AudioSample:

    def __init__(self, name: str, framerate: int, channels: int):
        self.name = name
        self.__framerate = framerate
        self.__frames = []
        self.__channels = channels

    def __len__(self):
        """
        Returns the total number of frames in the sample.
        """
        return len(self.__frames)

    @property
    def framerate(self):
        return self.__framerate

    @property
    def channels(self):
        return self.__channels

    @property
    def frames(self):
        return self.__frames

    def join(self, other: 'AudioSample'):
        assert(self.framerate == other.framerate)
        self.__frames += other.__frames

    @classmethod
    def from_array(cls, array: List[float], framerate: int, name: str = ""):
        """
        Generate an audio sample from an array of audio data.
        """
        sample = cls(name=name, framerate=framerate, channels=1)
        sample.__frames += array
        return sample

    @classmethod
    def from_oscillator(cls, osc: Oscillator, duration: float):
        """
        Generate an audio sample of a given duration from an oscillator object.
        """
        sample = cls(name=osc.__class__.__name__, framerate=osc.framerate, channels=1)

        block_gen = osc.blocks()
        total_frames = int(duration * osc.framerate)
        num_blocks, last_block = divmod(total_frames, params.blocksize)
        
        if last_block > 0: num_blocks +=1
        
        if num_blocks > 0:
            for block in block_gen:
                num_blocks -= 1
                if num_blocks == 0: block = block[:last_block]
                sample.join(AudioSample.from_array(block, osc.framerate))
                if num_blocks == 0: break

        return sample
