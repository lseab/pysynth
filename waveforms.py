from abc import ABC, abstractmethod
from typing import Generator, Optional, List
import numpy as np
import sounddevice as sd
import params


class Oscillator(ABC):
    """
    Abstract class for all oscillator objects.
    Requires a List[float] generator for instantiation.
    """
    def __init__(self, framerate: int = 0, name: str = ""):
        self.framerate = framerate
        self.name = name
    
    @abstractmethod
    def blocks(self) -> Generator[List[float], None, None]:
        pass


class SineWave(Oscillator):
    """
    Pure sine wave oscillator.
    Modulate flag in blocks() allows for FM modulation.
    """
    def __init__(self, frequency: int = 0, amplitude: int = 1.0, framerate: int = params.framerate, name: str = ""):
        super().__init__(framerate, name)
        self.frequency = frequency
        self.amplitude = amplitude

    def __str__(self):
        return f'{self.name}'

    def blocks(self, modulate=False) -> Generator[List[float], None, None]:
        increment = 2.0 * np.pi / self.framerate
        t = 0.0
        while True:
            block = []
            for _ in range(params.blocksize):
                if modulate: 
                    block.append(t * self.frequency)
                else: block.append(self.amplitude * np.sin(t * self.frequency))
                t += increment
            yield block

class SquareWave(Oscillator):
    """
    Pure square wave oscillator.
    """
    def __init__(self, frequency: int = 0, amplitude: int = 1.0, framerate: int = params.framerate):
        super().__init__(framerate)
        self.frequency = frequency
        self.amplitude = amplitude

    def blocks(self) -> Generator[List[float], None, None]:
        increment = 1.0 / self.framerate
        t = 0.0
        while True:
            block = []
            for _ in range(params.blocksize):
                block.append(self.amplitude if int(2*t*self.frequency) % 2 == 0 else -self.amplitude)
                t += increment
            yield block