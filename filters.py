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
        self.source = source
        self.modulator = modulator
        self.amplitude = amplitude

    def __str__(self):
        return f'FreqMod({self.source}, {self.modulator})'

    def blocks(self, modulate=False):
        while True:
            # modulation = [s + m for (s, m) in zip(next(self.source.blocks(modulate=True)), next(self.modulator.blocks()))]
            if modulate:
                yield [s + m for (s, m) in zip(next(self.source.blocks(modulate=True)), next(self.modulator.blocks()))]                
            else:
                yield np.cos([s + m for (s, m) in zip(next(self.source.blocks(modulate=True)), next(self.modulator.blocks()))])


class SumFilter:
    """
    Takes multiple oscillators as input generates a single output from them.
    """
    def __init__(self, sources: List[Oscillator]):
        self.sources = sources

    def __str__(self):
        return f'Sum{tuple(str(s) for s in self.sources)}'

    def blocks(self):
        sources = [src.blocks() for src in self.sources]
        source_blocks = zip(*sources)
        while True:            
            blocks = next(source_blocks)
            yield [sum(v) for v in zip(*blocks)]