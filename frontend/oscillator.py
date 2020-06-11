import tkinter as tk
import string
from tkinter import ttk
from pysynth.waveforms import SineWave, SquareWave
from pysynth.filters import FreqModulationFilter
from PIL import ImageTk, Image


class FmButton(tk.Frame):

    def __init__(self, master, gui, oscillator):
        super().__init__(master)
        self.master = master
        self.gui = gui
        self.output = gui.output
        self.oscillator = oscillator
        self.osc_input = tk.IntVar()
        self.to_option = tk.Checkbutton(self, text=str(oscillator),
                                        command=self.do_modulate, 
                                        variable=self.osc_input)
        self.to_option.grid(row=0, column=1)

    def do_modulate(self):
        """
        Callback function from Checkbutton object.
        Adds the given oscillator to the list of destination oscillators in the parent.
        """
        if self.osc_input.get():
            self.gui.osc.to_oscillators.append(self.oscillator)
        else:
            self.gui.osc.to_oscillators.remove(self.oscillator)
        self.gui.output.route_and_filter()


class OscillatorGUI(ttk.LabelFrame):
    """
    GUI unit for an oscillator panel.
    """
    def __init__(self, master_frame, output, number):
        super().__init__(master_frame)
        self.number = number
        self.name = f'Oscillator {string.ascii_uppercase[number]}'
        self.output = output
        self.osc = None        
        self.fm_frame = None
        self.UI()

    def UI(self):
        """
        Generate UI.
        """
        self.images = [
            r'static\oscillators\osA.png',  
            r'static\oscillators\osB.png',
            r'static\oscillators\osC.png',
            r'static\oscillators\osD.png'
            ]
            
        self.wave_frame = tk.Frame(self)
        self.wave_frame.pack(padx=10, pady=10)        
        self.image = Image.open(self.images[self.number]).convert('RGBA').resize((20,20))        
        self.wave_icon = ImageTk.PhotoImage(self.image)
        self.image_panel = tk.Label(self.wave_frame, image=self.wave_icon)
        self.image_panel.grid(row=0, column=0)
        self.image_panel.bind("<Button-1>", self.disable_osc)
        
        # Waveform choice
        self.waveforms = {
            "sine": SineWave,  
            "square": SquareWave
            # "triangle": None,
            # "sawtooth": None,
            # "noise": None
            }
        self.input_waveformtype = tk.StringVar()
        self.waveform = ttk.OptionMenu(self.wave_frame, self.input_waveformtype, 'sine', *self.waveforms.keys(), command=self.create_osc)
        self.waveform.grid(row=0, column=1)

        # Generate frequency frame
        self.ui_frame = tk.Frame(self)
        self.ui_frame.pack()
        self.set_freq_frame()
        self.amplitude_frame()

        # Create oscillator object on creation.
        # Defaults to sine.
        self.create_osc()

    def set_freq_frame(self):
        self.freq_frame = tk.Frame(self.ui_frame)
        self.fixed_var = tk.BooleanVar(value=0)
        self.freq_fixed = tk.Checkbutton(self.freq_frame, text="Fixed", variable=self.fixed_var, command=self.toggle_freq_ratio)
        self.freq_fixed.pack()
        self.input_freq_frame = tk.Frame(self.freq_frame)
        self.freq_label = tk.Label(self.input_freq_frame, text="Freq. (Hz)")
        self.freq_label.grid(row=1, column=0)
        self.frequency_var = tk.DoubleVar(value=440.0)
        self.input_freq = tk.Entry(self.input_freq_frame, width=10, textvariable=self.frequency_var)
        self.input_freq.grid(row=1, column=1, pady=10)
        self.input_freq.bind('<Return>', self.set_frequency)
        self.input_freq_frame.pack()
        self.ratio_frame = tk.Frame(self.freq_frame)
        self.ratio_label = tk.Label(self.ratio_frame, text="Freq. ratio")
        self.ratio_label.grid(row=0, column=0)
        self.ratio_var = tk.DoubleVar(value=1.0)
        self.input_ratio = tk.Entry(self.ratio_frame, width=10, textvariable=self.ratio_var)
        self.input_ratio.grid(row=0, column=1, pady=10)
        self.ratio_var.trace('w', self.set_frequency_ratio)
        self.toggle_freq_ratio()

    def set_frequency_ratio(self, *args):
        try:
            self.osc.frequency_ratio = float(self.input_ratio.get())
        except:
            pass

    def toggle_freq_ratio(self):
        """
        Callback method from fix frequency checkbutton.
        If frequency is fixed, entry widget is enabled and user can input frequency.
        Otherwise enty widget is disabled and user can input a ratio.
        """
        if self.fixed_var.get() == 0:
            self.input_freq_frame.pack_forget()
            if self.osc is not None: self.osc.fixed_frequency = False
            self.ratio_frame.pack()
        else:
            self.input_freq_frame.pack()
            self.set_frequency()
            if self.osc is not None: self.osc.fixed_frequency = True
            self.ratio_frame.pack_forget()

    def amplitude_frame(self):
        """
        Generate Amplitude frame
        """
        self.amp_frame = tk.Frame(self.ui_frame)
        self.amp_frame.pack()
        self.amplitude = tk.Scale(self.amp_frame, from_=0, to=1, orient=tk.HORIZONTAL, resolution=.02, command=self.set_amplitude)
        self.amplitude.set(0.5)
        self.amplitude.pack(pady=10)

    def freq_mod_frame(self):
        """
        Generate FM frame.
        """
        # FM frame
        self.fm_frame = tk.Frame(self.ui_frame)
        self.fm_frame.pack()
        self.fm_label = tk.Label(self.fm_frame, text="FM to : ", anchor='n')
        self.fm_label.pack(pady=10)

        # FM options frame        
        self.op_frame = tk.Frame(self.fm_frame)
        self.op_frame.pack()

        for oscillator in self.output.get_next_oscillators(self.osc):
            self.fm_button = FmButton(self.op_frame, self, oscillator)
            self.fm_button.pack()

    def create_osc(self, *args):
        """
        Instantiate oscillator after waveform type selection.
        """
        if self.osc is not None:
            del self.output.oscillators[self.number]
        self.waveform_choice = self.waveforms[self.input_waveformtype.get()]
        self.osc = self.waveform_choice(name=self.name)
        self.output.add_oscillator(self.osc, index=self.number)
        self.set_frequency()
        self.freq_frame.pack()

    def disable_osc(self, *args):
        if str(self.waveform["state"]) == "normal":
            self.ui_frame.pack_forget()
            bw_image = self.image.convert('L')
            self.wave_icon = ImageTk.PhotoImage(bw_image)
            self.image_panel.configure(image=self.wave_icon)
            self.waveform["state"] = "disabled"
            self.osc.disable()
        else:
            self.ui_frame.pack()
            self.wave_icon = ImageTk.PhotoImage(self.image)
            self.image_panel.configure(image=self.wave_icon)
            self.waveform["state"] = "normal"
            self.set_amplitude()
        self.output.route_and_filter()

    def set_frequency(self, *args):
        """
        Set frequency to input value.
        """
        if self.osc: self.osc.frequency= float(self.input_freq.get())

    def set_amplitude(self, *args):
        """
        Set amplitude to input value.
        """
        if self.osc: self.osc.amplitude= float(self.amplitude.get())