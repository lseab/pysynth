from abc import ABC, abstractmethod
from typing import Generator, Optional, List
import numpy as np
import random
import sounddevice as sd
from pysynth.params import blocksize, framerate


class Oscillator:
    """
    Abstract class for all oscillator objects.
    Requires a List[float] generator for instantiation.
    """
    def __init__(self, frequency, amplitude, framerate, name):
        self.disabled = False
        self.frequency = frequency
        self.amplitude = amplitude
        self.framerate = framerate
        self.name = name
        self.to_oscillators = []        
        self.fixed_frequency = False
        self.frequency_ratio = 1.0
        self.envelope = {
            "attack": 0.0,
            "decay": 0.0,
            "sustain": 1.0,
            "release": 0.05,
            "a_target": 1,
            "dr_target": 10**(-6)
        }

    def __str__(self):
        return f'{self.name}'

    def disable(self):
        self.amplitude = 0.0
        self.disabled = True
    
    @abstractmethod
    def data(self) -> Generator[List[float], None, None]:
        pass


class SineWave(Oscillator):
    """
    Pure sine wave oscillator.
    Modulate flag in blocks() allows for FM modulation.
    """
    def __init__(self, frequency: float = 0.0, amplitude: float = 0.1, framerate: int = framerate, name: str = ""):
        super().__init__(frequency, amplitude, framerate, name)

    def data(self, modulate=False, single_samples=True) -> Generator[List[float], None, None]:
        increment = 2.0 * np.pi / self.framerate
        t = 0.0
        frequency = self.frequency
        while True:
            if single_samples:
                if modulate:
                    yield t * frequency
                else: yield np.sin(t * frequency)
                t += increment
            else:
                block = []
                for _ in range(blocksize):                
                    if modulate:
                        block.append(t * frequency)
                    else: block.append(self.amplitude * np.sin(t * frequency))
                    t += increment
                yield block


class SquareWave(Oscillator):
    """
    Pure square wave oscillator.
    """
    def __init__(self, frequency: float = 0.0, amplitude: float = 0.1, framerate: int = framerate, name: str = ""):
        super().__init__(frequency, amplitude, framerate, name)

    def data(self, modulate=False, single_samples=True) -> Generator[List[float], None, None]:
        increment = 1.0 / self.framerate
        t = 0.0
        while True:
            if single_samples:
                yield self.amplitude if int(2*t*self.frequency) % 2 == 0 else -self.amplitude
                t += increment
            else:
                block = []
                for _ in range(blocksize):
                    block.append(self.amplitude if int(2*t*self.frequency) % 2 == 0 else -self.amplitude)
                    t += increment
                yield block


class WhiteNoise(Oscillator):
    """
    White noise oscillator.
    """
    def __init__(self, frequency: float = 0.0, amplitude: float = 0.1, framerate: int = framerate, name: str = ""):
        super().__init__(frequency, amplitude, framerate, name)

    def data(self, modulate=False) -> Generator[List[float], None, None]:
        increment = 2.0 * np.pi / self.framerate
        t = 0.0
        while True:
            yield self.amplitude * random.uniform(-self.amplitude, self.amplitude)


class EmptyOscillator(Oscillator):
    def __init__(self, frequency: float = 0.0, amplitude: float = 0.1, framerate: int = framerate, name: str = ""):
        super().__init__(frequency, amplitude, framerate, name)

    def data(self, modulate=False) -> Generator[List[float], None, None]:
        while True:
            yield 0.0