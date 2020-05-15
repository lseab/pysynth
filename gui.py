import tkinter as tk
from tkinter import messagebox
import params
from audio_api import AudioApi
from waveforms import SineWave
from midi import MidiController
from threading import Thread


class OscillatorGUI(tk.LabelFrame):
    """
    GUI unit for an oscillator panel.
    """
    def __init__(self, master, audio_api, title):
        super().__init__(master)
        self._title = title
        self.master.title = 'Oscillator'
        self.osc = None
        self.audio_api = audio_api
        self.UI()

    def UI(self):
        """
        Generate UI.
        """
        # Waveform choice
        self.waveforms = {
            "sine": SineWave, 
            "triangle": None,
            "sawtooth": None, 
            "square": None, 
            "noise": None
            }
        self.input_waveformtype = tk.StringVar()
        self.waveform = tk.OptionMenu(self, self.input_waveformtype, *self.waveforms.keys(), command=self.create_osc)
        self.waveform.grid(row=0, column=0, pady=10)

        # Set frequency
        self.freq_frame = tk.Frame(self)
        self.freq_label = tk.Label(self.freq_frame, text="Freq (Hz)")
        self.freq_label.grid(row=0, column=0)
        self.frequency = tk.IntVar(value=440)
        self.input_freq = tk.Entry(self.freq_frame, width=10, textvariable=self.frequency)
        self.input_freq.grid(row=0, column=1, pady=10)

        # Play button
        self.play_btn = tk.Button(self, text="Play", command=self.play_osc)
        self.play_btn.grid(row=2, column=0, pady=10)

    def create_osc(self, *args):
        """
        Instantiate oscillator after waveform type selection.
        """
        osc = self.waveforms[self.input_waveformtype.get()]
        self.osc = osc()
        self.freq_frame.grid(row=1)

    def play_osc(self):
        """
        Start oscillator playback.
        """
        if self.osc: self.osc.frequency = int(self.input_freq.get())
        self.audio_api.play(self.osc)


class SynthGUI(tk.Frame):

    def __init__(self, master=None):
        super().__init__(master)
        self._is_running = True
        self.audio_api = AudioApi(framerate=params.framerate, blocksize=params.blocksize, channels=1)
        self.use_midi = True
        self.controller = MidiController()
        self.init_protocols()
        self.UI()
        self.pack()

    def init_protocols(self):
        """
        Call self.on_closing when the gui window is closed.
        """
        self.master.protocol("WM_DELETE_WINDOW", self.on_closing)

    def on_closing(self):
        """
        Closing message box
        """
        if messagebox.askokcancel("Quit", "Are you sure you want to quit?"):
            self._is_running = False
            self.midi_thread.join()
            self.controller.close()
            self.master.destroy()

    def UI(self):
        """
        Generate UI.
        """
        self.oscillators = []
        self.osc_frame = tk.Frame(self)
        for _ in range(3):
            self.generate_osc_gui()
        self.osc_frame.pack(side=tk.TOP, padx=10, pady=10)
        if self.use_midi: 
            self.midi_thread = Thread(target=self.get_midi_info)
            self.midi_thread.start()

    def generate_osc_gui(self):
        """
        Add oscillator panels.
        """
        osc_nr = len(self.oscillators)
        osc_gui = OscillatorGUI(self.osc_frame, title=f'Oscillator {str(osc_nr)}', audio_api=self.audio_api)
        osc_gui.pack(side=tk.LEFT, anchor=tk.N, padx=10, pady=10)
        self.oscillators.append(osc_gui)

    def get_midi_info(self):
        """
        Extract midi info from controller.
        Update oscillators if use_midi flag set to True.
        """
        while self._is_running:
            self.controller.read_input()
            for osc in self.oscillators:
                try:
                    osc.osc.frequency = int(self.controller.frequency)
                except AttributeError:
                    pass