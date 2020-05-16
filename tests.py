import params
import time
from midi import MidiController
from audio_api import AudioApi
from waveforms import *
from filters import *

### AM Modulation

def AM_mod_test(duration: float):
    audio_interface = AudioApi(framerate=params.framerate, blocksize=params.blocksize, channels=1)
    source = SineWave(880)
    modulator = SineWave(5.0)
    modulated_sound = AmModulationFilter(source=source, modulator=modulator, sensitivity=0)
    audio_interface.play(modulated_sound)
    time.sleep(duration)

def midi_controller():
    cont = MidiController()
    print(cont.input_devices)


if __name__ == '__main__':
    midi_controller() 