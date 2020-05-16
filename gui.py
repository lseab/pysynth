import tkinter as tk
from tkinter import messagebox, ttk
import params
from audio_api import AudioApi
from waveforms import SineWave
from midi import MidiController


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
        self.waveform = ttk.OptionMenu(self, self.input_waveformtype, '<select waveform>', *self.waveforms.keys(), command=self.create_osc)
        self.waveform.grid(row=0, column=0, pady=10)

        # Set frequency
        self.freq_frame = tk.Frame(self)
        self.freq_label = tk.Label(self.freq_frame, text="Freq (Hz)")
        self.freq_label.grid(row=0, column=0)
        self.frequency = tk.IntVar(value=440)
        self.input_freq = tk.Entry(self.freq_frame, width=10, textvariable=self.frequency)
        self.input_freq.grid(row=0, column=1, pady=10)

        # Play button
        self.play_btn = ttk.Button(self, text="Play", command=self.set_frequency)
        self.play_btn.grid(row=2, column=0, pady=10)

    def create_osc(self, *args):
        """
        Instantiate oscillator after waveform type selection.
        """
        osc = self.waveforms[self.input_waveformtype.get()]
        self.osc = osc()
        self.freq_frame.grid(row=1)
        self.play()

    def set_frequency(self):
        """
        Set frequency to input value and start oscillator playback.
        """
        if self.osc: 
            self.osc.frequency = int(self.input_freq.get())

    def play(self):
        """
        Call play on audio interface.
        """
        self.audio_api.play(self.osc)


class SynthGUI(tk.Frame):

    def __init__(self, master=None):
        super().__init__(master)
        self.audio_api = AudioApi(framerate=params.framerate, blocksize=params.blocksize, channels=1)
        self.init_protocols()
        self.generate_oscillators()
        self.generate_input()
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
            self.controller.close_controller()
            MidiController.exit()
            self.master.destroy()

    def generate_oscillators(self):
        """
        Create oscillator frames.
        """
        self.oscillators = []
        self.oscframe = tk.Frame(self)
        for _ in range(1):
            osc_nr = len(self.oscillators)
            osc_gui = OscillatorGUI(self.oscframe, title=f'Oscillator {str(osc_nr)}', audio_api=self.audio_api)
            osc_gui.pack(side=tk.LEFT, anchor=tk.N, padx=10, pady=10)
            self.oscillators.append(osc_gui)
        self.oscframe.pack(side=tk.TOP, padx=10, pady=10)

    def generate_input(self):
        """
        Generate UI.
        """
        ## Input Frame
        self.controller = MidiController(self)
        self.inputFrame = tk.Frame(self)
        self.inputFrame.pack(side=tk.TOP, padx=10, pady=10)
        self.input_device = tk.StringVar()
        self.input = ttk.OptionMenu(self.inputFrame, self.input_device, 'None', *self.controller.get_input_devices().keys())
        # callback only triggered on config change
        self.input.bind("<Configure>", self.select_input_device)
        self.input.grid(row=0, column=0, pady=10)

    def select_input_device(self, *args):
        """
        Called upon change in the input_device menu.
        Get new input_device ID and sets the new input on the Midi controller interface.
        """
        selection = self.input_device.get()
        device_id = self.controller.get_input_devices()[selection]
        self.controller.set_input_device(device_id)