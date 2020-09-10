import tkinter as tk
from PIL import ImageTk, Image
from tkinter import messagebox, ttk
from os.path import join
import pysynth.params
from pysynth.output import Output
from pysynth.filters import ADSREnvelope
from pysynth.waveforms import SineWave
from pysynth.midi import MidiController
from .oscillator import OscillatorGUI
from .filters import TremoloGUI, PassFilterGUI
from .keyboard import KeyboardGUI
from .algos import AlgorithmGUI
from .envelope import EnvelopeGUI
from .gui_helpers import ScrollFrame


class SynthGUI(tk.Tk):
    """
    Root Tkinter application.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.first = True
        self.output = Output()
        self.init_protocols()
        self.main_frames()
        self.status_bar()
        self.selected_algorithm_frame()
        self.oscillator_frame()
        self.save_frame()
        self.display_frame()
        self.configuration_frame()
        self.envelope_frame()
        self.filters_frame()
        self.keyboard_frame()
        self.input_frame()

    def init_protocols(self):
        """
        Call self.on_closing when the gui window is closed.
        """
        self.protocol("WM_DELETE_WINDOW", self.on_closing)

    def on_closing(self):
        """
        Closing message box.
        """
        if messagebox.askokcancel("Quit", "Are you sure you want to quit?"):
            self.controller.close_controller()
            MidiController.exit()
            self.destroy()

    def main_frames(self):
        """
        Create and pack top level frames with full screen scrollbar for redimensioning.
        """
        self.scroll_frame = ScrollFrame(self)
        self.scroll_frame.pack()
        self.main_frame = tk.Frame(self.scroll_frame.scrollwindow)
        self.main_frame.pack()
        self.oscframe = tk.Frame(self.main_frame)
        self.oscframe.pack()
        self.disframe = tk.Frame(self.main_frame)
        self.disframe.pack()
        self.keyframe = tk.Frame(self.main_frame)
        self.keyframe.pack()
        self.inputFrame = tk.Frame(self.main_frame)
        self.inputFrame.pack()
        self.saveFrame = tk.Frame(self.main_frame)
        self.saveFrame.pack()

    def status_bar(self):
        """
        Add a status bar at the bottom.
        """
        self.statusbar = ttk.Label(self, text='Welcome to PySynth', relief=tk.SUNKEN, font='Times 10 italic')
        self.statusbar.pack(side=tk.BOTTOM, fill=tk.X)

    def selected_algorithm_frame(self):
        """
        FM algorithm selection icon.
        """
        self.selected_algo_frame = tk.Frame(self.oscframe, width=100, height=100)
        self.selected_algo_frame.pack(side=tk.LEFT, anchor=tk.N, padx=5, pady=50)
        self.selected_algo_frame.pack_propagate(False)
        self.selected_algo_frame.bind("<Button-1>", self.show_config)

    def oscillator_frame(self):
        """
        Create oscillator frames.
        """
        self.oscillators = []

        for _ in range(4):
            osc_nr = len(self.oscillators)
            osc_gui = OscillatorGUI(master_frame=self.oscframe, gui=self, output=self.output, number=osc_nr)
            osc_gui.pack(side=tk.LEFT, anchor=tk.N, padx=30, pady=5)
            self.oscillators.append(osc_gui)
    
    def save_frame(self):
        """
        Midi input gui.
        """
        ## Record Button
        self.record_image = ImageTk.PhotoImage(Image.open(join('images', 'buttons', 'record.png')).resize((30,30)))
        self.record = tk.Button(self.oscframe, command=self._record, image=self.record_image, border=0, highlightbackground="#d9d9d9")
        self.record.config(activebackground=self.record.cget('background'))
        self.record.pack(pady=10, padx=50)
        ## Save Button
        self.save_image = ImageTk.PhotoImage(Image.open(join('images', 'buttons', 'recording.png')).resize((30,30)))
        self.save = tk.Button(self.oscframe, command=self._save, image=self.save_image, border=0, highlightbackground="#d9d9d9")
        self.save.config(activebackground=self.save.cget('background'))

    def display_frame(self):
        """
        Central frame which displays different config frames on click (ADSR, Filter..).
        """
        self.display_frame = tk.Frame(self.disframe, relief=tk.RAISED, borderwidth=2, 
                                        highlightbackground="light sky blue", highlightcolor="light sky blue", highlightthickness=20, 
                                        height=450, width=550)
        self.display_frame.grid(row=0, column=1, pady=20)
        self.display_frame.pack_propagate(False)

    def configuration_frame(self):
        """
        Central diplay: algorithm selection, voice number selection. 
        """
        self.config_frame = tk.Frame(self.display_frame)
        self.algo_frame = AlgorithmGUI(self.config_frame, self)
        self.algo_frame.pack(padx=10, pady=20)
        self.change_algorithm_image()
        self.voicesframe = tk.Frame(self.config_frame)
        self.voicesframe.pack(padx=10, pady=20)
        self.voicesLabel = tk.Label(self.voicesframe, text="Voices : ")
        self.voicesLabel.grid(row=0, column=0)
        self.input_num_voices = tk.IntVar(value=self.output.max_voices)
        self.num_voices = ttk.OptionMenu(self.voicesframe, self.input_num_voices, *[i for i in range(15)], command=self.set_voices)
        self.num_voices.grid(row=0, column=1)

    def envelope_frame(self):
        """
        ADSR envelope display.
        """
        self.oscillators[0]['bg'] = 'SkyBlue1'
        self.env_gui = EnvelopeGUI(self.display_frame, self.oscillators[0].osc, padx=20, pady=20)

    def filters_frame(self):
        """
        Filters frames on either side of the display.
        """
        self.filters_frame_left = tk.Frame(self.disframe)
        self.filters_frame_left.grid(row=0, column=0, padx=20, pady=10)
        self.filters_frame_right = tk.Frame(self.disframe)
        self.filters_frame_right.grid(row=0, column=2, padx=20, pady=10)
        # Tremolo
        self.trem_gui = TremoloGUI(self.filters_frame_left, output=self.output, 
                                                width=200, height=160, relief=tk.RAISED, borderwidth=2)
        self.trem_gui.pack(padx=10, pady=10)
        # Pass filter
        self.pass_filter_gui = PassFilterGUI(self.filters_frame_right, output=self.output, display_frame=self.display_frame,
                                                width=200, height=160, relief=tk.RAISED, borderwidth=2)
        self.pass_filter_gui.pack(padx=10, pady=10)
        self.pass_filter_gui.bind("<Button-1>", self.show_pass_filter)
        self.pass_filter_gui.cutoff.slide.bind("<Button-1>", self.show_pass_filter)
        self.pass_filter_gui.plot_frame.pack_forget()

    def keyboard_frame(self):
        """
        Keyboard frame.
        """
        self.keyboard = KeyboardGUI(self.keyframe, self.output)
        self.keyboard.pack()

    def input_frame(self):
        """
        Midi input gui.
        """
        ## Input Frame
        self.controller = MidiController(self.output)
        self.inputLabel = tk.Label(self.inputFrame, text="Input device : ")
        self.inputLabel.grid(row=0, column=0, pady=10)
        self.input_device = tk.StringVar()
        self.input = ttk.OptionMenu(self.inputFrame, self.input_device, 'None', *self.controller.get_input_devices().keys())
        # callback only triggered on config change
        self.input.bind("<Configure>", self.select_input_device)
        self.input.grid(row=0, column=1, pady=10)

    def _save(self):
        self.output.save_to_wav()
        self.save.pack_forget()
        self.record.pack(pady=10, padx=50)

    def _record(self):
        self.output.record_to_wav()
        self.record.pack_forget()
        self.save.pack(pady=10, padx=50)

    def change_algorithm_image(self):
        """
        Displays the selected algorithm image and binds a display click event.
        """
        selected_algo = self.algo_frame.algo_var.get()
        if selected_algo == "stack": self.algo_image = self.algo_frame.stack_image        
        elif selected_algo == "parallel": self.algo_image = self.algo_frame.para_image        
        elif selected_algo == "square": self.algo_image = self.algo_frame.square_image
        elif selected_algo == "3to1": self.algo_image = self.algo_frame.three_image
        elif selected_algo == "custom": self.algo_image = self.algo_frame.custom_image
        try: 
            self.algo_label.destroy()
        except: pass
        self.algo_label = tk.Label(self.selected_algo_frame, image=self.algo_image)
        self.algo_label.bind("<Button-1>", self.show_config)
        self.algo_label.pack()

    def show_config(self, *args):
        """
        Open configuration display.
        """
        self.env_gui.pack_forget()
        self.pass_filter_gui.plot_frame.pack_forget()
        self.config_frame.pack(expand=True, padx=10, pady=10)

    def show_envelope(self, oscillator, number):
        """
        Open ADSR display for a given oscillator.
        """
        self.config_frame.pack_forget()
        self.pass_filter_gui.plot_frame.pack_forget()
        self.env_gui.pack()
        self.env_gui.update_envelope(oscillator, number)

    def set_voices(self, *args):
        """
        Change max number of voices (simultaneous notes).
        """
        self.output.max_voices = self.input_num_voices.get()
        
    def show_pass_filter(self, *args):
        """
        Display pass filter.
        """
        self.env_gui.pack_forget()
        self.config_frame.pack_forget()
        self.pass_filter_gui.plot_frame.pack(padx=10, pady=10, expand=True)

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