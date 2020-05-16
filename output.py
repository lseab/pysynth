import params
from audio_api import AudioApi
from filters import AmModulationFilter


class Output:

    def __init__(self):
        self.audio_api = AudioApi(framerate=params.framerate, blocksize=params.blocksize, channels=1)
        self.oscillator = None
        self.am_modulator = None

    def add_oscillator(self, oscillator):
        self.oscillator = oscillator

    def set_osc_frequency(self, frequency):
        self.oscillator.frequency = frequency

    def tremolo(self):
        self.modulated = AmModulationFilter(source=self.oscillator, modulator=self.am_modulator)

    def apply_filters(self):
        self.tremolo()

    def play(self):
        self.apply_filters()   
        self.audio_api.play(self.modulated)

    def stop(self):
        self.audio_api.stop()