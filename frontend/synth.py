import tkinter as tk
from tkinter import messagebox, ttk
import params
from output import Output
from midi import MidiController
from .oscillator import OscillatorGUI
from .tremolo import TremoloGUI


class SynthGUI(ttk.Frame):

    def __init__(self, master=None):
        super().__init__(master)
        self.first = True
        self.output = Output()
        self.init_protocols()
        self.generate_oscillators()
        self.generate_filters()
        self.generate_input()
        self.playback_frame()
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

        for _ in range(2):
            osc_nr = len(self.oscillators)
            osc_gui = OscillatorGUI(master_frame=self.oscframe, output=self.output, name=f'Oscillator {str(osc_nr + 1)}')
            osc_gui.pack(side=tk.LEFT, anchor=tk.N, padx=10, pady=10)
            self.oscillators.append(osc_gui)

        for osc in self.oscillators[:-1]:
            osc.FM_frame()
            ## TO DO
            # Implement multiple FM send
            #
            # if self.first:
            #     osc.FM_frame()
            #     self.first = False
        self.normalise_amplitudes(self.oscillators)

        self.oscframe.pack(side=tk.TOP, padx=10, pady=10)

    def normalise_amplitudes(self, oscillators):
        for o in oscillators:
            o.osc.amplitude = o.osc.amplitude / len(oscillators)

    def generate_input(self):
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

    def generate_filters(self):
        # Tremolo
        self.tremolo_frame = tk.Frame(self)
        self.tremolo_frame.pack(side=tk.TOP, padx=10, pady=10)
        self.trem_gui = TremoloGUI(self.tremolo_frame, output=self.output, title=f'Tremolo (AM modulation)')
        self.trem_gui.pack()

    def playback_frame(self):
        # Playback frame
        self.play_frame = tk.Frame(self.inputFrame)
        self.play_frame.grid(row=0, column=2, padx=20)
        # Play button
        self.play_btn = ttk.Button(self.play_frame, text="Play", command=self.play)
        self.play_btn.grid(row=0, column=2, padx=5, pady=10)
        # Stop button
        self.stop_btn = ttk.Button(self.play_frame, text="Stop", command=self.stop)
        self.stop_btn.grid(row=0, column=3, padx=5, pady=10)

    def select_input_device(self, *args):
        """
        Called upon change in the input_device menu.
        Get new input_device ID and sets the new input on the Midi controller interface.
        """
        selection = self.input_device.get()
        device_id = self.controller.get_input_devices()[selection]
        self.controller.set_input_device(device_id)
    
    def play(self):
        """
        Call play on audio interface.
        """
        self.output.play()

    def stop(self):
        """
        Call stop on audio interface.
        """
        self.output.stop()