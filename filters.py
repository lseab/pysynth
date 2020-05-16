from waveforms import Oscillator

class AmModulationFilter:
    """
    Amplitude modulater. Takes a source oscillator and a modulating oscillator as inputs and generates a modulated signal.
    Sensitivity changes the strength of the modulation effect.
    """
    def __init__(self, source: Oscillator, modulator: Oscillator, sensitivity: float):
        self.source = source.blocks()
        self.modulator = modulator.blocks()
        self.sensitivity = sensitivity

    def blocks(self):

        while True:
            am_envelope = [(1.0 + self.sensitivity * i) for i in next(self.modulator)]
            yield [e * s for (e, s) in zip(am_envelope, next(self.source))]