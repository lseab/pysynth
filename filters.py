import numpy as np
from waveforms import Oscillator
from typing import List

class AmpModulationFilter:
    """
    Amplitude modulater. Takes a source oscillator and a modulating oscillator as inputs and generates a modulated signal.
    """
    def __init__(self, source: Oscillator, modulator: Oscillator):
        self.source = source.blocks()
        self.modulator = modulator.blocks()

    def blocks(self):
        while True:
            am_envelope = [(1.0 + i) for i in next(self.modulator)]
            yield [e * s for (e, s) in zip(am_envelope, next(self.source))]

class FreqModulationFilter:
    """
    Frequncy modulater. Takes a source oscillator and a modulating oscillator as inputs and generates a modulated signal.
    """
    def __init__(self, source: Oscillator, modulator: Oscillator, amplitude: float = 1.0):
        self.source = source.blocks(modulate=True)
        self.modulator = modulator.blocks()
        self.amplitude = amplitude

    def blocks(self):
        while True:
            yield np.cos([s + m for (s, m) in zip(next(self.source), next(self.modulator))])


class SumFilter:
    """
    Takes multiple oscillators as input generates a single output from them.
    """
    def __init__(self, sources: List[Oscillator]):
        self.sources = sources

    def blocks(self):
        sources = [src.blocks() for src in self.sources]
        source_blocks = zip(*sources)
        while True:            
            blocks = next(source_blocks)
            yield [sum(v) for v in zip(*blocks)]