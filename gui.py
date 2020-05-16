import tkinter as tk
from tkinter import messagebox, ttk
import params
from output import Output
from waveforms import SineWave
from midi import MidiController
from filters import AmModulationFilter


class OscillatorGUI(ttk.LabelFrame):
    """
    GUI unit for an oscillator panel.
    """
    def __init__(self, master_frame, output, title):
        super().__init__(master_frame, text=title)
        #self.osc = None
        self.output = output
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
        self.play_btn = ttk.Button(self, text="Play", command=self.play)
        self.play_btn.grid(row=2, column=0, padx=5, pady=10)

        # Stop button
        self.stop_btn = ttk.Button(self, text="Stop", command=self.stop)
        self.stop_btn.grid(row=2, column=1, padx=5, pady=10)

    def create_osc(self, *args):
        """
        Instantiate oscillator after waveform type selection.
        """
        osc = self.waveforms[self.input_waveformtype.get()]
        self.output.add_oscillator(osc())
        self.freq_frame.grid(row=1)
        #self.play()

    def set_frequency(self):
        """
        Set frequency to input value.
        """
        if self.output.oscillator: 
            self.output.set_osc_frequency(int(self.input_freq.get()))

    def play(self):
        """
        Call play on audio interface.
        """
        self.set_frequency()
        self.output.play()

    def stop(self):
        """
        Call stop on audio interface.
        """
        self.output.stop()


class TremoloGUI(ttk.LabelFrame):

    def __init__(self, master, output, title):
        super().__init__(master, text=title)
        self.output = output
        self.UI()

    def UI(self):
        # Waveform choice
        self.waveforms = {
            "sine": SineWave, 
            "triangle": None,
            "sawtooth": None, 
            "square": None, 
            "noise": None
            }
        self.input_waveformtype = tk.StringVar()
        self.waveform = ttk.OptionMenu(self, self.input_waveformtype, '<modulator waveform>', *self.waveforms.keys(), command=self.set_modulator)
        self.waveform.pack(padx=10, pady=10)

        # Control frame
        self.control_frame = tk.Frame(self)
        self.control_frame.pack(padx=10, pady=5)
        # Frequency slider
        self.freq_label = tk.Label(self.control_frame, text='frequency')
        self.freq_label.grid(row=0, column=0)
        self.frequency = tk.Scale(self.control_frame, from_=0, to=10, orient=tk.HORIZONTAL, resolution=.1, command=self.set_frequency)
        self.frequency.set(5)
        self.frequency.grid(row=0, column=1)
        # Sensitivity slider
        self.sens_label = tk.Label(self.control_frame, text='sensitivity')
        self.sens_label.grid(row=1, column=0)
        self.sensitivity = tk.Scale(self.control_frame, from_=0, to=1, orient=tk.HORIZONTAL, resolution=.02, command=self.set_sensitivity)
        self.sensitivity.set(0.5)
        self.sensitivity.grid(row=1, column=1)

    def set_modulator(self, *args):
        freq = self.frequency.get()
        waveform = self.waveforms[self.input_waveformtype.get()]
        self.output.am_modulator = waveform()
        self.set_frequency()

    def set_frequency(self, *args):
        if self.output.am_modulator:
            freq = self.frequency.get()
            self.output.am_modulator.frequency = freq

    def set_sensitivity(self, *args):
        if self.output.am_modulator:
            sens = self.sensitivity.get()
            self.output.am_modulator.amplitude = sens


class SynthGUI(ttk.Frame):

    def __init__(self, master=None):
        super().__init__(master)
        self.output = Output()
        self.init_protocols()
        self.generate_oscillators()
        self.generate_filters()
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
            osc_gui = OscillatorGUI(master_frame=self.oscframe, output=self.output, title=f'Oscillator {str(osc_nr + 1)}')
            osc_gui.pack(side=tk.LEFT, anchor=tk.N, padx=10, pady=10)
            self.oscillators.append(osc_gui)
        self.oscframe.pack(side=tk.TOP, padx=10, pady=10)

    def generate_input(self):
        """
        Generate midi input gui.
        """
        ## Input Frame
        self.controller = MidiController(self.output)
        self.inputFrame = tk.Frame(self)
        self.inputFrame.pack(side=tk.TOP, padx=10, pady=10)
        self.input_device = tk.StringVar()
        self.input = ttk.OptionMenu(self.inputFrame, self.input_device, 'None', *self.controller.get_input_devices().keys())
        # callback only triggered on config change
        self.input.bind("<Configure>", self.select_input_device)
        self.input.grid(row=0, column=0, pady=10)

    def generate_filters(self):
        # Tremolo
        self.tremolo_frame = tk.Frame(self)
        self.tremolo_frame.pack(side=tk.TOP, padx=10, pady=10)
        self.trem_gui = TremoloGUI(self.tremolo_frame, output=self.output, title=f'Tremolo (AM modulation)')
        self.trem_gui.pack()

    def select_input_device(self, *args):
        """
        Called upon change in the input_device menu.
        Get new input_device ID and sets the new input on the Midi controller interface.
        """
        selection = self.input_device.get()
        device_id = self.controller.get_input_devices()[selection]
        self.controller.set_input_device(device_id)