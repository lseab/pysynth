import tkinter as tk
from tkinter import messagebox, ttk
import pysynth.params
from pysynth.output import Output
from pysynth.midi import MidiController
from .oscillator import OscillatorGUI
from .tremolo import TremoloGUI
from .keyboard import KeyboardGUI
from .algos import AlgorithmGUI


class SynthGUI(ttk.Frame):

    def __init__(self, master=None):
        super().__init__(master)
        self.first = True
        self.output = Output()
        self.init_protocols()
        self.generate_oscillators()
        self.algorithm_frame()
        self.filters_frame()
        self.keyboard_frame()
        self.input_frame()
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

        for _ in range(4):
            osc_nr = len(self.oscillators)
            osc_gui = OscillatorGUI(master_frame=self.oscframe, output=self.output, number=osc_nr)
            osc_gui.pack(side=tk.LEFT, anchor=tk.N, padx=30, pady=10)
            self.oscillators.append(osc_gui)

        self.oscframe.pack(side=tk.TOP, padx=10, pady=10)

    def algorithm_frame(self):
        self.algo_frame = AlgorithmGUI(self)
        self.algo_frame.pack(side=tk.TOP, padx=10, pady=10)

    def filters_frame(self):
        # Tremolo
        self.tremolo_frame = tk.Frame(self)
        self.tremolo_frame.pack(side=tk.TOP, padx=10, pady=10)
        self.trem_gui = TremoloGUI(self.tremolo_frame, output=self.output, title=f'Tremolo (AM modulation)')
        self.trem_gui.pack()

    def keyboard_frame(self):
        self.key_frame = tk.Frame(self)        
        self.key_frame.pack(side=tk.TOP, padx=10, pady=10)
        self.keyboard = KeyboardGUI(self.key_frame, self.output)
        self.keyboard.pack()

    def input_frame(self):
        """
        Generate midi input gui.
        """
        ## Input Frame
        self.controller = MidiController(self.output)
        self.inputFrame = tk.Frame(self)
        self.inputFrame.pack(side=tk.TOP, padx=10, pady=10)
        self.inputLabel = tk.Label(self.inputFrame, text="Input device : ")
        self.inputLabel.grid(row=0, column=0, pady=10)
        self.input_device = tk.StringVar()
        self.input = ttk.OptionMenu(self.inputFrame, self.input_device, 'None', *self.controller.get_input_devices().keys())
        # callback only triggered on config change
        self.input.bind("<Configure>", self.select_input_device)
        self.input.grid(row=0, column=1, pady=10)

    def select_input_device(self, *args):
        """
        Called upon change in the input_device menu.
        Get new input_device ID and sets the new input on the Midi controller interface.
        """
        selection = self.input_device.get()
        device_id = self.controller.get_input_devices()[selection]
        self.controller.set_input_device(device_id)