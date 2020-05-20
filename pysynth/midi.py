import pygame.midi as midi
from pygame.midi import MidiException
from threading import Thread

class MidiController:

    def __init__(self, output):
        midi.init()
        self._midi_active = False
        self.input_devices = self.get_input_devices()
        self.default_device_id = midi.get_default_input_id()
        self.controller = None
        self._frequency = 0
        self.midi_thread = None
        self.output = output

    @property
    def active(self):
        return self._midi_active

    @active.setter
    def active(self, value):
        self._midi_active = value

    @property
    def frequency(self):
        return self._frequency

    def get_input_devices(self):
        """
        Queries midi interface for available devices.
        Checks that they are input devices (third element in return tuple corresponds to input flag, 1 if input else 0).
        Returns a dict of the form {device_name: device_id} device_id = -1 corresponds to no device.
        """
        input_devices = {}

        for i in range(midi.get_count()):
            if midi.get_device_info(i)[2] == 1:
                input_devices[midi.get_device_info(i)[1].decode('utf-8')] = i
        input_devices['None'] = -1

        return input_devices

    def set_input_device(self, device_id: int):
        """
        Changes input device and starts listening thread if midi enabled.
        Can be called from gui.
        """
        self.controller = self._input_device(device_id)
        if self.active:
            self.midi_thread = Thread(target=self.update_oscillators)
            self.midi_thread.start()

    def _input_device(self, device_id: int):
        """
        Create new Input object. 
        Catches MidiException if no controller found or none configured.
        """
        try:
            self._midi_active = True
            return midi.Input(device_id)
        except MidiException:
            self._midi_active = False
            self.close_controller()
            return None

    def read_input(self):
        """
        Poll midi device for input.
        Convert midi note to frequency.
        """
        event = self.controller.read(1)[0]
        data = event[0]
        timestamp = event[1]
        note_number = data[1]
        velocity = data[2]
        self._frequency = midi.midi_to_frequency(note_number)

    def update_oscillators(self):
        """
        Extract midi info from controller if active and update oscillators.
        """
        while self.active:
            if self.controller.poll():
                self.read_input()
                try:
                    self.output.set_output_frequency(int(self.frequency))
                except AttributeError:
                    pass

    def close_controller(self):
        """
        Called on closing the application. Closes the midi controller interface and PortMidi.
        """
        if self.midi_thread:
            self.active = False
            self.midi_thread.join()
            self.midi_thread = None
            self.controller.close()
        
    @staticmethod
    def exit():
        midi.quit()