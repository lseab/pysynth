import tkinter as tk
import matplotlib.pyplot as plt
import numpy as np
from math import log10
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from pysynth.waveforms import SineWave
from pysynth.filters import Envelope
from pysynth.params import blocksize


class EnvelopeGUI(tk.Frame):

    def __init__(self, master, oscillator, **kwargs):
        super().__init__(master=master, **kwargs)
        self.oscillator = oscillator
        self.get_envelope_values()
        self.amplitude = 0.0
        self.time = 0.0
        self.envelopeFrame()
        self.value_sliders()

    def get_envelope_values(self):        
        self.framerate = self.oscillator.framerate
        self.max_amp = self.oscillator.amplitude
        self.attack_time = self.oscillator.envelope['attack']
        self.a_target = self.oscillator.envelope['a_target']
        self.decay_time = self.oscillator.envelope['decay']
        self.dr_target = self.oscillator.envelope['dr_target']
        self.sustain_fraction = self.oscillator.envelope['sustain']
        self.sustain_level = self.sustain_fraction * self.max_amp
        self.release_time = self.oscillator.envelope['release']

    def get_rate(self, target, rate, base):
        return (1.0 / (rate * self.framerate)) * np.log(target / base)

    def envelopeFrame(self):
        fig = Figure(figsize=(3.2,2.4))
        fig.patch.set_facecolor('silver')
        self.env_frame = tk.Frame(self, width=500, height=200)
        self.env_frame.pack_propagate(False)
        self.env_frame.pack()
        self.plot = fig.subplots()
        self.plot.set_facecolor('skyblue')
        self.plot.yaxis.set_visible(False)
        self.draw()
        self.canvas = FigureCanvasTkAgg(fig, master=self.env_frame)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(side='top', fill='both', expand=1)
        self.pack()

    def attack(self):
        attack_coef = self.get_rate(self.a_target, self.attack_time, self.max_amp + self.a_target)
        self.time = self.attack_time
        x = np.linspace(0, self.time * self.framerate, num=20)
        amps = []
        for n, i in enumerate(x):
            if n == 0: self.amplitude = (self.max_amp + self.a_target) * (1 - np.exp(attack_coef)) + self.amplitude * np.exp(attack_coef)
            else:
                self.amplitude = (self.max_amp + self.a_target) * (1 - np.exp(attack_coef * (i - x[n-1]))) + self.amplitude * np.exp(attack_coef * (i - x[n-1]))      
            amps.append(self.amplitude)
        return (x, amps)

    def decay(self):
        decay_coef = self.get_rate(self.dr_target, self.decay_time, self.max_amp - self.sustain_level + self.dr_target)
        x = np.linspace(self.time * self.framerate, (self.time + self.decay_time) * self.framerate, num=20)
        self.time = (self.time + self.decay_time)
        amps = []
        for n, i in enumerate(x):
            if n == 0: self.amplitude = (self.sustain_level - self.dr_target) * (1 - np.exp(decay_coef)) + self.amplitude * np.exp(decay_coef)
            else:
                self.amplitude = (self.sustain_level - self.dr_target)  * (1 - np.exp(decay_coef * (i - x[n-1]))) + self.amplitude * np.exp(decay_coef * (i - x[n-1]))      
            amps.append(self.amplitude)
        return (x, amps)

    def sustain(self):        
        x = np.linspace(self.time, self.time + 2.0, num=20)
        self.time = self.time + 2.0
        amps = [self.sustain_level for _ in x]
        return (x, amps)

    def release(self):
        release_coef = self.get_rate(self.dr_target, self.release_time, self.sustain_level + self.dr_target)
        x = np.linspace(self.time * self.framerate, (self.time + self.release_time) * self.framerate, num=20)
        amps = []
        for n, i in enumerate(x):
            if n == 0: self.amplitude = - self.dr_target * (1 - np.exp(release_coef)) + self.amplitude * np.exp(release_coef)
            else:
                self.amplitude = - self.dr_target * (1 - np.exp(release_coef * (i - x[n-1]))) + self.amplitude * np.exp(release_coef * (i - x[n-1]))      
            amps.append(self.amplitude)
        return (x, amps)

    def draw(self):
        if self.attack_time == 0:
            self.amplitude = self.max_amp
            self.time = 0.0
            self.plot.plot((0.0, 0.0), (0.0, self.max_amp), 'r')
        else:
            attack = self.attack()
            self.plot.plot(attack[0] / self.framerate, attack[1], 'r')

        if self.decay_time == 0:
            self.amplitude = self.sustain_level
            self.time = self.attack_time
            self.plot.plot((self.attack_time, self.attack_time), (self.sustain_level, self.max_amp), 'r')
        else:
            decay = self.decay()
            self.plot.plot(decay[0] / self.framerate, decay[1], 'r')

        sustain = self.sustain()
        self.plot.plot(sustain[0], sustain[1], 'r')
        
        if self.release_time == 0:
            self.amplitude = 0.0
            self.time = self.attack_time + self.decay_time + 2.0
            self.plot.plot((self.time, self.time), (0.0, self.sustain_level), 'r')
        else:
            release = self.release()
            self.plot.plot(release[0] / self.framerate, release[1], 'r')

    def value_sliders(self):
        self.sliders_frame = tk.Frame(self)
        self.sliders_frame.pack(pady=10)

        self.adsr_frame = tk.Frame(self.sliders_frame, pady=10)
        self.adsr_frame.pack()
        ## ATTACK
        self.a_frame = tk.Frame(self.adsr_frame)
        self.a_frame.grid(row=0, column=0, padx=5)
        self.a_label = tk.Label(self.a_frame, text="Attack")
        self.a_label.pack()
        self.a_time = tk.Scale(self.a_frame, from_=0.00001, to=5, orient=tk.HORIZONTAL, resolution=.02, command=self.change_attack_time)
        self.a_time.set(self.attack_time)
        self.a_time.pack()
        ## DECAY
        self.d_frame = tk.Frame(self.adsr_frame)
        self.d_frame.grid(row=0, column=1, padx=5)
        self.d_label = tk.Label(self.d_frame, text="Decay")
        self.d_label.pack()
        self.d_time = tk.Scale(self.d_frame, from_=0, to=5, orient=tk.HORIZONTAL, resolution=.02, command=self.change_decay_time)
        self.d_time.set(self.decay_time)
        self.d_time.pack()
        ## RELEASE
        self.r_frame = tk.Frame(self.adsr_frame)
        self.r_frame.grid(row=0, column=2, padx=5)
        self.r_label = tk.Label(self.r_frame, text="Release")
        self.r_label.pack()
        self.r_time = tk.Scale(self.r_frame, from_=0.05, to=5, orient=tk.HORIZONTAL, resolution=.02, command=self.change_release_time)
        self.r_time.set(self.release_time)
        self.r_time.pack()        
        ## SUSTAIN
        self.s_frame = tk.Frame(self.adsr_frame)
        self.s_frame.grid(row=0, column=3, padx=5)
        self.s_label = tk.Label(self.s_frame, text="Sustain")
        self.s_label.pack()
        self.s_level = tk.Scale(self.s_frame, from_=0, to=1, orient=tk.HORIZONTAL, resolution=0.05, command=self.change_sustain)
        self.s_level.set(self.sustain_fraction)
        self.s_level.pack()
        
        self.shape_frame = tk.Frame(self.sliders_frame, pady=10)
        self.shape_frame.pack()
        ## ATTACK SHAPE
        self.shape_frame = tk.Frame(self.sliders_frame, pady=10)
        self.shape_frame.pack()
        self.a_shape_frame = tk.Frame(self.shape_frame)
        self.a_shape_frame.grid(row=0, column=0, padx=5)
        self.a_shape_label = tk.Label(self.a_shape_frame, text="Attack Shape")
        self.a_shape_label.pack()
        self.a_shape = tk.Scale(self.a_shape_frame, from_=0, to=6, orient=tk.HORIZONTAL, resolution=0.1, command=self.change_a_target, showvalue=0)
        self.a_shape.set(-log10(self.a_target))
        self.a_shape.pack()
        ## DECAY/RELEASE SHAPE
        self.dr_shape_frame = tk.Frame(self.shape_frame)
        self.dr_shape_frame.grid(row=0, column=1, padx=5)
        self.dr_shape_label = tk.Label(self.dr_shape_frame, text="Decay/Release Shape")
        self.dr_shape_label.pack()
        self.dr_shape = tk.Scale(self.dr_shape_frame, from_=0, to=6, orient=tk.HORIZONTAL, resolution=0.1, command=self.change_dr_target, showvalue=0)
        self.dr_shape.set(-log10(self.dr_target))
        self.dr_shape.pack()

    def change_attack_time(self, *args):
        attack_time = self.a_time.get()
        self.attack_time = attack_time
        self.oscillator.envelope['attack'] = attack_time
        self.replot()

    def change_decay_time(self, *args):
        decay_time = self.d_time.get()
        self.decay_time = decay_time
        self.oscillator.envelope['decay'] = decay_time
        self.replot()

    def change_release_time(self, *args):
        release_time = self.r_time.get()
        self.release_time = release_time
        self.oscillator.envelope['release'] = release_time
        if release_time < 0.1: self.dr_shape.set(6)
        self.replot()

    def change_sustain(self, *args):
        sustain = self.s_level.get()
        self.sustain_level = sustain * self.max_amp
        self.oscillator.envelope['sustain'] = sustain
        self.replot()

    def change_a_target(self, *args):
        a_target = 10 ** (-self.a_shape.get())
        self.a_target = a_target
        self.oscillator.envelope['a_target'] = a_target
        self.replot()

    def change_dr_target(self, *args):
        dr_target = 10 ** (-self.dr_shape.get())
        self.dr_target = dr_target
        self.oscillator.envelope['dr_target'] = dr_target
        self.replot()

    def replot(self):
        self.plot.cla()
        self.draw()
        self.canvas.draw()

    def update_envelope(self, oscillator, number):
        colours = ['skyblue', 'firebrick', 'xkcd:mint green', 'orange']
        self.oscillator = oscillator
        self.get_envelope_values()
        self.a_time.set(self.attack_time)
        self.d_time.set(self.decay_time)
        self.r_time.set(self.release_time)
        self.s_level.set(self.sustain_fraction)
        self.a_shape.set(-log10(self.a_target))
        self.dr_shape.set(-log10(self.dr_target))
        self.plot.set_facecolor(colours[number])
        self.replot()