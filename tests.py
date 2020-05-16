import params
import time
from audio_api import AudioApi
from waveforms import *
from filters import *

### AM Modulation

def AM_mod_test():
    audio_interface = AudioApi(framerate=params.framerate, blocksize=params.blocksize, channels=1)
    source = SineWave(880)
    modulator = SineWave(5.0)
    modulated_sound = AmModulationFilter(source=source, modulator=modulator, sensitivity=0)
    audio_interface.play(modulated_sound)

if __name__ == '__main__':
    AM_mod_test()
    time.sleep(5.0)