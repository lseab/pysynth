import pygame.midi as midi

class MidiController:

    def __init__(self):
        midi.init()
        self.device_id = midi.get_default_input_id()
        self.controller = midi.Input(self.device_id)
        self._frequency = 0

    @property
    def frequency(self):
        return self._frequency

    def read_input(self):
        """
        Poll midi device for input.
        Convert midi note to frequency.
        """
        if self.controller.poll():
            event = self.controller.read(1)[0]
            data = event[0]
            timestamp = event[1]
            note_number = data[1]
            velocity = data[2]
            self._frequency = midi.midi_to_frequency(note_number)

    def close(self):
        self.controller.close()