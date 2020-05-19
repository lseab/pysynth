import tkinter as tk
from tkinter import ttk
from waveforms import SineWave, SquareWave
from filters import FreqModulationFilter

class FmGUI(tk.Frame):

    def __init__(self, master, output, osc_list):
        super().__init__(master)
        self.master = master
        self.output = output
        self.osc_list = osc_list
        self.fm_label = tk.Label(self, text="FM to : ")
        self.fm_label.grid(row=0, column=0)
        self.osc_input = tk.StringVar()
        self.oscillator_menu = ttk.OptionMenu(self, self.osc_input, 'None', 'None', *self.osc_list.keys(), command=self.do_modulate)        
        self.oscillator_menu.grid(row=0, column=1)
        self.pack()

    def do_modulate(self, o_input):      
        if self.master.osc:
            self.master.to_oscillator = []
            if o_input == 'None':
                pass
            elif self.osc_list[o_input] not in self.master.to_oscillator:
                self.master.to_oscillator.append(self.osc_list[o_input])
            self.output.play()


class OscillatorGUI(ttk.LabelFrame):
    """
    GUI unit for an oscillator panel.
    """
    def __init__(self, master_frame, output, name):
        super().__init__(master_frame, text=name)
        self.name = name
        self.output = output
        self.osc = None
        self.UI()
        self.osc_inputs = []
        self.to_oscillator = []

    def UI(self):
        """
        Generate UI.
        """
        # Waveform choice
        self.waveforms = {
            "sine": SineWave,  
            "square": SquareWave,
            "triangle": None,
            "sawtooth": None,
            "noise": None
            }
        self.input_waveformtype = tk.StringVar()
        self.waveform = ttk.OptionMenu(self, self.input_waveformtype, 'sine', *self.waveforms.keys(), command=self.create_osc)
        self.waveform.pack(padx=10, pady=10)
        
        # Set frequency
        self.freq_frame = tk.Frame(self)
        self.freq_label = tk.Label(self.freq_frame, text="Freq (Hz)")
        self.freq_label.grid(row=0, column=0)
        self.frequency = tk.IntVar(value=440)
        self.input_freq = tk.Entry(self.freq_frame, width=10, textvariable=self.frequency)
        self.input_freq.grid(row=0, column=1, pady=10)
        self.input_freq.bind('<Return>', self.set_frequency)

        # Create oscillator object on creation.
        # Defaults to sine.
        self.create_osc()

    def FM_frame(self):        
        oscillator_list = {str(o.osc): o for o in self.output.get_next_oscillators(self)}
        self.fm_frame = FmGUI(self, self.output, oscillator_list)
    # def FM_frame(self, num):
    #     self.fm_frame = tk.Frame(self)
    #     self.fm_frame.pack()
    #     self.fm_label = tk.Label(self.fm_frame, text="FM to : ")
    #     self.fm_label.grid(row=0, column=0)
    #     self.osc_inputs.append(tk.StringVar())
    #     self.oscillator_list = {str(o.osc): o for o in self.output.get_next_oscillators(self)}
    #     self.oscillator_menu = ttk.OptionMenu(self.fm_frame, self.osc_inputs[num], 'None', 'None', *self.oscillator_list.keys(), command=self.do_modulate(num))        
    #     self.oscillator_menu.grid(row=0, column=1)

    # def do_modulate(self, num, *args):
    #     print(self.osc_inputs[num].get())
    #     if self.osc:
    #         if self.osc_inputs[num].get() == 'None':
    #             self.to_oscillator = []
    #         else:
    #             print(self.osc_inputs[num].get())
    #             self.to_oscillator.append(self.oscillator_list[self.osc_inputs[num].gzt()])
    #         self.output.play()

    def create_osc(self, *args):
        """
        Instantiate oscillator after waveform type selection.
        """
        waveform = self.waveforms[self.input_waveformtype.get()]
        self.osc = waveform(name=self.name)
        self.output.add_oscillator(self)
        self.set_frequency()
        self.freq_frame.pack()

    def set_frequency(self, *args):
        """
        Set frequency to input value.
        """
        if self.osc: self.osc.frequency= int(self.input_freq.get())
