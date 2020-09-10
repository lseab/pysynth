import sounddevice as sd
import numpy as np
from scipy.io.wavfile import write
from pysynth.sample import AudioSample
import pysynth.params as p
from pysynth.waveforms import SineWave


class AudioApi:
    """
    Api to interface with PortAudio using the sounddevice library.
    """
    def __init__(self, framerate: int = p.framerate, blocksize: int = p.blocksize, channels: int = 1):
        self.framerate = framerate
        self.channels = channels        
        self.channel_mapping = np.arange(self.channels)
        self.blocksize = blocksize
        self.data = None
        self.stream = self.initialize_stream()
        self.stream.start()
        self.volume = 100.0
        self.playing = False
        self.sample = AudioSample("pysynth.wav")
        self.recording = False

    def initialize_stream(self):
        """
        Initialize sounddevice OutputStream.
        """        
        stream = sd.OutputStream(
            samplerate=self.framerate,
            channels=self.channels,
            blocksize=self.blocksize,
            callback=self.callback,
            dtype='float32')

        return stream

    def prepare_data_blocks(self, data):
        """
        Puts data blocks into correct numpy format.
        The input data is in the form of a List[float].
        """
        data = np.asarray(data)
        if data.ndim < 2: data = data.reshape(-1, 1)
        return data

    def callback(self, outdata, frames, time, status):
        """
        PortAudio callback function for callback in OutputStream.
        """
        if not self.data or not self.playing:
            outdata[:self.blocksize, self.channel_mapping] = np.zeros((self.blocksize, self.channels))
        else:
            try: 
                data = next(self.data)
                if self.recording:
                    self.sample.join(AudioSample.from_array(data))
                data = self.prepare_data_blocks(data)
                outdata[:self.blocksize, self.channel_mapping] =  (self.volume / 100.0) * data
            except StopIteration:
                raise sd.CallbackStop

    def play(self, output):
        """
        Takes an audio data generator as input
        e.g an Oscillator object.
        """
        self.data = output.data()
        self.playing = True

    def stop(self):
        """
        Stop audio playback.
        """
        self.playing = False

    def save_to_wav(self):
        self.sample.save_to_wav()
        self.sample = AudioSample("pysynth.wav")
        self.recording = False