import tkinter as tk
from tkinter import ttk
import numpy as np
from pysynth.waveforms import SineWave, SquareWave
from pysynth.filters import PassFilter
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure


class TremoloGUI(tk.LabelFrame):

    def __init__(self, master, output, **kwargs):
        super().__init__(master, text=f'Tremolo (AM modulation)', **kwargs)
        self.output = output
        self.pack_propagate(False)
        self.UI()

    def UI(self):
        # Waveform choice
        self.waveforms = {
            "sine": SineWave,  
            "square": SquareWave,
            # "triangle": None,
            # "sawtooth": None,
            # "noise": None
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
        self.output.set_am_modulator(waveform())
        self.set_frequency()

    def set_frequency(self, *args):
        if self.output.am_modulator:
            freq = self.frequency.get()
            self.output.am_modulator.frequency = freq

    def set_sensitivity(self, *args):
        if self.output.am_modulator:
            sens = self.sensitivity.get()
            self.output.am_modulator.amplitude = sens


class PassFilterGUI(tk.LabelFrame):

    def __init__(self, master, output, display_frame, **kwargs):
        super().__init__(master, text=f'Filter', **kwargs)
        self.output = output
        self.display_frame = display_frame
        self.pack_propagate(False)
        self.controls()
        self.filter_plot()

    def controls(self):
        # Control frame
        self.control_frame = tk.Frame(self)
        self.control_frame.pack(pady=5)
        # Filter type
        filter_types = ["lowpass", "highpass"]
        self.input_filter_type = tk.StringVar()
        self.filter_type = ttk.OptionMenu(self.control_frame, self.input_filter_type, 'lowpass', *filter_types, command=self.set_filter_type)
        self.filter_type.grid(row=0, column=1)
        # Cutoff slider
        self.cutoff_label = tk.Label(self.control_frame, text='Freq.')
        self.cutoff_label.grid(row=1, column=0)
        self.cutoff = tk.Scale(self.control_frame, from_=30, to=18000, orient=tk.HORIZONTAL, resolution=10, command=self.set_cutoff)
        self.cutoff.set(18000)
        self.cutoff.grid(row=1, column=1, pady=20)

    def set_cutoff(self, *args):
        cutoff = self.cutoff.get()
        self.output.filter_cutoff = cutoff
        self.replot()

    def set_filter_type(self, *args):
        filter_type = self.input_filter_type.get()
        self.output.filter_type = filter_type
        self.replot()

    def filter_plot(self):
        fig = Figure(figsize=(3.2,2.4))
        fig.patch.set_facecolor('silver')
        self.plot_frame = tk.Frame(self.display_frame, width=600, height=300)
        self.plot_frame.place(in_=self.display_frame, anchor="c", relx=.5, rely=.5)
        self.plot_frame.pack_propagate(False)
        self.plot_frame.pack(expand=True)
        self.plot = fig.subplots()
        self.plot.set_facecolor('skyblue')
        self.plot.yaxis.set_visible(False)
        self.draw()
        self.canvas = FigureCanvasTkAgg(fig, master=self.plot_frame)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(side='top', fill='both', expand=1)
        self.pack()

    def draw(self):
        cutoff = self.output.filter_cutoff
        filter_type = self.output.filter_type
        w, h = PassFilter.frequency_response(cutoff, filter_type)
        self.plot.plot(w, np.abs(h), 'b')
        self.plot.axvline(cutoff, color='k')

    def replot(self):
        self.plot.cla()
        self.draw()
        self.canvas.draw()