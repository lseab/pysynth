import tkinter as tk
from PIL import ImageTk, Image
from pysynth.output import Algorithms


class AlgorithmGUI(tk.Frame):

    def __init__(self, master):
        super().__init__(master)
        self.master = master
        self.algo_var = tk.StringVar(self, value='parallel')
        self.algo_var.trace("w", self.change_algorithm)
        self.algo_label = tk.Label(self, text="Algorithm:  ", font=('times', 15, 'bold'))
        self.algo_label.grid(row=0, column=0, padx=20)
        self.algo_buttons()

    def algo_buttons(self):
        # Stack Algorithm
        self.stack_image = ImageTk.PhotoImage(Image.open(r'static/algorithms/stack.png').convert('RGBA').resize((20,100)))
        self.stack = tk.Radiobutton(self, image=self.stack_image, value='stack', variable=self.algo_var)
        self.stack.grid(row=0, column=1, padx=20)
        # Parallel Algorithm
        self.para_image = ImageTk.PhotoImage(Image.open(r'static/algorithms/parallel.png').convert('RGBA').resize((90,22)))
        self.parallel = tk.Radiobutton(self, image=self.para_image, value='parallel', variable=self.algo_var)
        self.parallel.grid(row=0, column=2, padx=20)
        # Square Algorithm
        self.square_image = ImageTk.PhotoImage(Image.open(r'static/algorithms/square.png').convert('RGBA').resize((40,45)))
        self.square = tk.Radiobutton(self, image=self.square_image, value='square', variable=self.algo_var)
        self.square.grid(row=0, column=3, padx=20)
        # 3 to 1 algorithm
        self.three_image = ImageTk.PhotoImage(Image.open(r'static/algorithms/3to1.png').convert('RGBA').resize((70,55)))
        self.three = tk.Radiobutton(self, image=self.three_image, value='3to1', variable=self.algo_var)
        self.three.grid(row=0, column=4, padx=20)
        # Custom Algorithm
        self.custom = tk.Radiobutton(self, text='custom', value='custom', variable=self.algo_var)
        self.custom.grid(row=0, column=5, padx=20)

    def change_algorithm(self, *args):
        if self.algo_var.get() == 'custom':
            for o in self.master.oscillators[:-1]:
                if o.fm_frame is None: o.FM_frame()
            self.master.output.choose_algorithm("parallel")
        else:
            for o in self.master.oscillators[:-1]:
                try: 
                    o.fm_frame.destroy()
                    o.fm_frame = None
                except: pass
            self.master.output.choose_algorithm(self.algo_var.get())