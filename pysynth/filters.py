import numpy as np
from abc import ABC
from pysynth.waveforms import Oscillator, EmptyOscillator
from typing import List
from pysynth.params import blocksize, framerate, fade_in_time
from scipy.signal import butter, lfilter, freqz, lfilter_zi


class Filter(Oscillator, ABC):
    """
    Base class for all filter objects.
    All filters have a state flag, which is updated as the ADSR state of the sources changes. This state flag
    is passed along every stage of the data pipeline, thus allowing to control for idle voices in VoicesSumFilter,
    and remove them.
    """
    def __init__(self, sources: List[Oscillator]):
        super().__init__(sources[0].framerate if sources else 0)
        self.sources = sources
        self.state = 1


class AmpModulationFilter(Filter):
    """
    Amplitude modulater. Takes a source oscillator and a modulating oscillator as inputs and generates a modulated signal.
    """
    def __init__(self, source: Oscillator, modulator: Oscillator):
        super().__init__([source])
        self.source = source
        self.modulator = modulator

    def __str__(self):
        return f'AmpMod({self.source}, {self.modulator})'

    def data(self):
        source = self.source.data()
        modulator = self.modulator.data(single_samples=False)
        while True:
            am_envelope = [(1.0 + i) for i in next(modulator)]
            yield [e * s for (e, s) in zip(am_envelope, next(source))]
            self.state = self.source.state


class FreqModulationFilter(Filter):
    """
    Frequncy modulater. Takes a source oscillator and a modulating oscillator as inputs and generates a modulated signal.
    """
    def __init__(self, source: Oscillator, modulator: Oscillator):
        super().__init__([source])
        self.source = source
        self.source_data = source.data(modulate=True)
        self.modulator = modulator
        self.mod_data = modulator.data()

    def __str__(self):
        return f'FreqMod({self.source}, {self.modulator})'

    def data(self, modulate=False):
        while True:
            modulation = [s + m for (s, m) in zip(next(self.source_data), next(self.mod_data))]
            if modulate:
                yield modulation
            else:
                yield [a * b for (a, b) in zip(self.source.amps, np.cos(modulation))]
                self.state = self.source.state


class SumFilter(Filter):
    """
    Takes multiple oscillators as input and generates a single output from them.
    """
    def __init__(self, sources: List[Oscillator], amplitude: float = 1.0, normalise: bool = True):
        super().__init__(list(sources))
        self.amplitude = amplitude
        if normalise: self.normalise_amplitude()

    def __str__(self):
        return f'Sum{tuple(str(s) for s in self.sources)}'

    def normalise_amplitude(self):
        self.amplitude /= len(self.sources)

    def data(self):
        sources = [src.data() for src in self.sources]
        source_data = zip(*sources)
        amplitude = self.amplitude
        while True:
            data = next(source_data)
            yield [amplitude * sum(v) for v in zip(*data)]
            self.state = sum([source.state for source in self.sources])


class VoicesSumFilter(Filter):
    """
    Takes the filtered output of multiple voices as input and generates a single output from them.
    """
    def __init__(self, sources: List[Oscillator] = [], amplitude: float = 1.0, normalise: bool = True):
        super().__init__(list(sources))
        self.amplitude = amplitude
        self.sources = [PopFilter(source) for source in self.sources]
        if normalise: self.normalise_amplitude()

    def __str__(self):
        return f'Sum{tuple(str(s) for s in self.sources)}'

    def add_source(self, source, max):
        self.sources.append(source)
        self.generators.append(source.data())
        self.source_data = zip(*self.generators)

    def remove_source(self, source):
        index = self.sources.index(source)
        self.sources.remove(source)
        del self.generators[index]

    def prepare_source_data(self):        
        self.generators = [src.data() for src in self.sources]
        self.source_data = zip(*self.generators)

    def normalise_amplitude(self):
        self.amplitude /= len(self.sources)

    def data(self):
        self.prepare_source_data()
        while True:
            try:
                data = next(self.source_data)
                yield [self.amplitude * sum(v) for v in zip(*data)]
                for source in self.sources:
                    if source.state == 0:
                        self.remove_source(source)
            except StopIteration:
                yield [0.0 for _ in range(blocksize)]


class PassFilter(Filter):
    """
    Uses a butterworth filter function (from the scipy library) to change the audio
    bandwidth. Can be a lowpass or a highpass filter.
    """
    def __init__(self, source: Oscillator, cutoff: float, filter_type: str):
        super().__init__([source])
        self.source = source
        self.cutoff = cutoff
        self.filter_type = filter_type

    @staticmethod
    def butterworth(cutoff, filter_type, order=3):
        return butter(order, cutoff, fs=framerate, btype=filter_type, analog=False)

    @staticmethod
    def frequency_response(cutoff, filter_type, order=3):
        b, a = PassFilter.butterworth(cutoff, filter_type, order)
        return freqz(b, a, fs=framerate, worN=500)

    def butterworth_filter(self, data, cutoff, filter_type, zi, order=3):
        b, a = PassFilter.butterworth(cutoff, filter_type, order)
        y, zf = lfilter(b, a, data, axis=0, zi=zi)
        return y, zf

    def data(self):
        source = self.source.data()
        zi = lfilter_zi(*PassFilter.butterworth(self.cutoff, self.filter_type))
        while True:
            filtered_data, zi = self.butterworth_filter(next(source), self.cutoff, self.filter_type, zi)
            yield filtered_data
            self.state = self.source.state

    @classmethod
    def lowpass(cls, *args):
        return cls(*args, filter_type="low")

    @classmethod
    def highpass(cls, *args):
        return cls(*args, filter_type="high")


class Envelope(Filter):
    """
    ADSR envelope generator. Takes a source oscillator as input, and yields oscillator data
    multiplied by a variable amplitude envelope. There are four states in the envelope generator:
        - ATTACK: triggered when a key is pressed, the output rises from 0 to maximum output 
        according to a user-defined rate
        - DECAY: triggered once maximum output is reached, the output then drops until it reaches a 
        user-defined susain level
        - SUSTAIN: output remains constant until a release event is triggered (a key is no longer pressed)
        - RELEASE: output drops from the sustain level to 0 at a user-defined rate

    The envelope generators are defined exponentially (in part to mimic the shape of capacitor charge/discharge).
    The exponential calculations can be done in an iterative manner which makes them efficient. Indeed,
    it is trivial to show that a function of the form y(x) = A * (1 - exp(rate * x)) can be generated iteratively in the 
    following way:

    y(x + 1) = y(x) * exp(rate) + A * (1 - exp(rate))

    The rate is a constant, therefore exp(rate) can be calculated once and used as a multiplier in each subsequent iteration.

    In order to calculate the envelope, we define a 'target' value above the trigger (maximum amplitude in the case 
    of attack for example), which the exponential function 'reaches' asymptotically at x -> +∞. Hence in our y(x) function,
    in the case of attack, our A constant would be (max_amplitude + target). Solving for rate such that max_amplitude is
    reached in a given time (attack_time), it can be shown that:

    rate = (1.0 / attack_time) * log(target / (max_amplitude + target))
    """ 
    def __init__(self, source: Oscillator):
        super().__init__([source])
        self.source = source
        self.amps = [0.0 for _ in range(blocksize)]
        self.max_amp = source.amplitude
        self.attack = source.envelope['attack']
        self.decay = source.envelope['decay']
        self.sustain_level = source.envelope['sustain'] * self.max_amp
        self.release = source.envelope['release']
        self.a_target = source.envelope['a_target']
        self.dr_target = source.envelope['dr_target']

    def __str__(self):
        return str(self.source)

    def get_rate(self, target, time, base):
        """
        Calculate the evolution rates for attack, decay and release states.
        """
        return (1.0 / (time * self.framerate)) * np.log(target / base)

    def data(self, modulate=False):
        amplitude = 0.0
        max_amp = self.max_amp
        sustain_level = self.sustain_level
        source_data = self.source.data(modulate=modulate)

        # Calculate multipliers here for optimization
        if self.attack != 0.0:
            attack_multiplier = np.exp(self.get_rate(target=self.a_target, time=self.attack, base=(max_amp + self.a_target)))
            attack_base = (max_amp + self.a_target) * (1 - attack_multiplier)
        if self.decay != 0.0:
            decay_multiplier = np.exp(self.get_rate(target=self.dr_target, time=self.decay, base=(max_amp - sustain_level + self.dr_target)))
            decay_base = (sustain_level - self.dr_target) * (1 - decay_multiplier)
        if self.release != 0.0:
            release_multiplier = np.exp(self.get_rate(target=self.dr_target, time=self.release, base=(sustain_level + self.dr_target)))
            release_base = - self.dr_target * (1 - release_multiplier)

        while True:
            # ATTACK STATE
            if self.state == 1:
                if self.attack == 0.0:
                    amplitude = max_amp
                    self.state = 2
                else:
                    block = []
                    self.amps = []
                    for _ in range(blocksize):
                        block.append(next(source_data))
                        self.amps.append(amplitude)
                        amplitude = attack_base + amplitude * attack_multiplier
                    if modulate: yield block
                    else: yield [a * b for (a, b) in zip(self.amps, block)]
                    if amplitude >= max_amp: self.state = 2

            # DECAY STATE
            if self.state == 2:
                if self.decay == 0.0:
                    amplitude = max_amp
                    self.state = 3
                else:
                    block = []
                    self.amps = []
                    for _ in range(blocksize):
                        block.append(next(source_data))
                        self.amps.append(amplitude)
                        amplitude = decay_base + amplitude * decay_multiplier
                    if modulate: yield block
                    else: yield [a * b for (a, b) in zip(self.amps, block)]
                    if amplitude <= sustain_level: self.state = 3

            # SUSTAIN STATE
            if self.state == 3:
                block = []
                self.amps = []
                amplitude = sustain_level
                for _ in range(blocksize):
                    block.append(next(source_data))
                    self.amps.append(sustain_level)
                if modulate: yield block
                else: yield [a * b for (a, b) in zip(self.amps, block)]

            # RELEASE STATE
            if self.state == 4:
                if self.release == 0.0:
                    self.state = 0
                elif amplitude > 0:
                    block = []
                    self.amps = []
                    for _ in range(blocksize):
                        block.append(next(source_data))
                        self.amps.append(amplitude)
                        amplitude = release_base + amplitude * release_multiplier
                    if modulate: yield block
                    else: yield [a * b for (a, b) in zip(self.amps, block)]
                else:
                    self.state = 0

            # IDLE STATE
            if self.state == 0:
                self.amps = [0.0 for _ in range(blocksize)]
                yield self.amps


class PopFilter(Filter):
    """
    Filter added to every new voice to avoid popping sounds.
    This is the last filter to be added to the output from each new VoiceChannel object.
    """
    def __init__(self, source: Oscillator):
        super().__init__([source])
        self.source = source

    def __str__(self):
        return str(self.source)

    def data(self):
        source_data = self.source.data()
        frame_nr = fade_in_time * framerate
        if frame_nr > 0: increment = 1 / frame_nr
        fade_factor = 0.0

        while frame_nr > 0:
            data = next(source_data)
            for i, frame in enumerate(data):
                data[i] = frame * fade_factor
                if frame_nr > 0: 
                    frame_nr -= 1
                    fade_factor += increment
            yield data
        
        while True:
            yield next(source_data)
            self.state = self.source.state