import tkinter as tk
from tkinter import ttk
from waveforms import SineWave

class OscillatorGUI(ttk.LabelFrame):
    """
    GUI unit for an oscillator panel.
    """
    def __init__(self, master_frame, output, title):
        super().__init__(master_frame, text=title)
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
        self.waveform.pack(padx=10, pady=10)
        
        # Set frequency
        self.freq_frame = tk.Frame(self)
        self.freq_label = tk.Label(self.freq_frame, text="Freq (Hz)")
        self.freq_label.grid(row=0, column=0)
        self.frequency = tk.IntVar(value=440)
        self.input_freq = tk.Entry(self.freq_frame, width=10, textvariable=self.frequency)
        self.input_freq.grid(row=0, column=1, pady=10)

        # Playback frame
        self.play_frame = tk.Frame(self)
        self.play_frame.pack()
        # Play button
        self.play_btn = ttk.Button(self.play_frame, text="Play", command=self.play)
        self.play_btn.grid(row=0, column=0, padx=5, pady=10)
        # Stop button
        self.stop_btn = ttk.Button(self.play_frame, text="Stop", command=self.stop)
        self.stop_btn.grid(row=0, column=1, padx=5, pady=10)

    def create_osc(self, *args):
        """
        Instantiate oscillator after waveform type selection.
        """
        osc = self.waveforms[self.input_waveformtype.get()]
        self.output.add_oscillator(osc())
        self.freq_frame.pack()

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
