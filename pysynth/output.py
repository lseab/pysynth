from pysynth.params import blocksize, framerate
from copy import copy
from pysynth.audio_api import AudioApi
from pysynth.filters import AmpModulationFilter, FreqModulationFilter, SumFilter
from pysynth.routing import Routing


class Algorithms:

    def __init__(self, oscillators):
        assert(len(oscillators) == 4)
        self.oscillators = oscillators

    def stack(self):
        for n, o in enumerate(self.oscillators):
            if n < len(self.oscillators) - 1:
                o.to_oscillators = [self.oscillators[n+1]]

    def parallel(self):
        for o in self.oscillators:
            o.to_oscillators = []

    def square(self):
        for n, o in enumerate(self.oscillators):
            o.to_oscillators = []
            if n % 2 == 0:
                o.to_oscillators = [self.oscillators[n+1]]

    def three_to_one(self):
        for n, o in enumerate(self.oscillators):
            o.to_oscillators = []
            if n < len(self.oscillators) - 1:
                o.to_oscillators = [self.oscillators[-1]]

    def algorithm_switch(self):
        return {
            "stack": self.stack,
            "parallel": self.parallel,
            "square": self.square,
            "3to1": self.three_to_one
        }
            

class Output:

    def __init__(self):
        self.audio_api = AudioApi(framerate=framerate, blocksize=blocksize, channels=1)
        self.am_modulator = None
        self.oscillators = []
        self.filtered_ouput = None

    def set_am_modulator(self, waveform):
        self.am_modulator = waveform
        self.route_and_filter()

    def get_next_oscillators(self, osc):
        """
        Get the next oscillators in the sequence.
        The oscillators are ordered from left to right in the GUI.
        """
        index = self.oscillators.index(osc)
        return self.oscillators[index + 1:]

    def add_oscillator(self, oscillator):
        self.oscillators.append(oscillator)
        self.route_and_filter()

    def tremolo(self, source):
        """
        Apply a tremolo effect.
        """
        if self.am_modulator:
            return AmpModulationFilter(source=source, modulator=self.am_modulator)
        else:
            return source

    def route_and_filter(self):
        """
        Instantiate a Routing object which outputs the carrier waves after FM modulation.
        The resulting waves are then summed, and filters applied.
        """
        routing = Routing(self.oscillators)
        carriers = routing.get_final_output()
        if len(carriers) > 1: 
            output = routing.sum_signals(carriers)
        else: output = carriers[0]
        self.filtered_ouput = self.apply_filters(output)
        if self.audio_api.playing == True:
            self.play()

    def apply_filters(self, signal):
        """
        Apply filters after routing.
        """
        modulated_output = self.tremolo(signal)
        return modulated_output

    def set_output_frequency(self, frequency):
        """
        Set frequency of (non-modulating) oscillators from external source (e.g midi controller).
        """
        filtered_oscillators = [o for o in self.oscillators if not o.osc.disabled]
        for o in filtered_oscillators:
            if o.fixed_frequency(): pass
            else:
                ratio = o.ratio()
                o.osc.frequency = frequency * ratio
                o.frequency_var.set(frequency * ratio)

    def choose_algorithm(self, algo):
        algorithms = Algorithms(self.oscillators)
        algo_function = algorithms.algorithm_switch().get(algo)
        algo_function()
        self.route_and_filter()

    def play(self):
        """
        Perform modulation, filtering and start playback.
        """
        self.audio_api.play(self.filtered_ouput)

    def stop(self):
        """
        Stop audio playback
        """
        self.audio_api.stop()