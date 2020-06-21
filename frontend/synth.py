import tkinter as tk
from PIL import ImageTk, Image
from tkinter import messagebox, ttk
import pysynth.params
from pysynth.output import Output
from pysynth.filters import Envelope
from pysynth.waveforms import SineWave
from pysynth.midi import MidiController
from .oscillator import OscillatorGUI
from .filters import TremoloGUI, PassFilterGUI
from .keyboard import KeyboardGUI
from .algos import AlgorithmGUI
from .envelope import EnvelopeGUI


class SynthGUI(tk.Tk):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.first = True
        self.output = Output()
        self.init_protocols()
        self.main_frames()
        self.generate_oscillators()
        self.display_frame()
        self.envelope_frame()
        self.configuration_frame()
        self.selected_algorithm_frame()
        self.filters_frame()
        self.keyboard_frame()
        self.input_frame()
        self.status_bar()

    def init_protocols(self):
        """
        Call self.on_closing when the gui window is closed.
        """
        self.protocol("WM_DELETE_WINDOW", self.on_closing)

    def on_closing(self):
        """
        Closing message box
        """
        if messagebox.askokcancel("Quit", "Are you sure you want to quit?"):
            self.controller.close_controller()
            MidiController.exit()
            self.destroy()

    def main_frames(self):
        self.top_frame = tk.Frame(self)
        self.top_frame.pack()
        self.middle_frame = tk.Frame(self)
        self.middle_frame.pack()
        self.bottom_frame = tk.Frame(self)
        self.bottom_frame.pack()

    def generate_oscillators(self):
        """
        Create oscillator frames.
        """
        self.oscillators = []
        self.oscframe = tk.Frame(self.top_frame)

        for _ in range(4):
            osc_nr = len(self.oscillators)
            osc_gui = OscillatorGUI(master_frame=self.oscframe, gui=self, output=self.output, number=osc_nr)
            osc_gui.pack(side=tk.LEFT, anchor=tk.N, padx=30, pady=5)
            self.oscillators.append(osc_gui)

        self.oscframe.pack()

    def display_frame(self):
        self.display_frame = tk.Frame(self.middle_frame, relief=tk.RAISED, borderwidth=2, 
                                        highlightbackground="light sky blue", highlightcolor="light sky blue", highlightthickness=20, 
                                        height=450, width=700)
        self.display_frame.grid(row=0, column=1, pady=20)
        self.display_frame.pack_propagate(False)

    def envelope_frame(self):
        self.oscillators[0]['bg'] = 'SkyBlue1'
        self.env_gui = EnvelopeGUI(self.display_frame, self.oscillators[0].osc, padx=20, pady=20)

    def algorithm_frame(self):
        self.algo_frame = AlgorithmGUI(self.display_frame, self)

    def selected_algorithm_frame(self):
        self.selected_algo_frame = tk.Frame(self.oscframe, width=100, height=100)
        self.selected_algo_frame.pack(side=tk.LEFT, anchor=tk.N, padx=30, pady=50)
        self.selected_algo_frame.pack_propagate(False)
        self.selected_algo_frame.bind("<Button-1>", self.show_algorithms)
        self.change_algorithm_image()

    def change_algorithm_image(self):
        selected_algo = self.algo_frame.algo_var.get()
        if selected_algo == "stack": self.algo_image = self.algo_frame.stack_image        
        elif selected_algo == "parallel": self.algo_image = self.algo_frame.para_image        
        elif selected_algo == "square": self.algo_image = self.algo_frame.square_image
        elif selected_algo == "3to1": self.algo_image = self.algo_frame.three_image
        else: self.algo_image = None
        try: 
            self.algo_label.destroy()
        except: pass
        self.algo_label = tk.Label(self.selected_algo_frame, image=self.algo_image)
        self.algo_label.bind("<Button-1>", self.show_algorithms)
        self.algo_label.pack()

    def show_algorithms(self, *args):
        self.env_gui.pack_forget()
        self.pass_filter_gui.plot_frame.pack_forget()
        self.config_frame.pack(expand=True, padx=10, pady=10)

    def show_envelope(self, oscillator, number):
        self.config_frame.pack_forget()
        self.pass_filter_gui.plot_frame.pack_forget()
        self.env_gui.pack()
        self.env_gui.update_envelope(oscillator, number)

    def configuration_frame(self):
        self.config_frame = tk.Frame(self.display_frame)
        self.algo_frame = AlgorithmGUI(self.config_frame, self)
        self.algo_frame.pack(padx=10, pady=20)
        self.voicesframe = tk.Frame(self.config_frame)
        self.voicesframe.pack(padx=10, pady=20)
        self.voicesLabel = tk.Label(self.voicesframe, text="Voices : ")
        self.voicesLabel.grid(row=0, column=0)
        self.input_num_voices = tk.IntVar(value=self.output.max_voices)
        self.num_voices = ttk.OptionMenu(self.voicesframe, self.input_num_voices, *[i for i in range(15)], command=self.set_voices)
        self.num_voices.grid(row=0, column=1)

    def set_voices(self, *args):
        self.output.max_voices = self.input_num_voices.get()

    def filters_frame(self):
        self.filters_frame_left = tk.Frame(self.middle_frame)
        self.filters_frame_left.grid(row=0, column=0, padx=20, pady=10)
        self.filters_frame_right = tk.Frame(self.middle_frame)
        self.filters_frame_right.grid(row=0, column=2, padx=20, pady=10)
        # Tremolo
        self.trem_gui = TremoloGUI(self.filters_frame_left, output=self.output, 
                                                width=200, height=160, relief=tk.RAISED, borderwidth=2)
        self.trem_gui.pack(padx=10, pady=10)
        self.pass_filter_gui = PassFilterGUI(self.filters_frame_right, output=self.output, display_frame=self.display_frame,
                                                width=200, height=160, relief=tk.RAISED, borderwidth=2)
        self.pass_filter_gui.pack(padx=10, pady=10)
        self.pass_filter_gui.bind("<Button-1>", self.pass_filter_frame)
        
    def pass_filter_frame(self, *args):
        self.env_gui.pack_forget()
        self.config_frame.pack_forget()
        self.pass_filter_gui.plot_frame.pack(padx=10, pady=10, expand=True)

    def keyboard_frame(self):
        self.key_frame = tk.Frame(self.bottom_frame)
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
        
        try:
            self.controller.set_input_device(device_id)
            self.statusbar['text'] = f'Selected input device: {selection}'
        except Exception as e:
            self.controller.active = False
            if 'Host error' in str(e):
                self.statusbar['text'] = f'Midi device {selection} is busy...'

    def status_bar(self):
        self.statusbar = ttk.Label(self, text='Welcome to PySynth', relief=tk.SUNKEN, font='Times 10 italic')
        self.statusbar.pack(side=tk.BOTTOM, fill=tk.X)