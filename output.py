import params
from copy import copy
from audio_api import AudioApi
from filters import AmpModulationFilter, FreqModulationFilter, SumFilter
from routing import Routing


class Output:

    def __init__(self):
        self.audio_api = AudioApi(framerate=params.framerate, blocksize=params.blocksize, channels=1)
        self.am_modulator = None
        self.oscillators = []
        self.output = None

    def get_oscillators(self):
        return self.oscillators

    def get_next_oscillators(self, osc):
        index = self.oscillators.index(osc)
        return self.oscillators[index + 1:]

    def add_oscillator(self, oscillator):
        self.oscillators.append(oscillator)

    def tremolo(self, source):
        if self.am_modulator:
            return AmpModulationFilter(source=source, modulator=self.am_modulator)
        else:
            return source
            
    def apply_filters(self):
        routing = Routing(self.oscillators)
        carriers = [c for c in routing.get_final_output()]
        print([str(c) for c in carriers])
        summed_signal = routing.sum_signals(carriers)
        modulated_output = self.tremolo(summed_signal)
        return modulated_output

    def set_output_frequency(self, frequency):
        for o in self.oscillators:
            if o.to_oscillator: pass
            else: 
                o.osc.frequency = frequency
                o.frequency.set(frequency)

    def play(self):
        if self.oscillators:
            self.output = self.apply_filters()
            self.audio_api.play(self.output)

    def stop(self):
        self.audio_api.stop()