import pygame.midi as midi
from pygame import time
from pygame.midi import MidiException
from threading import Thread
from .output import VoiceChannel


class MidiEvent:

    def __init__(self, midi_output):
        self.data = midi_output[0]
        self.timestamp = midi_output[1]
        self._event_type = self.data[0] #key press or release
        self.note_number = self.data[1]
        self.velocity = self.data[2]
        self.frequency = midi.midi_to_frequency(self.note_number)    

    @property
    def event_type(self):
        if self._event_type == 144:
            return "On"
        elif self._event_type == 128:
            return "Off"   


class MidiController:

    def __init__(self, output):
        midi.init()
        self._midi_active = False
        self.input_devices = self.get_input_devices()
        self.default_device_id = midi.get_default_input_id()
        self.controller = None
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
        Returns a dict of the form {device_name: device_id}, device_id = -1 corresponds to no device.
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

    def update_oscillators(self):
        """
        Extract midi info from controller if active and add a new voice.
        """
        while self.active:
            if self.controller.poll():
                midi_event = MidiEvent(self.controller.read(1)[0])
                if midi_event.event_type == "On":
                    try:
                        voice = VoiceChannel(self.output, frequency=int(midi_event.frequency))
                        self.output.add_new_voice(voice)
                        self.output.play()
                    except AttributeError:
                        pass
                if midi_event.event_type == "Off":
                    self.output.release_notes(int(midi_event.frequency))
            time.wait(20)

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