from abc import ABC, abstractmethod
from typing import Generator, Optional, List
import numpy as np
import sounddevice as sd
from pysynth.params import blocksize, framerate


class Oscillator(ABC):
    """
    Abstract class for all oscillator objects.
    Requires a List[float] generator for instantiation.
    """
    def __init__(self, frequency, amplitude, framerate, name, disabled):
        if disabled: frequency = amplitude = 0.0
        self.disabled = disabled
        self.frequency = frequency
        self.amplitude = amplitude
        self.framerate = framerate
        self.name = name
        self.to_oscillators = []        
        self.fixed_frequency = False
        self.frequency_ratio = 1.0

    def __str__(self):
        return f'{self.name}'

    def disable(self):
        self.amplitude = 0.0
    
    @abstractmethod
    def blocks(self) -> Generator[List[float], None, None]:
        pass


class SineWave(Oscillator):
    """
    Pure sine wave oscillator.
    Modulate flag in blocks() allows for FM modulation.
    """
    def __init__(self, frequency: float = 0.0, amplitude: float = 1.0, framerate: int = framerate, name: str = "", disabled: bool = False):
        super().__init__(frequency, amplitude, framerate, name, disabled)

    def blocks(self, modulate=False) -> Generator[List[float], None, None]:
        increment = 2.0 * np.pi / self.framerate
        t = 0.0
        while True:
            block = []
            for _ in range(blocksize):                
                if modulate:
                    block.append(t * self.frequency)
                else: block.append(self.amplitude * np.sin(t * self.frequency))
                t += increment
            yield block


class SquareWave(Oscillator):
    """
    Pure square wave oscillator.
    """
    def __init__(self, frequency: float = 0.0, amplitude: float = 1.0, framerate: int = framerate, name: str = "", disabled: bool = False):
        super().__init__(frequency, amplitude, framerate, name, disabled)

    def blocks(self, modulate=False) -> Generator[List[float], None, None]:
        increment = 1.0 / self.framerate
        t = 0.0
        while True:
            block = []
            for _ in range(blocksize):
                block.append(self.amplitude if int(2*t*self.frequency) % 2 == 0 else -self.amplitude)
                t += increment
            yield block