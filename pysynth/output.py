from pysynth.params import blocksize, framerate
from copy import deepcopy, copy
from pysynth.audio_api import AudioApi
from pysynth.filters import AmpModulationFilter, FreqModulationFilter, SumFilter, Envelope, PassFilter
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
        self.filter_type = "lowpass"
        self.filter_cutoff = 18000
        self.oscillators = []
        self.max_voices = 6
        self.voices = []

    def add_oscillator(self, oscillator, index):
        self.oscillators.insert(index, oscillator)
        self.route_and_filter()

    def get_next_oscillators(self, osc):
        """
        Get the next oscillators in the sequence.
        The oscillators are ordered from left to right in the GUI.
        """
        index = self.oscillators.index(osc)
        return self.oscillators[index + 1:]

    def add_new_voice(self, voice):
        if len(self.voices) >= self.max_voices:
            self.voices.pop()
        self.voices.append(voice)

    def remove_voice(self, frequency):
        for voice in self.voices:
            if voice.frequency == frequency: self.voices.remove(voice)

    def release_notes(self, frequency):
        for voice in self.voices:
            if voice.frequency == frequency: 
                voice.release_notes()
                self.voices.remove(voice)

    def set_am_modulator(self, waveform):
        self.am_modulator = waveform
        self.route_and_filter()

    def tremolo(self, source):
        """
        Apply a tremolo effect.
        """
        if self.am_modulator:
            return AmpModulationFilter(source=source, modulator=self.am_modulator)
        else:
            return source

    def pass_filter(self, source):
        if self.filter_type == "lowpass": return PassFilter.lowpass(source, self.filter_cutoff)
        elif self.filter_type == "highpass": return PassFilter.highpass(source, self.filter_cutoff)

    def route_and_filter(self):
        for voice in self.voices:
            voice.route_and_filter()

    def apply_final_filters(self, signal):
        """
        Apply filters after routing.
        """
        final_output = self.tremolo(signal)
        final_output = self.pass_filter(final_output)
        return final_output

    def choose_algorithm(self, algo):
        algorithms = Algorithms(self.oscillators)
        algo_function = algorithms.algorithm_switch().get(algo)
        algo_function()
        self.route_and_filter()

    def get_output(self):
        outputs = [voice.filtered_output for voice in self.voices]
        return SumFilter(outputs)

    def play(self):
        """
        Perform modulation, filtering and start playback.
        """
        output = self.get_output()
        final_output = self.apply_final_filters(output)
        self.audio_api.play(final_output)

    def stop(self):
        """
        Stop audio playback
        """
        self.audio_api.stop()


class VoiceChannel:

    def __init__(self, output, frequency):
        oscillators = deepcopy(output.oscillators)
        self.oscillators = [Envelope(o) for o in oscillators]
        self.set_frequency(frequency)
        self.frequency = frequency
        self.route_and_filter()

    def route_and_filter(self):
        """
        Instantiate a Routing object which outputs the carrier waves after FM modulation.
        The resulting waves are then summed, and filters applied.
        """
        routing = Routing(self.oscillators)
        carriers = routing.get_final_output()
        if len(carriers) > 1: 
            self.filtered_output = routing.sum_signals(carriers)
        else: self.filtered_output = carriers[0]

    def set_frequency(self, frequency):
        """
        Set frequency of oscillators from external source (e.g midi controller).
        """
        filtered_oscillators = [o for o in self.oscillators if not o.source.disabled]
        for o in filtered_oscillators:
            if o.source.fixed_frequency: pass
            else:
                ratio = o.source.frequency_ratio
                o.source.frequency = frequency * ratio

    def release_notes(self):
        for o in self.oscillators:
            o.state = 4