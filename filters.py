from waveforms import Oscillator

class AmModulationFilter:

    def __init__(self, source: Oscillator, modulator: Oscillator, sensitivity: float):
        self.source = source.blocks()
        self.modulator = modulator.blocks()
        self.sensitivity = sensitivity

    def blocks(self):

        while True:
            am_envelope = [(1.0 + self.sensitivity * i) for i in next(self.modulator)]
            yield [e * s for (e, s) in zip(next(self.source), am_envelope)]
