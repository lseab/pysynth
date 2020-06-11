import numpy as np
from abc import ABC
from pysynth.waveforms import Oscillator
from typing import List


class Filter(ABC):
    """
    Abstract class for all filter objects.
    """
    def __init__(self, sources: List[Oscillator]):
        self.sources = sources        
        self.framerate = sources[0].framerate if sources else 0


class AmpModulationFilter(Filter):
    """
    Amplitude modulater. Takes a source oscillator and a modulating oscillator as inputs and generates a modulated signal.
    """
    def __init__(self, source: Oscillator, modulator: Oscillator):
        super().__init__([source])
        self.source = source.blocks()
        self.modulator = modulator.blocks()

    def blocks(self):
        while True:
            am_envelope = [(1.0 + i) for i in next(self.modulator)]
            yield [e * s for (e, s) in zip(am_envelope, next(self.source))]


class FreqModulationFilter(Filter):
    """
    Frequncy modulater. Takes a source oscillator and a modulating oscillator as inputs and generates a modulated signal.
    """
    def __init__(self, source: Oscillator, modulator: Oscillator, amplitude: float = 1.0):
        super().__init__([source])
        self.source = source
        self.source_blocks = source.blocks(modulate=True)
        self.modulator = modulator
        self.mod_blocks = modulator.blocks()
        self.amplitude = self.source.amplitude

    def __str__(self):
        return f'FreqMod({self.source}, {self.modulator})'

    def blocks(self, modulate=False):
        while True:
            modulation = [s + m for (s, m) in zip(next(self.source_blocks), next(self.mod_blocks))]
            if modulate:
                yield modulation               
            else:
                yield self.amplitude * np.cos(modulation)

class SumFilter(Filter):
    """
    Takes multiple oscillators as input generates a single output from them.
    """
    def __init__(self, sources: List[Oscillator], amplitude: float = 1.0, normalise: bool = True):
        super().__init__(list(sources))
        self.amplitude = amplitude
        if normalise: self.normalise_amplitude()

    def __str__(self):
        return f'Sum{tuple(str(s) for s in self.sources)}'

    def normalise_amplitude(self):
        self.amplitude /= len(self.sources)        

    def blocks(self):
        sources = [src.blocks() for src in self.sources]
        source_blocks = zip(*sources)
        while True:            
            blocks = next(source_blocks)
            yield [self.amplitude * sum(v) for v in zip(*blocks)]


class Envelope(Filter):
    def __init__(self, source: Oscillator, attack: float):
        super().__init__([source])
        self.source = source.blocks()
        self.attack = attack

    def blocks(self):
        amplitude = 0.0
        while True:
            amplitude += 2048 / (self.attack * self.framerate)
            yield [source * amplitude for source in next(self.source)]