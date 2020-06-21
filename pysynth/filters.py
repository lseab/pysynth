import numpy as np
from abc import ABC
from pysynth.waveforms import Oscillator
from typing import List
from pysynth.params import blocksize
from scipy.signal import butter, lfilter, freqz, lfilter_zi


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
        self.source = source
        self.modulator = modulator

    def blocks(self):
        source = self.source.blocks()
        modulator = self.modulator.blocks(single_samples=False)
        while True:
            am_envelope = [(1.0 + i) for i in next(modulator)]
            yield [e * s for (e, s) in zip(am_envelope, next(source))]


class FreqModulationFilter(Filter):
    """
    Frequncy modulater. Takes a source oscillator and a modulating oscillator as inputs and generates a modulated signal.
    """
    def __init__(self, source: Oscillator, modulator: Oscillator):
        super().__init__([source])
        self.source = source
        self.source_blocks = source.blocks(modulate=True)
        self.modulator = modulator
        self.mod_blocks = modulator.blocks()

    def __str__(self):
        return f'FreqMod({self.source}, {self.modulator})'

    def blocks(self, modulate=False):
        while True:
            modulation = [s + m for (s, m) in zip(next(self.source_blocks), next(self.mod_blocks))]
            if modulate:
                yield modulation
            else:
                yield [a * b for (a, b) in zip(self.source.amps, np.cos(modulation))]


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
        amplitude = self.amplitude
        while True:
            blocks = next(source_blocks)
            yield [amplitude * sum(v) for v in zip(*blocks)]


class FreqFilter(Filter):
    def __init__(self, source: Oscillator, cutoff: float, filter_type: str):
        super().__init__([source])
        self.source = source
        self.cutoff = cutoff
        self.filter_type = filter_type

    def butterworth(self, order, cutoff, filter_type):
        b, a = butter(order, cutoff, fs=self.framerate, btype=filter_type, analog=False)
        return b, a

    def butterworth_filter(self, data, cutoff, filter_type, zi, order=3):
        b, a = self.butterworth(order, cutoff, filter_type)
        y, zf = lfilter(b, a, data, axis=0, zi=zi)
        return y, zf

    def blocks(self):
        source = self.source.blocks()
        zi = lfilter_zi(*self.butterworth(3, self.cutoff, self.filter_type))
        while True:
            filtered_data, zi = self.butterworth_filter(next(source), self.cutoff, self.filter_type, zi)
            yield filtered_data

    @classmethod
    def lowpass(cls, *args):
        return cls(*args, filter_type="low")

    @classmethod
    def highpass(cls, *args):
        return cls(*args, filter_type="high")


class Envelope(Filter):
    def __init__(self, source: Oscillator):
        super().__init__([source])
        self.source = source
        self.amps = [0.0 for _ in range(blocksize)]
        self.state = 1
        self.max_amp = source.amplitude
        self.attack = source.envelope['attack']
        self.decay = source.envelope['decay']
        self.sustain_level = source.envelope['sustain'] * self.max_amp
        self.release = source.envelope['release']
        self.a_target = source.envelope['a_target']
        self.dr_target = source.envelope['dr_target']

    def __str__(self):
        return str(self.source)

    def get_coefficient(self, target, rate, base):
        return (1.0 / (rate * self.framerate)) * np.log(target / base)

    def blocks(self, modulate=False):
        amplitude = 0.0
        max_amp = self.max_amp
        sustain_level = self.sustain_level
        source_blocks = self.source.blocks(modulate=modulate)

        if self.attack != 0.0:
            attack_multiplier = np.exp(self.get_coefficient(target=self.a_target, rate=self.attack, base=(max_amp + self.a_target)))
            attack_base = (max_amp + self.a_target) * (1 - attack_multiplier)
        if self.decay != 0.0:
            decay_multiplier = np.exp(self.get_coefficient(target=self.dr_target, rate=self.decay, base=(max_amp - sustain_level + self.dr_target)))
            decay_base = (sustain_level - self.dr_target) * (1 - decay_multiplier)
        if self.release != 0.0:
            release_multiplier = np.exp(self.get_coefficient(target=self.dr_target, rate=self.release, base=(sustain_level + self.dr_target)))
            release_base = - self.dr_target * (1 - release_multiplier)

        while True:
            if self.state == 1:
                if self.attack == 0.0:
                    amplitude = max_amp
                    self.state = 2
                else:
                    block = []
                    self.amps = []
                    for _ in range(blocksize):
                        block.append(next(source_blocks))
                        self.amps.append(amplitude)
                        amplitude = attack_base + amplitude * attack_multiplier
                    if modulate: yield block
                    else: yield [a * b for (a, b) in zip(self.amps, block)]
                    if amplitude >= max_amp: self.state = 2

            if self.state == 2:
                if self.decay == 0.0:
                    amplitude = max_amp
                    self.state = 3
                else:
                    block = []
                    self.amps = []
                    for _ in range(blocksize):
                        block.append(next(source_blocks))
                        self.amps.append(amplitude)
                        amplitude = decay_base + amplitude * decay_multiplier
                    if modulate: yield block
                    else: yield [a * b for (a, b) in zip(self.amps, block)]
                    if amplitude <= sustain_level: self.state = 3

            if self.state == 3:
                block = []
                self.amps = []
                amplitude = sustain_level
                for _ in range(blocksize):
                    block.append(next(source_blocks))
                    self.amps.append(sustain_level)
                if modulate: yield block
                else: yield [a * b for (a, b) in zip(self.amps, block)]

            if self.state == 4:
                if self.release == 0.0:
                    amplitude = 0.0
                    yield [0.0 for _ in range(blocksize)]
                elif amplitude > 0:
                    block = []
                    self.amps = []
                    for _ in range(blocksize):
                        block.append(next(source_blocks))
                        self.amps.append(amplitude)
                        amplitude = release_base + amplitude * release_multiplier
                    if modulate: yield block
                    else: yield [a * b for (a, b) in zip(self.amps, block)]
                else:
                    yield [0.0 for _ in range(blocksize)]